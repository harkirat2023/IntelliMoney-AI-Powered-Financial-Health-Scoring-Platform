from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_recommendation import BudgetRecommendation


class BudgetRecommendationRepository(ABC):
    @abstractmethod
    async def create(self, rec: BudgetRecommendation) -> BudgetRecommendation: ...

    @abstractmethod
    async def bulk_create(self, recs: list[BudgetRecommendation]) -> list[BudgetRecommendation]: ...

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[BudgetRecommendation]: ...

    @abstractmethod
    async def get_active(self, user_id: str) -> list[BudgetRecommendation]: ...

    @abstractmethod
    async def dismiss(self, user_id: str, rec_id: str) -> bool: ...

    @abstractmethod
    async def delete_old(self, user_id: str, keep: int = 50) -> int: ...


class MongoBudgetRecommendationRepository(BudgetRecommendationRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.budget_recommendations

    async def create(self, rec: BudgetRecommendation) -> BudgetRecommendation:
        doc = rec.to_mongo()
        doc["created_at"] = datetime.utcnow()
        result = await self._collection.insert_one(doc)
        rec.id = str(result.inserted_id)
        return rec

    async def bulk_create(self, recs: list[BudgetRecommendation]) -> list[BudgetRecommendation]:
        docs = []
        for rec in recs:
            doc = rec.to_mongo()
            doc["created_at"] = datetime.utcnow()
            docs.append(doc)
        if docs:
            await self._collection.insert_many(docs, ordered=False)
        return recs

    async def get_by_user(self, user_id: str) -> list[BudgetRecommendation]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [BudgetRecommendation.from_mongo(d) for d in docs]

    async def get_active(self, user_id: str) -> list[BudgetRecommendation]:
        cursor = self._collection.find({"user_id": user_id, "dismissed": False}).sort("priority", 1)
        docs = await cursor.to_list(length=None)
        return [BudgetRecommendation.from_mongo(d) for d in docs]

    async def dismiss(self, user_id: str, rec_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": rec_id, "user_id": user_id},
            {"$set": {"dismissed": True}},
        )
        return result.modified_count > 0

    async def delete_old(self, user_id: str, keep: int = 50) -> int:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).skip(keep)
        old_ids = [doc["_id"] for doc in await cursor.to_list(length=None)]
        if old_ids:
            result = await self._collection.delete_many({"_id": {"$in": old_ids}})
            return result.deleted_count
        return 0
