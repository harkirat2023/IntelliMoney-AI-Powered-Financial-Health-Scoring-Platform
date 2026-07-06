from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_intelligence import BudgetIntelligence


class BudgetIntelligenceRepository(ABC):
    @abstractmethod
    async def upsert(self, intelligence: BudgetIntelligence) -> BudgetIntelligence: ...

    @abstractmethod
    async def get_by_user_and_period(self, user_id: str, period: str) -> BudgetIntelligence | None: ...

    @abstractmethod
    async def get_latest(self, user_id: str) -> BudgetIntelligence | None: ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 12) -> list[BudgetIntelligence]: ...


class MongoBudgetIntelligenceRepository(BudgetIntelligenceRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.budget_intelligence

    async def upsert(self, intelligence: BudgetIntelligence) -> BudgetIntelligence:
        doc = intelligence.to_mongo()
        doc["calculated_at"] = datetime.utcnow()
        result = await self._collection.find_one_and_update(
            {"user_id": intelligence.user_id, "period": intelligence.period},
            {"$set": doc},
            upsert=True,
            return_document=True,
        )
        return BudgetIntelligence.from_mongo(result)

    async def get_by_user_and_period(self, user_id: str, period: str) -> BudgetIntelligence | None:
        doc = await self._collection.find_one({"user_id": user_id, "period": period})
        return BudgetIntelligence.from_mongo(doc) if doc else None

    async def get_latest(self, user_id: str) -> BudgetIntelligence | None:
        cursor = self._collection.find({"user_id": user_id}).sort("calculated_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return BudgetIntelligence.from_mongo(docs[0]) if docs else None

    async def get_by_user(self, user_id: str, limit: int = 12) -> list[BudgetIntelligence]:
        cursor = self._collection.find({"user_id": user_id}).sort("calculated_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [BudgetIntelligence.from_mongo(d) for d in docs]
