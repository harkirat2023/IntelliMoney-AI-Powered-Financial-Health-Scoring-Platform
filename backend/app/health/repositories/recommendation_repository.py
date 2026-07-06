from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.models.health_recommendation import HealthRecommendation
from app.utils.object_id import to_object_id


class RecommendationRepository(ABC):
    @abstractmethod
    async def create(self, rec: HealthRecommendation) -> HealthRecommendation:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 20) -> list[HealthRecommendation]:
        ...

    @abstractmethod
    async def dismiss(self, rec_id: str, user_id: str) -> bool:
        ...

    @abstractmethod
    async def delete_old(self, user_id: str, keep_count: int = 50) -> int:
        ...


class MongoRecommendationRepository(RecommendationRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, rec: HealthRecommendation) -> HealthRecommendation:
        doc = rec.to_mongo()
        await self._db.health_recommendations.insert_one(doc)
        rec.id = str(doc["_id"])
        return rec

    async def get_by_user(self, user_id: str, limit: int = 20) -> list[HealthRecommendation]:
        cursor = self._db.health_recommendations.find(
            {"user_id": to_object_id(user_id), "dismissed": False}
        ).sort("priority", 1).sort("created_at", -1).limit(limit)
        return [HealthRecommendation.from_mongo(doc) async for doc in cursor]

    async def dismiss(self, rec_id: str, user_id: str) -> bool:
        result = await self._db.health_recommendations.update_one(
            {"_id": to_object_id(rec_id), "user_id": to_object_id(user_id)},
            {"$set": {"dismissed": True}},
        )
        return result.modified_count > 0

    async def delete_old(self, user_id: str, keep_count: int = 50) -> int:
        cursor = self._db.health_recommendations.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).skip(keep_count)
        ids = [doc["_id"] async for doc in cursor]
        if not ids:
            return 0
        result = await self._db.health_recommendations.delete_many(
            {"_id": {"$in": ids}}
        )
        return result.deleted_count
