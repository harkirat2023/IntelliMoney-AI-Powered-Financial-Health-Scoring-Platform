from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.models.financial_health import FinancialHealth
from app.utils.object_id import to_object_id


class FinancialHealthRepository(ABC):
    @abstractmethod
    async def upsert(self, health: FinancialHealth) -> FinancialHealth:
        ...

    @abstractmethod
    async def get_by_user_and_period(self, user_id: str, period: str) -> FinancialHealth | None:
        ...

    @abstractmethod
    async def get_latest(self, user_id: str) -> FinancialHealth | None:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 12) -> list[FinancialHealth]:
        ...


class MongoFinancialHealthRepository(FinancialHealthRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, health: FinancialHealth) -> FinancialHealth:
        doc = health.to_mongo()
        filter_key = {"user_id": doc["user_id"], "period": health.period}
        await self._db.financial_health.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.financial_health.find_one(filter_key)
        return FinancialHealth.from_mongo(result) if result else health

    async def get_by_user_and_period(self, user_id: str, period: str) -> FinancialHealth | None:
        doc = await self._db.financial_health.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return FinancialHealth.from_mongo(doc) if doc else None

    async def get_latest(self, user_id: str) -> FinancialHealth | None:
        cursor = self._db.financial_health.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(1)
        docs = [doc async for doc in cursor]
        return FinancialHealth.from_mongo(docs[0]) if docs else None

    async def get_by_user(self, user_id: str, limit: int = 12) -> list[FinancialHealth]:
        cursor = self._db.financial_health.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(limit)
        return [FinancialHealth.from_mongo(doc) async for doc in cursor]
