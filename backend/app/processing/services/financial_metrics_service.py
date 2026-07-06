import logging
from statistics import mean, pstdev

from app.core.constants import RISK_LEVELS

logger = logging.getLogger("intellimoney")
from app.domain.expenses.models import Expense
from app.infrastructure.database.repositories.expense_repository import MongoExpenseRepository
from app.processing.models.financial_metrics import FinancialMetrics
from app.processing.repositories.financial_metrics_repository import MongoFinancialMetricsRepository
from app.utils.date_utils import month_bounds, utc_now


class FinancialMetricsService:
    def __init__(self, expense_repo: MongoExpenseRepository, metrics_repo: MongoFinancialMetricsRepository):
        self._expense_repo = expense_repo
        self._metrics_repo = metrics_repo

    async def compute_metrics(
        self, user_id: str, savings_rate: float,
        budget_states: list[dict], expense_stability_override: float | None = None,
    ) -> FinancialMetrics:
        now = utc_now()
        savings_rate = max(min(savings_rate, 100), -100)
        savings_component = max(min(savings_rate / 30 * 100, 100), 0)

        if budget_states:
            adherence_values = [
                max(0, 100 - max(0, item["percentage_used"] - 100))
                for item in budget_states
            ]
            budget_adherence = mean(adherence_values)
        else:
            budget_adherence = 70.0

        monthly_totals = []
        for offset in range(5, -1, -1):
            month = now.month - offset
            year = now.year
            while month <= 0:
                month += 12
                year -= 1
            start, end = month_bounds(year, month)
            expenses = await self._expense_repo.get_by_user(user_id, date_from=start, date_to=end)
            total = sum(exp.amount for exp in expenses)
            monthly_totals.append(total)

        avg_spend = mean(monthly_totals) if monthly_totals else 0
        if expense_stability_override is not None:
            stability = expense_stability_override
        elif avg_spend > 0:
            stability = max(0, 100 - (pstdev(monthly_totals) / avg_spend * 100))
        else:
            stability = 100.0

        now_start, now_end = month_bounds(now.year, now.month)
        current_expenses = await self._expense_repo.get_by_user(user_id, date_from=now_start, date_to=now_end)
        discretionary = sum(exp.amount for exp in current_expenses if exp.category in {"Shopping", "Entertainment", "Travel"})
        total_spending = sum(exp.amount for exp in current_expenses) or 1

        total_spending = total_spending or 1
        category_risk = max(0, 100 - (discretionary / total_spending * 100))

        score = round(
            savings_component * 0.35
            + budget_adherence * 0.30
            + stability * 0.20
            + category_risk * 0.15
        )
        score = int(max(0, min(score, 100)))

        if score >= 80:
            risk_level = "Excellent"
        elif score >= 65:
            risk_level = "Good"
        elif score >= 45:
            risk_level = "Moderate"
        else:
            risk_level = "Needs Attention"

        discretionary_ratio = round(discretionary / total_spending, 4) if total_spending else 0.0

        period = f"{now.year}-{now.month:02d}"
        previous = await self._metrics_repo.get_by_user_and_period(user_id, period)
        month_over_month = score - (previous.score if previous else 0)
        trend = "stable"
        if month_over_month > 5:
            trend = "improving"
        elif month_over_month < -5:
            trend = "declining"

        metrics = FinancialMetrics(
            user_id=user_id,
            period=period,
            calculated_at=now,
            score=score,
            risk_level=risk_level,
            savings_rate=round(savings_rate, 2),
            budget_adherence=round(budget_adherence, 2),
            expense_stability=round(stability, 2),
            discretionary_ratio=discretionary_ratio,
            month_over_month_change=month_over_month,
            trend=trend,
        )

        return await self._metrics_repo.upsert(metrics)
