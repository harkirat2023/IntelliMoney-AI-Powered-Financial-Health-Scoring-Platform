from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.monthly_summary import MonthlySummary
from app.utils.object_id import to_object_id


class MonthlySummaryRepository(ABC):
    @abstractmethod
    async def upsert(self, summary: MonthlySummary) -> MonthlySummary:
        ...

    @abstractmethod
    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> MonthlySummary | None:
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, limit: int = 12,
    ) -> list[MonthlySummary]:
        ...


class MongoMonthlySummaryRepository(MonthlySummaryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, summary: MonthlySummary) -> MonthlySummary:
        doc = summary.to_mongo()
        filter_key = {"user_id": doc["user_id"], "period": summary.period}
        await self._db.monthly_summary.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.monthly_summary.find_one(filter_key)
        return MonthlySummary.from_mongo(result) if result else summary

    async def get_by_user_and_period(
        self, user_id: str, period: str,
    ) -> MonthlySummary | None:
        doc = await self._db.monthly_summary.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return MonthlySummary.from_mongo(doc) if doc else None

    async def get_by_user(
        self, user_id: str, limit: int = 12,
    ) -> list[MonthlySummary]:
        cursor = self._db.monthly_summary.find(
            {"user_id": to_object_id(user_id)}
        ).sort("period", -1).limit(limit)
        return [MonthlySummary.from_mongo(doc) async for doc in cursor]
