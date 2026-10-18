"""Synchronize derived per-user aggregates with the expenses ledger.

After any mutation to expense-bearing collections (manual expense routes,
confirmed receipts, agent-executed proposal actions, budget mutations) call
``refresh_aggregates`` so every read endpoint (dashboard, budgets, cash flow,
financial metrics, financial health) returns consistent numbers.

The ``expenses`` collection is the single source of truth for spending. All
computation here is deterministic and backend-owned; no LLM is involved and
each derived store is upserted independently so a partial failure never leaves
the ledger inconsistent.
"""

import logging
from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.infrastructure.database.repositories.expense_repository import MongoExpenseRepository
from app.processing.models.cash_flow_summary import CashFlowSummary
from app.processing.models.dashboard_metrics import DashboardMetrics
from app.processing.repositories.budget_usage_repository import MongoBudgetUsageRepository
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository
from app.processing.repositories.financial_metrics_repository import MongoFinancialMetricsRepository
from app.processing.services.budget_processing_service import BudgetProcessingService
from app.processing.services.financial_metrics_service import FinancialMetricsService
from app.utils.date_utils import month_bounds, utc_now
from app.utils.object_id import to_object_id

logger = logging.getLogger("intellimoney")


async def _month_credits(db: AsyncIOMotorDatabase, oid, start, end) -> tuple[float, list[dict]]:
    """Credit income for the period, aggregated from bank financial transactions."""
    cursor = db.financial_transactions.aggregate(
        [
            {
                "$match": {
                    "user_id": oid,
                    "transaction_date": {"$gte": start, "$lte": end},
                    "transaction_type": "CREDIT",
                }
            },
            {
                "$group": {
                    "_id": "$assigned_category",
                    "total": {"$sum": "$amount"},
                }
            },
        ]
    )
    categories = []
    total = 0.0
    async for doc in cursor:
        amount = float(doc.get("total") or 0)
        category = doc.get("_id") or "Other"
        categories.append({"category": category, "amount": round(amount, 2)})
        total += amount
    categories.sort(key=lambda kv: -kv["amount"])
    return round(total, 2), categories


async def refresh_aggregates(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    now = utc_now()
    month, year = now.month, now.year
    period = f"{year}-{month:02d}"
    oid = to_object_id(user_id)
    start, end = month_bounds(year, month)
    summary: dict = {"period": period}

    # 1. Budget usage (written from the authoritative expense ledger).
    budget_usage_repo = MongoBudgetUsageRepository(db)
    budget_states = await BudgetProcessingService(db, budget_usage_repo).update_budget_usage(user_id)
    summary["budget_usage_updated"] = len(budget_states)

    # 2. Current-period expenses.
    expenses = [
        doc async for doc in db.expenses.find(
            {"user_id": oid, "date": {"$gte": start, "$lte": end}}
        )
    ]
    total_spending = round(sum(float(e.get("amount", 0)) for e in expenses), 2)
    spending_by_category: dict[str, float] = defaultdict(float)
    for e in expenses:
        category = e.get("category", "Other")
        spending_by_category[category] += float(e.get("amount", 0))
    sorted_categories = sorted(spending_by_category.items(), key=lambda kv: -kv[1])

    spending_list = [
        {
            "category": c,
            "amount": round(a, 2),
            "percentage": round((a / total_spending) * 100, 2) if total_spending else 0,
        }
        for c, a in sorted_categories
    ]

    # 3. Income: explicit monthly income wins, else bank credit transactions.
    user_doc = await db.users.find_one({"_id": oid})
    monthly_income = float((user_doc or {}).get("monthly_income") or 0)
    credit_total, credit_categories = await _month_credits(db, oid, start, end)
    total_income = round(max(monthly_income, credit_total), 2)
    net_savings = round(total_income - total_spending, 2)
    savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0.0

    # 4. Dashboard metrics (expense-ledger aggregates that persist for /dashboard).
    monthly_trend = []
    for offset in range(5, -1, -1):
        m = month - offset
        y = year
        while m <= 0:
            m += 12
            y -= 1
        s, e = month_bounds(y, m)
        docs = [
            doc async for doc in db.expenses.find(
                {"user_id": oid, "date": {"$gte": s, "$lte": e}}
            )
        ]
        monthly_trend.append({
            "month": f"{y}-{m:02d}",
            "spending": round(sum(float(d.get("amount", 0)) for d in docs), 2),
            "income": total_income if offset == 0 else 0.0,
        })

    budget_overview = [
        {
            "category": b["category"],
            "limit": b["limit"],
            "spent": b["spent"],
            "state": b["state"],
        }
        for b in budget_states
    ]

    dashboard_repo = MongoDashboardMetricsRepository(db)
    dashboard = DashboardMetrics(
        user_id=user_id,
        period=period,
        total_spending=total_spending,
        total_income=total_income,
        net_savings=net_savings,
        savings_rate=savings_rate,
        expense_count=len(expenses),
        spending_by_category=spending_list,
        monthly_trend=monthly_trend,
        top_merchants=[],
        budget_overview=budget_overview,
        updated_at=now,
    )
    await dashboard_repo.upsert(dashboard)
    summary["dashboard_metrics_updated"] = 1

    # 5. Cash-flow summary (expense by category + credit income).
    cash_flow_repo = MongoCashFlowRepository(db)
    cash_flow = CashFlowSummary(
        user_id=user_id,
        year=year,
        month=month,
        total_income=total_income,
        total_expenses=total_spending,
        net_cash_flow=net_savings,
        income_by_category=credit_categories,
        expense_by_category=[
            {"category": c, "amount": round(a, 2)} for c, a in sorted_categories
        ],
        updated_at=now,
    )
    await cash_flow_repo.upsert(cash_flow)
    summary["cash_flow_updated"] = 1

    # 6. Financial metrics (already expense-based).
    metrics_repo = MongoFinancialMetricsRepository(db)
    metrics_service = FinancialMetricsService(MongoExpenseRepository(db), metrics_repo)
    metrics = await metrics_service.compute_metrics(user_id, savings_rate, budget_states)
    summary["financial_metrics_updated"] = 1
    summary["financial_score"] = metrics.score
    summary["risk_level"] = metrics.risk_level

    # 7. Financial health (recompute always, not gated on existing period doc).
    try:
        from app.health.services.financial_health_service import FinancialHealthService

        health = await FinancialHealthService(db).recalculate(user_id)
        summary["health_score"] = health.score
        summary["health_recalculated"] = 1
    except Exception as exc:  # noqa: BLE001 - keep the rest of the refresh intact
        logger.warning("health_recalc_failed user=%s err=%s", user_id, exc)

    logger.info(
        "spending_sync_complete user=%s period=%s spending=%s income=%s budgets=%d",
        user_id, period, total_spending, total_income, len(budget_states),
    )
    return summary