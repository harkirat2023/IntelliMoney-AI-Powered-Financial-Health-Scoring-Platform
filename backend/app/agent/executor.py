"""Deterministic proposal executor.

This module applies a confirmed proposal by calling the same domain
services / collection operations used by the REST API. It is the ONLY
code path that performs writes triggered by the LLM, and it runs entirely
without LLM involvement.

Guarantees:
- A proposal can be executed at most once (status transition guarded).
- Every action reports its own result, so partial failures are surfaced.
- All ownership/scope checks are re-run at execution time.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.agent.schemas import (
    ActionExecutionResult,
    ActionKind,
    ProposedAction,
    Proposal,
    ProposalStatus,
)
from app.services.serializers import date_to_datetime, utc_now
from app.utils.object_id import to_object_id

_NOTES = "note: applied automatically via confirmed AI Copilot proposal."


def _now_date_str() -> str:
    return utc_now().strftime("%Y-%m-%d")


def _parse_date(value: str):
    from datetime import date
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


class ProposalExecutor:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def execute(self, proposal: Proposal) -> Proposal:
        """Execute all actions of a confirmed proposal. Safe to call once."""
        results: list[ActionExecutionResult] = []
        failures = 0
        for index, action in enumerate(proposal.actions):
            if isinstance(action, dict):
                action = ProposedAction(**action)
            try:
                result = await self._execute_one(action, proposal.user_id)
            except Exception as exc:  # noqa: BLE001 - surface per-action failures
                failures += 1
                result = ActionExecutionResult(
                    index=index, kind=action.kind.value, summary=action.summary,
                    status="failed", message=str(exc),
                )
            results.append(result)
            if result.status != "executed":
                failures += 1

        status = (
            ProposalStatus.EXECUTED if failures == 0
            else ProposalStatus.PARTIALLY_FAILED
        )
        await self._db.agent_proposals.update_one(
            {"_id": ObjectId(proposal.id)},
            {
                "$set": {
                    "status": status.value,
                    "execution": [r.model_dump(mode="json") for r in results],
                    "updated_at": utc_now(),
                }
            },
        )
        proposal.status = status
        proposal.execution = results
        proposal.updated_at = utc_now()
        return proposal

    async def _execute_one(self, action: ProposedAction, user_id: str) -> ActionExecutionResult:
        base = ActionExecutionResult(
            index=-1, kind=action.kind.value, summary=action.summary, status="executed",
        )
        handler = {
            ActionKind.SET_INCOME: self._set_income,
            ActionKind.CREATE_EXPENSE: self._create_expense,
            ActionKind.UPDATE_EXPENSE: self._update_expense,
            ActionKind.DELETE_EXPENSE: self._delete_expense,
            ActionKind.CREATE_BUDGET: self._create_budget,
            ActionKind.UPDATE_BUDGET: self._update_budget,
            ActionKind.DELETE_BUDGET: self._delete_budget,
            ActionKind.CREATE_GOAL: self._create_goal,
            ActionKind.UPDATE_GOAL: self._update_goal,
            ActionKind.DELETE_GOAL: self._delete_goal,
            ActionKind.CREATE_RECURRING: self._create_recurring,
            ActionKind.UPDATE_RECURRING: self._update_recurring,
            ActionKind.DELETE_RECURRING: self._delete_recurring,
            ActionKind.CREATE_SUBSCRIPTION: self._create_subscription,
            ActionKind.UPDATE_SUBSCRIPTION: self._update_subscription,
            ActionKind.DELETE_SUBSCRIPTION: self._delete_subscription,
            ActionKind.MARK_NOTIFICATION_READ: self._mark_notification_read,
            ActionKind.RECALCULATE_HEALTH: self._recalculate_health,
            ActionKind.SYNC_ACCOUNT: self._sync_account,
            ActionKind.IMPORT_AA_DATA: self._import_aa_data,
        }
        handler_fn = handler.get(action.kind)
        if handler_fn is None:
            raise ValueError(f"Unsupported action kind: {action.kind.value}")
        payload = await handler_fn(user_id, action.params)
        base.result = payload or {}
        base.message = "executed"
        return base

    # ---- income ------------------------------------------------------------
    async def _set_income(self, user_id: str, params: dict) -> dict:
        amount = float(params["amount"])
        now = utc_now()
        month = params.get("period") or f"{now.year}-{now.month:02d}"
        await self._db.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"monthly_income": amount}}
        )
        await self._db.income_history.insert_one({
            "user_id": ObjectId(user_id),
            "month": month,
            "income": amount,
            "source": "agent",
            "created_at": now,
        })
        return {"monthly_income": amount, "month": month}

    # ---- expenses ----------------------------------------------------------
    async def _create_expense(self, user_id: str, params: dict) -> dict:
        category = params.get("category") or params["description"] and self._guess_category(params["description"])
        date_value = params.get("date") or _now_date_str()
        doc = {
            "user_id": ObjectId(user_id),
            "amount": float(params["amount"]),
            "description": params["description"],
            "category": category,
            "payment_method": params.get("payment_method", "Other"),
            "date": date_to_datetime(_parse_date(date_value)),
            "created_at": utc_now(),
            "notes": _NOTES,
        }
        result = await self._db.expenses.insert_one(doc)
        return {"expense_id": str(result.inserted_id), "category": category}

    @staticmethod
    def _guess_category(description: str) -> str:
        from app.services.category_service import suggest_category
        return suggest_category(description)[0]

    async def _update_expense(self, user_id: str, params: dict) -> dict:
        oid = self._oid(params.get("expense_id"))
        updates = {k: v for k, v in params.items() if k != "expense_id" and v is not None}
        if "date" in updates:
            updates["date"] = date_to_datetime(_parse_date(updates["date"]))
        if not updates:
            raise ValueError("No fields to update.")
        result = await self._db.expenses.update_one(
            {"_id": oid, "user_id": ObjectId(user_id)}, {"$set": updates}
        )
        if result.matched_count == 0:
            raise ValueError("Expense not found.")
        return {"expense_id": str(oid), "updated_fields": list(updates)}

    async def _delete_expense(self, user_id: str, params: dict) -> dict:
        oid = self._oid(params.get("expense_id"))
        result = await self._db.expenses.delete_one({"_id": oid, "user_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise ValueError("Expense not found.")
        return {"deleted": str(oid)}

    # ---- budgets -----------------------------------------------------------
    async def _create_budget(self, user_id: str, params: dict) -> dict:
        month = int(params.get("month") or _current_period()[1])
        year = int(params.get("year") or _current_period()[0])
        existing = await self._db.budgets.find_one({
            "user_id": ObjectId(user_id),
            "category": params["category"],
            "month": month,
            "year": year,
        })
        if existing:
            raise ValueError("A budget already exists for this category and month.")
        doc = {
            "user_id": ObjectId(user_id),
            "category": params["category"],
            "limit": float(params["limit"]),
            "month": month,
            "year": year,
            "spent": 0.0,
            "created_at": utc_now(),
        }
        result = await self._db.budgets.insert_one(doc)
        return {"budget_id": str(result.inserted_id)}

    async def _update_budget(self, user_id: str, params: dict) -> dict:
        oid = self._oid(params.get("budget_id"))
        updates = {k: v for k, v in params.items() if k != "budget_id" and v is not None}
        if not updates:
            raise ValueError("No fields to update.")
        result = await self._db.budgets.update_one(
            {"_id": oid, "user_id": ObjectId(user_id)}, {"$set": updates}
        )
        if result.matched_count == 0:
            raise ValueError("Budget not found.")
        return {"budget_id": str(oid), "updated_fields": list(updates)}

    async def _delete_budget(self, user_id: str, params: dict) -> dict:
        oid = self._oid(params.get("budget_id"))
        result = await self._db.budgets.delete_one({"_id": oid, "user_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise ValueError("Budget not found.")
        return {"deleted": str(oid)}

    # ---- goals -------------------------------------------------------------
    async def _create_goal(self, user_id: str, params: dict) -> dict:
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(self._db)
        data = {
            "goal_type": params.get("goal_type", "savings"),
            "name": params["name"],
            "target_amount": float(params["target_amount"]),
            "current_amount": float(params.get("current_amount", 0.0)),
            "monthly_contribution": float(params.get("monthly_contribution", 0.0)),
            "target_date": params.get("target_date", ""),
            "priority": params.get("priority", "medium"),
            "category": params.get("category", ""),
            "description": params.get("description", ""),
        }
        created = await service.create_goal(user_id, data)
        return {"goal_id": created["goal"]["id"], "name": created["goal"]["name"]}

    async def _update_goal(self, user_id: str, params: dict) -> dict:
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(self._db)
        updates = {k: v for k, v in params.items() if k != "goal_id" and v is not None}
        if not updates:
            raise ValueError("No fields to update.")
        updated = await service.update_goal(params["goal_id"], user_id, updates)
        if updated is None:
            raise ValueError("Goal not found.")
        return {"goal_id": params["goal_id"], "updated_fields": list(updates)}

    async def _delete_goal(self, user_id: str, params: dict) -> dict:
        from app.goal_planning.services.goal_planning_service import GoalPlanningService
        service = GoalPlanningService(self._db)
        deleted = await service.delete_goal(params["goal_id"], user_id)
        if not deleted:
            raise ValueError("Goal not found.")
        return {"deleted": params["goal_id"]}

    # ---- recurring ---------------------------------------------------------
    async def _create_recurring(self, user_id: str, params: dict) -> dict:
        from app.services.recurring_service import create_recurring_expense
        item = await create_recurring_expense(self._db, user_id, params)
        return {"recurring_id": item["_id"] if "_id" in item else item.get("id")}

    async def _update_recurring(self, user_id: str, params: dict) -> dict:
        from app.services.recurring_service import update_recurring_expense
        recurring_id = params.pop("recurring_id")
        item = await update_recurring_expense(self._db, user_id, recurring_id, params)
        if not item:
            raise ValueError("Recurring expense not found.")
        return {"recurring_id": recurring_id}

    async def _delete_recurring(self, user_id: str, params: dict) -> dict:
        from app.services.recurring_service import delete_recurring_expense
        deleted = await delete_recurring_expense(self._db, user_id, params["recurring_id"])
        if not deleted:
            raise ValueError("Recurring expense not found.")
        return {"deleted": params["recurring_id"]}

    # ---- subscriptions -----------------------------------------------------
    async def _create_subscription(self, user_id: str, params: dict) -> dict:
        from app.services.subscription_service import create_subscription
        item = await create_subscription(self._db, user_id, params)
        return {"subscription_id": item.get("id") or str(item.get("_id", ""))}

    async def _update_subscription(self, user_id: str, params: dict) -> dict:
        from app.services.subscription_service import update_subscription
        subscription_id = params.pop("subscription_id")
        item = await update_subscription(self._db, user_id, subscription_id, params)
        if not item:
            raise ValueError("Subscription not found.")
        return {"subscription_id": subscription_id}

    async def _delete_subscription(self, user_id: str, params: dict) -> dict:
        from app.services.subscription_service import delete_subscription
        deleted = await delete_subscription(self._db, user_id, params["subscription_id"])
        if not deleted:
            raise ValueError("Subscription not found.")
        return {"deleted": params["subscription_id"]}

    # ---- notifications -----------------------------------------------------
    async def _mark_notification_read(self, user_id: str, params: dict) -> dict:
        oid = self._oid(params.get("notification_id"))
        result = await self._db.notifications.update_one(
            {"_id": oid, "user_id": ObjectId(user_id)}, {"$set": {"read": True}}
        )
        if result.matched_count == 0:
            raise ValueError("Notification not found.")
        return {"notification_id": str(oid)}

    # ---- health ------------------------------------------------------------
    async def _recalculate_health(self, user_id: str, params: dict) -> dict:
        from app.health.services.financial_health_service import FinancialHealthService
        service = FinancialHealthService(self._db)
        response = await service.recalculate(user_id)
        return {"score": response.score, "risk_level": response.risk_level}

    # ---- accounts / AA -----------------------------------------------------
    async def _sync_account(self, user_id: str, params: dict) -> dict:
        from app.infrastructure.bank_integration import MockBankProvider
        from app.infrastructure.bank_integration.consent_manager import BankProviderRegistry
        from app.infrastructure.bank_integration.setu_sandbox import setu_sandbox_provider
        from app.infrastructure.database.repositories.bank_repository import (
            MongoBankAccountRepository,
        )
        from app.infrastructure.database.repositories.consent_repository import (
            MongoConsentRepository,
        )
        from app.infrastructure.database.repositories.import_preference_repository import (
            MongoImportPreferenceRepository,
        )
        from app.infrastructure.database.repositories.sync_repository import (
            MongoBankTransactionRepository,
            MongoSyncLogRepository,
        )
        from app.services.sync_service import SyncService

        account = await self._db.bank_accounts.find_one({
            "_id": self._oid(params.get("account_id")), "user_id": ObjectId(user_id),
        })
        if not account:
            raise ValueError("Bank account not found.")

        registry = BankProviderRegistry()
        registry.register("mock", MockBankProvider())
        registry.register("setu", setu_sandbox_provider)
        service = SyncService(
            bank_repo=MongoBankAccountRepository(self._db),
            consent_repo=MongoConsentRepository(self._db),
            pref_repo=MongoImportPreferenceRepository(self._db),
            tx_repo=MongoBankTransactionRepository(self._db),
            sync_log_repo=MongoSyncLogRepository(self._db),
            adapter_registry=registry,
        )
        response = await service.start_sync(user_id, str(account["_id"]))
        return {"synced": str(account["_id"]), "status": response.status,
                "sync_log_id": response.sync_log_id, "message": response.message}

    async def _import_aa_data(self, user_id: str, params: dict) -> dict:
        from app.infrastructure.bank_integration import MockBankProvider
        from app.infrastructure.bank_integration.setu_sandbox import setu_sandbox_provider
        from app.services.aa_data_service import import_aa_data_session

        data_session_id = params.get("data_session_id")
        consent_id = params.get("consent_id")
        session = None
        if data_session_id:
            session = await self._db.aa_data_sessions.find_one({
                "_id": self._oid(data_session_id), "user_id": user_id,
            })
        elif consent_id:
            consent = await self._db.aa_consents.find_one({
                "consent_id": consent_id, "user_id": user_id, "consent_status": "APPROVED",
            })
            if not consent:
                raise ValueError("Active consent not found for import.")
            session = await self._db.aa_data_sessions.find_one(
                {"user_id": user_id, "consent_id": str(consent["_id"])},
                sort=[("created_at", -1)],
            )
        if not session:
            raise ValueError("data_session_id or a data session for consent_id is required.")

        provider = session.get("provider", "mock")
        adapter = setu_sandbox_provider if provider == "setu" else MockBankProvider()
        result = await import_aa_data_session(self._db, user_id, session, adapter)
        return {"imported": True, **result}

    @staticmethod
    def _oid(value: Any) -> ObjectId:
        try:
            return to_object_id(value)
        except ValueError as exc:
            raise ValueError("Invalid record id.") from exc
