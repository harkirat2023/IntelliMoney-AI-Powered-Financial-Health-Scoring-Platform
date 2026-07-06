from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.cash_flow_summary import CashFlowSummary
from app.utils.object_id import to_object_id


class CashFlowRepository(ABC):
    @abstractmethod
    async def upsert(self, summary: CashFlowSummary) -> CashFlowSummary:
        ...

    @abstractmethod
    async def get_by_user_and_month(
        self, user_id: str, year: int, month: int,
    ) -> CashFlowSummary | None:
        ...

    @abstractmethod
    async def get_range(
        self, user_id: str, from_date: datetime, to_date: datetime,
    ) -> list[CashFlowSummary]:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 12) -> list[CashFlowSummary]:
        ...


class MongoCashFlowRepository(CashFlowRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, summary: CashFlowSummary) -> CashFlowSummary:
        doc = summary.to_mongo()
        filter_key = {"user_id": doc["user_id"], "year": summary.year, "month": summary.month}
        await self._db.cash_flow_summary.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.cash_flow_summary.find_one(filter_key)
        return CashFlowSummary.from_mongo(result) if result else summary

    async def get_by_user_and_month(
        self, user_id: str, year: int, month: int,
    ) -> CashFlowSummary | None:
        doc = await self._db.cash_flow_summary.find_one(
            {"user_id": to_object_id(user_id), "year": year, "month": month}
        )
        return CashFlowSummary.from_mongo(doc) if doc else None

    async def get_range(
        self, user_id: str, from_date: datetime, to_date: datetime,
    ) -> list[CashFlowSummary]:
        cursor = self._db.cash_flow_summary.find(
            {
                "user_id": to_object_id(user_id),
                "$or": [
                    {"year": {"$gt": from_date.year}},
                    {"year": from_date.year, "month": {"$gte": from_date.month}},
                ],
            }
        ).sort("year", -1).sort("month", -1)
        return [CashFlowSummary.from_mongo(doc) async for doc in cursor]

    async def get_by_user(self, user_id: str, limit: int = 12) -> list[CashFlowSummary]:
        cursor = self._db.cash_flow_summary.find(
            {"user_id": to_object_id(user_id)}
        ).sort("year", -1).sort("month", -1).limit(limit)
        return [CashFlowSummary.from_mongo(doc) async for doc in cursor]
