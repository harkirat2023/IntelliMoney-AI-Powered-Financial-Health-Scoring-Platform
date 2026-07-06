from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_prediction import BudgetPrediction


class BudgetPredictionRepository(ABC):
    @abstractmethod
    async def upsert(self, prediction: BudgetPrediction) -> BudgetPrediction: ...

    @abstractmethod
    async def get_by_user_and_period(self, user_id: str, period: str) -> list[BudgetPrediction]: ...

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[BudgetPrediction]: ...

    @abstractmethod
    async def delete_old(self, user_id: str, keep_months: int = 12) -> int: ...


class MongoBudgetPredictionRepository(BudgetPredictionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.budget_predictions

    async def upsert(self, prediction: BudgetPrediction) -> BudgetPrediction:
        doc = prediction.to_mongo()
        doc["calculated_at"] = datetime.utcnow()
        result = await self._collection.find_one_and_update(
            {"user_id": prediction.user_id, "period": prediction.period, "category": prediction.category},
            {"$set": doc},
            upsert=True,
            return_document=True,
        )
        return BudgetPrediction.from_mongo(result)

    async def bulk_upsert(self, predictions: list[BudgetPrediction]) -> list[BudgetPrediction]:
        for p in predictions:
            await self.upsert(p)
        return predictions

    async def get_by_user_and_period(self, user_id: str, period: str) -> list[BudgetPrediction]:
        cursor = self._collection.find({"user_id": user_id, "period": period})
        docs = await cursor.to_list(length=None)
        return [BudgetPrediction.from_mongo(d) for d in docs]

    async def get_by_user(self, user_id: str) -> list[BudgetPrediction]:
        cursor = self._collection.find({"user_id": user_id}).sort("calculated_at", -1)
        docs = await cursor.to_list(length=None)
        return [BudgetPrediction.from_mongo(d) for d in docs]

    async def delete_old(self, user_id: str, keep_months: int = 12) -> int:
        cursor = self._collection.find({"user_id": user_id}).sort("period", -1)
        all_docs = await cursor.to_list(length=None)
        if len(all_docs) <= keep_months:
            return 0
        to_delete = all_docs[keep_months:]
        ids = [d["_id"] for d in to_delete]
        result = await self._collection.delete_many({"_id": {"$in": ids}})
        return result.deleted_count
