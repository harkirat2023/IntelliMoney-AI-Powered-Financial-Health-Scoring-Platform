from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_risk import BudgetRisk


class BudgetRiskRepository(ABC):
    @abstractmethod
    async def upsert(self, risk: BudgetRisk) -> BudgetRisk: ...

    @abstractmethod
    async def get_by_user_and_period(self, user_id: str, period: str) -> BudgetRisk | None: ...

    @abstractmethod
    async def get_latest(self, user_id: str) -> BudgetRisk | None: ...


class MongoBudgetRiskRepository(BudgetRiskRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.budget_risk

    async def upsert(self, risk: BudgetRisk) -> BudgetRisk:
        doc = risk.to_mongo()
        doc["calculated_at"] = datetime.utcnow()
        result = await self._collection.find_one_and_update(
            {"user_id": risk.user_id, "period": risk.period},
            {"$set": doc},
            upsert=True,
            return_document=True,
        )
        return BudgetRisk.from_mongo(result)

    async def get_by_user_and_period(self, user_id: str, period: str) -> BudgetRisk | None:
        doc = await self._collection.find_one({"user_id": user_id, "period": period})
        return BudgetRisk.from_mongo(doc) if doc else None

    async def get_latest(self, user_id: str) -> BudgetRisk | None:
        cursor = self._collection.find({"user_id": user_id}).sort("calculated_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return BudgetRisk.from_mongo(docs[0]) if docs else None
