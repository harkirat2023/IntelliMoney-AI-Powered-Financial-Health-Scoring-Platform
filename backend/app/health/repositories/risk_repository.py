from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.models.risk_profile import RiskProfile
from app.utils.object_id import to_object_id


class RiskRepository(ABC):
    @abstractmethod
    async def upsert(self, profile: RiskProfile) -> RiskProfile:
        ...

    @abstractmethod
    async def get_by_user_and_period(self, user_id: str, period: str) -> RiskProfile | None:
        ...

    @abstractmethod
    async def get_latest(self, user_id: str) -> RiskProfile | None:
        ...


class MongoRiskRepository(RiskRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, profile: RiskProfile) -> RiskProfile:
        doc = profile.to_mongo()
        filter_key = {"user_id": doc["user_id"], "period": profile.period}
        await self._db.financial_risk_profile.update_one(filter_key, {"$set": doc}, upsert=True)
        result = await self._db.financial_risk_profile.find_one(filter_key)
        return RiskProfile.from_mongo(result) if result else profile

    async def get_by_user_and_period(self, user_id: str, period: str) -> RiskProfile | None:
        doc = await self._db.financial_risk_profile.find_one(
            {"user_id": to_object_id(user_id), "period": period}
        )
        return RiskProfile.from_mongo(doc) if doc else None

    async def get_latest(self, user_id: str) -> RiskProfile | None:
        cursor = self._db.financial_risk_profile.find(
            {"user_id": to_object_id(user_id)}
        ).sort("calculated_at", -1).limit(1)
        docs = [doc async for doc in cursor]
        return RiskProfile.from_mongo(docs[0]) if docs else None
