from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.dashboard_metrics import DashboardMetrics
from app.utils.object_id import to_object_id


class DashboardMetricsRepository(ABC):
    @abstractmethod
    async def upsert(self, metrics: DashboardMetrics) -> DashboardMetrics:
        ...

    @abstractmethod
    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> DashboardMetrics | None:
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, limit: int = 6,
    ) -> list[DashboardMetrics]:
        ...


class MongoDashboardMetricsRepository(DashboardMetricsRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, metrics: DashboardMetrics) -> DashboardMetrics:
        doc = metrics.to_mongo()
        filter_key = {"user_id": doc["user_id"], "period": metrics.period}
        await self._db.dashboard_metrics.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.dashboard_metrics.find_one(filter_key)
        return DashboardMetrics.from_mongo(result) if result else metrics

    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> DashboardMetrics | None:
        doc = await self._db.dashboard_metrics.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return DashboardMetrics.from_mongo(doc) if doc else None

    async def get_by_user(
        self, user_id: str, limit: int = 6,
    ) -> list[DashboardMetrics]:
        cursor = self._db.dashboard_metrics.find(
            {"user_id": to_object_id(user_id)}
        ).sort("updated_at", -1).limit(limit)
        return [DashboardMetrics.from_mongo(doc) async for doc in cursor]
