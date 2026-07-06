import logging

from app.health.models.financial_health import FinancialHealth
from app.health.models.health_history import HealthHistory
from app.health.repositories.health_history_repository import (
    MongoHealthHistoryRepository,
)

logger = logging.getLogger("intellimoney")


class HealthHistoryService:
    def __init__(self, history_repo: MongoHealthHistoryRepository):
        self._history_repo = history_repo

    async def record(self, health: FinancialHealth) -> HealthHistory:
        existing = await self._history_repo.get_by_period(health.user_id, health.period)
        if existing:
            return existing

        entry = HealthHistory(
            user_id=health.user_id,
            period=health.period,
            score=health.score,
            risk_level=health.risk_level,
            savings_rate=health.savings_rate,
            budget_adherence=health.budget_adherence,
            expense_stability=health.expense_stability,
            cash_flow_stability=health.cash_flow_stability,
            income_consistency=health.income_consistency,
            emergency_fund_score=health.emergency_fund_score,
            recurring_expense_ratio=health.recurring_expense_ratio,
            essential_spending_ratio=health.essential_spending_ratio,
            calculated_at=health.calculated_at,
        )
        result = await self._history_repo.create(entry)
        logger.info(
            "health_history_recorded user=%s period=%s score=%d",
            health.user_id, health.period, health.score,
        )
        return result

    async def get_history(self, user_id: str, limit: int = 36) -> list[HealthHistory]:
        return await self._history_repo.get_by_user(user_id, limit)
