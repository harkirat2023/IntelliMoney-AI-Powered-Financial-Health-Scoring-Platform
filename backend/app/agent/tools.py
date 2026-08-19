"""Typed, user-scoped financial tools for the LangChain agent.

Every tool receives the authenticated user context through a closure
(``db`` + ``user_id``). Tools never trust client/user-provided IDs for
authorization: all queries are constrained to the authenticated user.

Read/calculation tools execute immediately. The single write-planning tool
(``propose_actions``) only validates and stores a plan for later explicit
user confirmation. No tool performs a direct database mutation.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from langchain_core.tools import tool
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.schemas import (
    DESTRUCTIVE_KINDS,
    ActionKind,
    ProposedAction,
    Proposal,
    ProposalStatus,
    validate_params,
)
from app.core.constants import CATEGORIES
from app.services.category_service import suggest_category
from app.services.serializers import date_to_datetime, serialize_document
from app.utils.date_utils import month_bounds, utc_now
from app.utils.object_id import to_object_id

CATEGORIES_JOINED = ", ".join(CATEGORIES)


def _clean(docs: list[dict] | dict) -> Any:
    if isinstance(docs, list):
        return [_clean(d) for d in docs]
    return serialize_document(docs)


def _json(data: Any) -> str:
    return json.dumps(data, default=str, indent=2)


# ---------------------------------------------------------------------------
# Args schemas (strongly typed; the LLM cannot bypass validation)
# ---------------------------------------------------------------------------


class EmptyArgs(BaseModel):
    pass


class TextArgs(BaseModel):
    query: str = Field(..., description="Search term (merchant, description or category)")


class PeriodArgs(BaseModel):
    period: str | None = Field(
        default=None, description="YYYY-MM period. Leave empty for the current month."
    )


class DateRangeArgs(BaseModel):
    from_date: str = Field(..., description="YYYY-MM-DD start date (inclusive)")
    to_date: str = Field(..., description="YYYY-MM-DD end date (inclusive)")


class CategoryArgs(BaseModel):
    category: str = Field(..., description=f"Category. One of: {CATEGORIES_JOINED}")


class CategoryPeriodArgs(BaseModel):
    category: str = Field(..., description=f"Category. One of: {CATEGORIES_JOINED}")
    period: str | None = Field(default=None, description="YYYY-MM period")


class BudgetArgs(BaseModel):
    budget_id: str = Field(..., description="Budget id")


class ExpenseIdArgs(BaseModel):
    expense_id: str = Field(..., description="Expense id")


class GoalArgs(BaseModel):
    goal_id: str = Field(..., description="Goal id")


class RecurringArgs(BaseModel):
    recurring_id: str = Field(..., description="Recurring expense id")


class SubscriptionArgs(BaseModel):
    subscription_id: str = Field(..., description="Subscription id")


class NotificationArgs(BaseModel):
    notification_id: str = Field(..., description="Notification id")


class AccountArgs(BaseModel):
    account_id: str = Field(..., description="Bank account id")


class AaDataSessionArgs(BaseModel):
    data_session_id: str = Field(..., description="AA data session id")


class CalculateRemainingArgs(BaseModel):
    income: float = Field(..., gt=0, description="Confirmed monthly income")
    committed: list[float] = Field(
        default_factory=list, description="Confirmed committed amounts (expenses/budgets)"
    )


class CategorizeArgs(BaseModel):
    description: str = Field(..., min_length=1, description="Transaction description")


class ProposeActionsArgs(BaseModel):
    actions: list[dict[str, Any]] = Field(
        ...,
        description=(
            "List of proposed actions. Each action must have: kind (one of "
            + ", ".join(a.value for a in ActionKind)
            + "), summary (short human description), params (object with the "
            "relevant fields), and destructive (bool, true for deletions)."
        ),
    )


# ---------------------------------------------------------------------------
# Tool factory
# ---------------------------------------------------------------------------


def build_tools(db: AsyncIOMotorDatabase, user_id: str, session_id: str = ""):
    """Build the user-scoped tool list for the LangChain agent."""

    proposal_created: list[Proposal] = []

    # ---- helpers ----------------------------------------------------------
    async def _income_doc() -> dict | None:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return user or {}

    async def _month_expenses(period: str | None) -> tuple[datetime, datetime]:
        if period:
            try:
                year, month = (int(x) for x in period.split("-"))
                return month_bounds(year, month)
            except (ValueError, TypeError):
                pass
        now = utc_now()
        return month_bounds(now.year, now.month)

    async def _expenses_in_range(start: datetime, end: datetime) -> list[dict]:
        cursor = db.expenses.find(
            {"user_id": ObjectId(user_id), "date": {"$gte": start, "$lte": end}}
        ).sort("date", -1)
        return await cursor.to_list(length=None)

    # ---- read tools -------------------------------------------------------
    @tool(args_schema=EmptyArgs)
    async def get_income(_: EmptyArgs = EmptyArgs()) -> str:
        """Get the user's confirmed monthly income and recent income history. Use for income questions."""
        user = await _income_doc()
        history = await db.income_history.find(
            {"user_id": ObjectId(user_id)}
        ).sort("month", -1).limit(12).to_list(length=12)
        return _json({
            "monthly_income": user.get("monthly_income", 0) if user else 0,
            "income_history": _clean(history),
        })

    @tool(args_schema=PeriodArgs)
    async def get_expenses(period: str | None = None) -> str:
        """Get expenses for a YYYY-MM period (default: current month). Use for spending questions."""
        start, end = await _month_expenses(period)
        docs = await _expenses_in_range(start, end)
        if not docs:
            return "No expenses found for this period."
        return _json(_clean(docs))

    @tool(args_schema=ExpenseIdArgs)
    async def get_expense_by_id(expense_id: str) -> str:
        """Get a single expense by its id."""
        try:
            oid = to_object_id(expense_id)
        except ValueError:
            return "Invalid expense id."
        doc = await db.expenses.find_one({"_id": oid, "user_id": ObjectId(user_id)})
        if not doc:
            return "Expense not found."
        return _json(_clean(doc))

    @tool(args_schema=TextArgs)
    async def search_expenses(query: str) -> str:
        """Search expenses by description or category keyword."""
        regex = {"$regex": query, "$options": "i"}
        cursor = db.expenses.find({
            "user_id": ObjectId(user_id),
            "$or": [{"description": regex}, {"category": regex}],
        }).sort("date", -1).limit(20)
        docs = await cursor.to_list(length=20)
        if not docs:
            return f"No expenses found matching '{query}'."
        return _json(_clean(docs))

    @tool(args_schema=PeriodArgs)
    async def summarize_spending(period: str | None = None) -> str:
        """Summarize total spending, transaction count, top category and average for a period."""
        start, end = await _month_expenses(period)
        docs = await _expenses_in_range(start, end)
        total = round(sum(d.get("amount", 0) for d in docs), 2)
        by_category: dict[str, float] = {}
        for d in docs:
            by_category[d.get("category", "Other")] = by_category.get(d.get("category", "Other"), 0) + d.get("amount", 0)
        top = max(by_category.items(), key=lambda kv: kv[1]) if by_category else ("N/A", 0)
        return _json({
            "period": period or "current-month",
            "total_spending": total,
            "expense_count": len(docs),
            "average_per_transaction": round(total / len(docs), 2) if docs else 0,
            "top_category": top[0],
            "top_category_amount": round(top[1], 2),
            "spending_by_category": [
                {"category": c, "amount": round(a, 2)}
                for c, a in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)
            ],
        })

    @tool(args_schema=CategoryPeriodArgs)
    async def get_spending_by_category(category: str, period: str | None = None) -> str:
        """Get spending for a specific category in a period (default: current month)."""
        start, end = await _month_expenses(period)
        docs = await _expenses_in_range(start, end)
        matching = [d for d in docs if d.get("category", "Other") == category]
        total = round(sum(d.get("amount", 0) for d in matching), 2)
        return _json({
            "category": category,
            "period": period or "current-month",
            "total": total,
            "expense_count": len(matching),
        })

    @tool(args_schema=DateRangeArgs)
    async def get_spending_by_date_range(from_date: str, to_date: str) -> str:
        """Get total spending between two dates (YYYY-MM-DD)."""
        try:
            start = date_to_datetime(from_date)
            end = date_to_datetime(to_date) + timedelta(days=1)
        except Exception:
            return "Invalid dates. Use YYYY-MM-DD format."
        docs = await _expenses_in_range(start, end)
        total = round(sum(d.get("amount", 0) for d in docs), 2)
        return _json({
            "from_date": from_date, "to_date": to_date,
            "total_spending": total, "expense_count": len(docs),
        })

    @tool(args_schema=EmptyArgs)
    async def list_budgets(_: EmptyArgs = EmptyArgs()) -> str:
        """List the user's budgets for all months. Use for budget questions."""
        cursor = db.budgets.find({"user_id": ObjectId(user_id)}).sort([("year", -1), ("month", -1)])
        docs = await cursor.to_list(length=None)
        if not docs:
            return "No budgets found."
        return _json(_clean(docs))

    async def _budget_status_period(period: str | None) -> list[dict]:
        from app.services.analytics_service import get_month_expenses
        now = utc_now()
        if period:
            try:
                year, month = (int(x) for x in period.split("-"))
            except ValueError:
                year, month = now.year, now.month
        else:
            year, month = now.year, now.month
        budgets = [
            serialize_document(item)
            async for item in db.budgets.find(
                {"user_id": ObjectId(user_id), "month": month, "year": year}
            )
        ]
        expenses = await get_month_expenses(db, user_id, year, month)
        spent_by_category: dict[str, float] = {}
        for expense in expenses:
            spent_by_category[expense["category"]] = (
                spent_by_category.get(expense["category"], 0) + expense["amount"]
            )
        statuses = []
        for budget in budgets:
            spent = round(spent_by_category.get(budget["category"], 0), 2)
            limit = float(budget["limit"])
            percentage = round((spent / limit) * 100, 2) if limit else 0
            state = "over" if percentage >= 100 else ("warning" if percentage >= 80 else "safe")
            statuses.append({
                "id": budget["id"],
                "category": budget["category"],
                "limit": limit,
                "spent": spent,
                "remaining": round(limit - spent, 2),
                "percentage_used": percentage,
                "state": state,
            })
        return statuses

    @tool(args_schema=BudgetArgs)
    async def get_budget(budget_id: str) -> str:
        """Get a single budget by id."""
        try:
            oid = to_object_id(budget_id)
        except ValueError:
            return "Invalid budget id."
        doc = await db.budgets.find_one({"_id": oid, "user_id": ObjectId(user_id)})
        if not doc:
            return "Budget not found."
        return _json(_clean(doc))

    @tool(args_schema=PeriodArgs)
    async def get_budget_usage(period: str | None = None) -> str:
        """Get budget usage (spent vs limit, percentage, state) for a period. Use for overspending questions."""
        statuses = await _budget_status_period(period)
        return _json(statuses)

    @tool(args_schema=PeriodArgs)
    async def get_remaining_budget(period: str | None = None) -> str:
        """Get remaining budget amounts per category for a period."""
        statuses = await _budget_status_period(period)
        result = [
            {
                "category": s["category"],
                "limit": s["limit"],
                "spent": s["spent"],
                "remaining": round(s["limit"] - s["spent"], 2),
                "percentage_used": s["percentage_used"],
                "state": s["state"],
            }
            for s in statuses
        ]
        return _json(result)

    @tool(args_schema=PeriodArgs)
    async def compare_budget_actual(period: str | None = None) -> str:
        """Compare budget limits against actual spending for a period."""
        statuses = await _budget_status_period(period)
        return _json({
            "period": period or "current-month",
            "budgets": statuses,
            "on_track": sum(1 for s in statuses if s["state"] == "safe"),
            "warning": sum(1 for s in statuses if s["state"] == "warning"),
            "over": sum(1 for s in statuses if s["state"] == "over"),
        })

    @tool(args_schema=EmptyArgs)
    async def list_goals(_: EmptyArgs = EmptyArgs()) -> str:
        """List the user's savings goals with progress. Use for goal questions."""
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(db)
        goals = await service.get_goals(user_id)
        return _json(goals)

    @tool(args_schema=GoalArgs)
    async def get_goal(goal_id: str) -> str:
        """Get a single savings goal by id."""
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(db)
        goal = await service.get_goal(goal_id, user_id)
        if not goal:
            return "Goal not found."
        return _json(goal.model_dump(mode="json"))

    @tool(args_schema=EmptyArgs)
    async def get_goal_progress(_: EmptyArgs = EmptyArgs()) -> str:
        """Get goal progress (current vs target, percentage, remaining)."""
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(db)
        progress = await service.get_progress(user_id)
        return _json(progress)

    @tool(args_schema=EmptyArgs)
    async def list_recurring_expenses(_: EmptyArgs = EmptyArgs()) -> str:
        """List recurring expenses. Use for recurring payment questions."""
        docs = await db.recurring_expenses.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        if not docs:
            return "No recurring expenses found."
        return _json(_clean(docs))

    @tool(args_schema=EmptyArgs)
    async def get_upcoming_recurring(_: EmptyArgs = EmptyArgs()) -> str:
        """Get upcoming recurring expenses (next 30 days)."""
        now = utc_now()
        end = now + timedelta(days=30)
        docs = await db.recurring_expenses.find({
            "user_id": ObjectId(user_id),
            "is_active": True,
            "next_due_date": {"$lte": end},
        }).sort("next_due_date", 1).to_list(length=None)
        if not docs:
            return "No upcoming recurring expenses."
        return _json(_clean(docs))

    @tool(args_schema=EmptyArgs)
    async def list_subscriptions(_: EmptyArgs = EmptyArgs()) -> str:
        """List subscriptions. Use for subscription questions."""
        docs = await db.subscriptions.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        if not docs:
            return "No subscriptions found."
        return _json(_clean(docs))

    @tool(args_schema=EmptyArgs)
    async def get_subscription_renewals(_: EmptyArgs = EmptyArgs()) -> str:
        """Get subscription renewal dates and total monthly cost."""
        now = utc_now()
        docs = await db.subscriptions.find({
            "user_id": ObjectId(user_id), "is_active": True,
        }).to_list(length=None)
        monthly = sum(d.get("monthly_cost", 0) for d in docs)
        return _json({
            "total_monthly_cost": round(monthly, 2),
            "renewals_next_30_days": _clean([
                d for d in docs
                if d.get("next_renewal_date") and now <= d["next_renewal_date"] <= now + timedelta(days=30)
            ]),
        })

    @tool(args_schema=EmptyArgs)
    async def calculate_health(_: EmptyArgs = EmptyArgs()) -> str:
        """Get the user's financial health score, factors, risk level and recommendations."""
        from app.health.services.financial_health_service import FinancialHealthService
        service = FinancialHealthService(db)
        current = await service.get_current(user_id)
        if not current:
            return "No financial health data found. Run a recalculate first."
        recs = await service.get_recommendations(user_id)
        return _json({"current": current, "recommendations": _clean(recs)})

    @tool(args_schema=EmptyArgs)
    async def get_health_history(_: EmptyArgs = EmptyArgs()) -> str:
        """Get financial health score history and trends."""
        from app.health.services.financial_health_service import FinancialHealthService
        service = FinancialHealthService(db)
        history = await service.get_history(user_id)
        trends = await service.get_trends(user_id)
        return _json({"history": _clean(history), "trends": _clean(trends)})

    @tool(args_schema=EmptyArgs)
    async def get_health_risk(_: EmptyArgs = EmptyArgs()) -> str:
        """Get the user's financial risk profile."""
        from app.health.services.financial_health_service import FinancialHealthService
        service = FinancialHealthService(db)
        risk = await service.get_risk(user_id)
        return _json(risk or {})

    @tool(args_schema=EmptyArgs)
    async def get_health_factors(_: EmptyArgs = EmptyArgs()) -> str:
        """Get the factor breakdown of the financial health score."""
        from app.health.services.financial_health_service import FinancialHealthService
        service = FinancialHealthService(db)
        breakdown = await service.get_breakdown(user_id)
        return _json(breakdown)

    @tool(args_schema=EmptyArgs)
    async def get_budget_intelligence(_: EmptyArgs = EmptyArgs()) -> str:
        """Get budget intelligence: budget score, category analysis, savings opportunities, risk, trends."""
        from app.budget_intelligence.services.budget_intelligence_service import BudgetIntelligenceService
        service = BudgetIntelligenceService(db)
        current = await service.get_current(user_id)
        if not current:
            return "No budget intelligence data found."
        return _json(current)

    @tool(args_schema=PeriodArgs)
    async def get_spending_report(period: str | None = None) -> str:
        """Generate a spending report for a YYYY-MM period."""
        from app.services.report_service import get_spending_report
        return _json(await get_spending_report(db, user_id, period))

    @tool(args_schema=PeriodArgs)
    async def get_cashflow_report(period: str | None = None) -> str:
        """Get cash flow (income, expenses, savings) for a period."""
        from app.services.report_service import get_cashflow_report
        return _json(await get_cashflow_report(db, user_id, period))

    @tool(args_schema=EmptyArgs)
    async def detect_anomalies(_: EmptyArgs = EmptyArgs()) -> str:
        """Detect and list unusual spending anomalies."""
        from app.services.anomaly_service import detect_and_store
        anomalies = await detect_and_store(db, user_id)
        return _json(_clean(anomalies))

    @tool(args_schema=EmptyArgs)
    async def list_notifications(_: EmptyArgs = EmptyArgs()) -> str:
        """List notifications and unread count."""
        cursor = db.notifications.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(20)
        docs = await cursor.to_list(length=20)
        unread = await db.notifications.count_documents({"user_id": ObjectId(user_id), "read": False})
        return _json({"unread_count": unread, "notifications": _clean(docs)})

    @tool(args_schema=EmptyArgs)
    async def list_accounts(_: EmptyArgs = EmptyArgs()) -> str:
        """List connected bank accounts and their sync state. Use for account/import questions."""
        docs = await db.bank_accounts.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        if not docs:
            return "No connected accounts found."
        return _json(_clean(docs))

    @tool(args_schema=EmptyArgs)
    async def get_aa_status(_: EmptyArgs = EmptyArgs()) -> str:
        """Get the Account Aggregator sandbox status (consents, data sessions, mode)."""
        consents = await db.aa_consents.find({"user_id": user_id}).sort("created_at", -1).to_list(length=10)
        sessions = await db.aa_data_sessions.find({"user_id": user_id}).sort("created_at", -1).to_list(length=10)
        return _json({
            "mode": "sandbox",
            "label": "Setu AA Sandbox / Demo",
            "consents": _clean(consents),
            "data_sessions": _clean(sessions),
            "message": "This is sandbox/demo financial data, not connected to real bank accounts.",
        })

    @tool(args_schema=CalculateRemainingArgs)
    async def calculate_remaining(income: float, committed: list[float]) -> str:
        """Deterministically calculate how much remains after committed amounts. Use for 'save the rest' planning."""
        total_committed = round(sum(float(c) for c in committed), 2)
        remaining = round(income - total_committed, 2)
        return _json({
            "income": round(float(income), 2),
            "committed_total": total_committed,
            "remaining": remaining,
            "note": "Authoritative calculation performed by the backend, not the LLM.",
        })

    @tool(args_schema=CategorizeArgs)
    async def categorize(description: str) -> str:
        """Suggest a category for a transaction description (deterministic)."""
        category, confidence = suggest_category(description)
        return _json({"description": description, "category": category, "confidence": confidence})

    # ---- write planning tool ---------------------------------------------
    @tool(args_schema=ProposeActionsArgs)
    async def propose_actions(actions: list[dict[str, Any]]) -> str:
        """PROPOSE (not execute) financial changes for the user to confirm.

        Call this ONLY when the user explicitly requests a create/update/delete.
        Validates every action, records ownership checks and stores a pending
        proposal. The user must confirm it before anything is applied.
        """
        parsed: list[ProposedAction] = []
        for i, raw in enumerate(actions):
            try:
                kind = ActionKind(raw.get("kind"))
            except (ValueError, KeyError):
                raise ValueError(f"Action {i}: invalid kind '{raw.get('kind')}'")
            params = raw.get("params") or {}
            errors = validate_params(kind, params)
            if errors:
                raise ValueError(f"Action {i} ({kind.value}) validation failed: {'; '.join(errors)}")
            summary = raw.get("summary") or f"{kind.value} action"
            parsed.append(ProposedAction(
                kind=kind, summary=summary, params=params,
                destructive=bool(raw.get("destructive", kind in DESTRUCTIVE_KINDS)),
            ))

        if not parsed:
            raise ValueError("At least one action is required.")

        # Ownership checks for record-based actions (fail fast on confirmation).
        for action in parsed:
            if not await _verify_ownership(action):
                raise ValueError(
                    f"Could not find the record for action '{action.summary}'. "
                    "Ask the user to identify the correct record first."
                )

        now = utc_now()
        doc = {
            "user_id": user_id,
            "session_id": session_id,
            "status": ProposalStatus.PENDING.value,
            "actions": [a.model_dump(mode="json") for a in parsed],
            "created_at": now,
            "updated_at": now,
            "execution": [],
        }
        result = await db.agent_proposals.insert_one(doc)
        proposal = Proposal(
            id=str(result.inserted_id), user_id=user_id,
            session_id=session_id, status=ProposalStatus.PENDING,
            actions=parsed, created_at=now, updated_at=now,
        )
        proposal_created.append(proposal)
        return (
            f"Proposal recorded (id {proposal.id}) with {len(parsed)} action(s). "
            "The proposed changes will be shown to the user for confirmation. "
            "Summarize the plan clearly and ask the user to confirm."
        )

    async def _verify_ownership(action: ProposedAction) -> bool:
        """Verify that the target record exists and belongs to the user."""
        params = action.params
        collection_map = {
            "expense_id": "expenses",
            "budget_id": "budgets",
            "goal_id": "financial_goals",
            "recurring_id": "recurring_expenses",
            "subscription_id": "subscriptions",
            "notification_id": "notifications",
        }
        for field, collection in collection_map.items():
            record_id = params.get(field)
            if not record_id:
                continue
            try:
                oid = to_object_id(record_id)
            except ValueError:
                return False
            return await db[collection].find_one({"_id": oid, "user_id": ObjectId(user_id)}) is not None
        return True

    read_tools = [
        get_income, get_expenses, get_expense_by_id, search_expenses,
        summarize_spending, get_spending_by_category, get_spending_by_date_range,
        list_budgets, get_budget, get_budget_usage, get_remaining_budget,
        compare_budget_actual, list_goals, get_goal, get_goal_progress,
        list_recurring_expenses, get_upcoming_recurring,
        list_subscriptions, get_subscription_renewals,
        calculate_health, get_health_history, get_health_risk, get_health_factors,
        get_budget_intelligence, get_spending_report, get_cashflow_report,
        detect_anomalies, list_notifications, list_accounts, get_aa_status,
        calculate_remaining, categorize,
    ]
    return read_tools + [propose_actions], proposal_created


def get_system_prompt() -> str:
    return SYSTEM_PROMPT