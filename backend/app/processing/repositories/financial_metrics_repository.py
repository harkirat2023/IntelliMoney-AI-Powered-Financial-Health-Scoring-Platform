from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.financial_metrics import FinancialMetrics
from app.utils.object_id import to_object_id


class FinancialMetricsRepository(ABC):
    @abstractmethod
    async def upsert(self, metrics: FinancialMetrics) -> FinancialMetrics:
        ...

    @abstractmethod
    async def get_latest_by_user(
        self, user_id: str,
    ) -> FinancialMetrics | None:
        ...

    @abstractmethod
    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> FinancialMetrics | None:
        ...

    @abstractmethod
    async def get_trend(
        self, user_id: str, months: int = 6,
    ) -> list[FinancialMetrics]:
        ...


class MongoFinancialMetricsRepository(FinancialMetricsRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, metrics: FinancialMetrics) -> FinancialMetrics:
        doc = metrics.to_mongo()
        filter_key = {"user_id": doc["user_id"], "period": metrics.period}
        await self._db.financial_metrics.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.financial_metrics.find_one(filter_key)
        return FinancialMetrics.from_mongo(result) if result else metrics

    async def get_latest_by_user(self, user_id: str) -> FinancialMetrics | None:
        cursor = self._db.financial_metrics.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(1)
        docs = [doc async for doc in cursor]
        return FinancialMetrics.from_mongo(docs[0]) if docs else None

    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> FinancialMetrics | None:
        doc = await self._db.financial_metrics.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return FinancialMetrics.from_mongo(doc) if doc else None

    async def get_trend(
        self, user_id: str, months: int = 6,
    ) -> list[FinancialMetrics]:
        cursor = self._db.financial_metrics.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(months)
        return [FinancialMetrics.from_mongo(doc) async for doc in cursor]
