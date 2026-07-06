from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.budget_usage import BudgetUsage
from app.utils.object_id import to_object_id


class BudgetUsageRepository(ABC):
    @abstractmethod
    async def upsert(
        self, user_id: str, budget_id: str, month: int, year: int,
        limit: float, spent: float, remaining: float,
        percentage_used: float, state: str, category: str,
        updated_at,
    ) -> BudgetUsage:
        ...

    @abstractmethod
    async def get_by_user_and_period(
        self, user_id: str, month: int, year: int,
    ) -> list[BudgetUsage]:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[BudgetUsage]:
        ...


class MongoBudgetUsageRepository(BudgetUsageRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(
        self, user_id: str, budget_id: str, month: int, year: int,
        limit: float, spent: float, remaining: float,
        percentage_used: float, state: str, category: str,
        updated_at,
    ) -> BudgetUsage:
        doc = {
            "user_id": to_object_id(user_id),
            "budget_id": to_object_id(budget_id),
            "category": category,
            "month": month,
            "year": year,
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "state": state,
            "updated_at": updated_at,
        }
        await self._db.budget_usage.update_one(
            {"user_id": to_object_id(user_id), "budget_id": to_object_id(budget_id), "month": month, "year": year},
            {"$set": doc},
            upsert=True,
        )
        return BudgetUsage.from_mongo(doc)

    async def get_by_user_and_period(
        self, user_id: str, month: int, year: int,
    ) -> list[BudgetUsage]:
        cursor = self._db.budget_usage.find(
            {"user_id": to_object_id(user_id), "month": month, "year": year}
        )
        return [BudgetUsage.from_mongo(doc) async for doc in cursor]

    async def get_by_user(self, user_id: str) -> list[BudgetUsage]:
        cursor = self._db.budget_usage.find({"user_id": to_object_id(user_id)}).sort("year", -1).sort("month", -1)
        return [BudgetUsage.from_mongo(doc) async for doc in cursor]
