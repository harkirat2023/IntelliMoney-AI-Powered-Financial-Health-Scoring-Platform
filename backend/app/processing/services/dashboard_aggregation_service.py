import logging
from collections import defaultdict
from datetime import datetime

from app.domain.financial_transactions.models import FinancialTransaction

logger = logging.getLogger("intellimoney")
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.processing.models.dashboard_metrics import DashboardMetrics
from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository
from app.utils.date_utils import month_bounds, utc_now


class DashboardAggregationService:
    def __init__(
        self, tx_repo: MongoFinancialTransactionRepository,
        dash_repo: MongoDashboardMetricsRepository,
    ):
        self._tx_repo = tx_repo
        self._dash_repo = dash_repo

    async def aggregate(
        self, user_id: str, transactions: list[FinancialTransaction],
        savings_data: dict, budget_states: list[dict],
    ) -> DashboardMetrics:
        now = utc_now()
        period = f"{now.year}-{now.month:02d}"

        spending_by_cat: dict[str, float] = defaultdict(float)
        merchant_totals: dict[str, dict] = {}
        expense_count = 0

        for tx in transactions:
            if tx.transaction_type == "DEBIT" and not tx.is_refund and not tx.is_transfer:
                spending_by_cat[tx.assigned_category or "Other"] += tx.amount
                expense_count += 1
                merchant = tx.normalized_merchant or tx.cleaned_merchant or "Unknown"
                if merchant not in merchant_totals:
                    merchant_totals[merchant] = {"amount": 0.0, "count": 0}
                merchant_totals[merchant]["amount"] += tx.amount
                merchant_totals[merchant]["count"] += 1

        total_spending = round(sum(spending_by_cat.values()), 2)
        total_income = savings_data.get("total_income", 0)
        net_savings = savings_data.get("net_savings", 0)
        savings_rate = savings_data.get("savings_rate", 0)

        spending_list = [
            {"category": c, "amount": round(a, 2), "percentage": round((a / total_spending * 100), 2) if total_spending else 0}
            for c, a in sorted(spending_by_cat.items(), key=lambda x: -x[1])
        ]

        top_merchants = sorted(
            [{"merchant": m, "amount": round(d["amount"], 2), "count": d["count"]}
             for m, d in merchant_totals.items()],
            key=lambda x: -x["amount"],
        )[:10]

        monthly_trend = []
        for offset in range(5, -1, -1):
            m = now.month - offset
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            label = datetime(y, m, 1).strftime("%b")
            start, end = month_bounds(y, m)
            txns = await self._tx_repo.find_by_date_range(user_id, start, end)
            s_total = sum(
                tx.amount for tx in txns
                if tx.transaction_type == "DEBIT" and not tx.is_refund and not tx.is_transfer
            )
            i_total = sum(tx.amount for tx in txns if tx.transaction_type == "CREDIT")
            monthly_trend.append({"month": label, "spending": round(s_total, 2), "income": round(i_total, 2)})

        budget_overview = [
            {"category": b["category"], "limit": b["limit"], "spent": b["spent"], "state": b["state"]}
            for b in budget_states
        ]

        metrics = DashboardMetrics(
            user_id=user_id,
            period=period,
            total_spending=total_spending,
            total_income=round(total_income, 2),
            net_savings=round(net_savings, 2),
            savings_rate=round(savings_rate, 2),
            expense_count=expense_count,
            spending_by_category=spending_list,
            monthly_trend=monthly_trend,
            top_merchants=top_merchants,
            budget_overview=budget_overview,
            updated_at=now,
        )

        return await self._dash_repo.upsert(metrics)
