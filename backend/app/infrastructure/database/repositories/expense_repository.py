from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.expenses.models import Expense
from app.domain.expenses.repository import ExpenseRepository
from app.utils.object_id import to_object_id


class MongoExpenseRepository(ExpenseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def get_by_id(self, expense_id: str) -> Expense | None:
        doc = await self._db.expenses.find_one({"_id": to_object_id(expense_id)})
        return Expense.from_mongo(doc) if doc else None

    async def get_by_user(
        self, user_id: str, category: str | None = None,
        payment_method: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Expense]:
        query: dict = {"user_id": to_object_id(user_id)}
        if category:
            query["category"] = category
        if payment_method:
            query["payment_method"] = payment_method
        if date_from or date_to:
            date_query: dict = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["date"] = date_query
        cursor = self._db.expenses.find(query).sort("date", -1)
        return [Expense.from_mongo(doc) async for doc in cursor]

    async def create(self, expense: Expense) -> Expense:
        doc = expense.to_mongo()
        result = await self._db.expenses.insert_one(doc)
        expense.id = str(result.inserted_id)
        return expense

    async def update(self, expense_id: str, data: dict) -> Expense | None:
        result = await self._db.expenses.update_one(
            {"_id": to_object_id(expense_id)}, {"$set": data}
        )
        if result.modified_count == 0:
            return None
        return await self.get_by_id(expense_id)

    async def delete(self, expense_id: str) -> bool:
        result = await self._db.expenses.delete_one(
            {"_id": to_object_id(expense_id)}
        )
        return result.deleted_count > 0
