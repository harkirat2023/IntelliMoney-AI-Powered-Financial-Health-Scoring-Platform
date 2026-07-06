from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.models.health_history import HealthHistory
from app.utils.object_id import to_object_id


class HealthHistoryRepository(ABC):
    @abstractmethod
    async def create(self, entry: HealthHistory) -> HealthHistory:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 36) -> list[HealthHistory]:
        ...

    @abstractmethod
    async def get_by_period(self, user_id: str, period: str) -> HealthHistory | None:
        ...


class MongoHealthHistoryRepository(HealthHistoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, entry: HealthHistory) -> HealthHistory:
        doc = entry.to_mongo()
        await self._db.financial_health_history.insert_one(doc)
        entry.id = str(doc["_id"])
        return entry

    async def get_by_user(self, user_id: str, limit: int = 36) -> list[HealthHistory]:
        cursor = self._db.financial_health_history.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(limit)
        return [HealthHistory.from_mongo(doc) async for doc in cursor]

    async def get_by_period(self, user_id: str, period: str) -> HealthHistory | None:
        doc = await self._db.financial_health_history.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return HealthHistory.from_mongo(doc) if doc else None
