from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository


class DashboardReadService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._dash_repo = MongoDashboardMetricsRepository(db)
        self._cf_repo = MongoCashFlowRepository(db)

    async def get_summary(self, user_id: str, period: str):
        return await self._dash_repo.get_by_user_and_period(user_id, period)

    async def get_cashflow(self, user_id: str, months: int):
        return await self._cf_repo.get_by_user(user_id, months)

    async def get_monthly_trends(self, user_id: str, months: int):
        return await self._dash_repo.get_by_user(user_id, months)