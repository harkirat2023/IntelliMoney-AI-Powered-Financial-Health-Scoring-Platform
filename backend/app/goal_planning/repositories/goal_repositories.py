from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import (
    FinancialGoal, GoalNotification, GoalPrediction,
    GoalProgress, GoalRecommendation,
)


class FinancialGoalRepository(ABC):
    @abstractmethod
    async def create(self, goal: FinancialGoal) -> FinancialGoal: ...
    @abstractmethod
    async def get_by_id(self, goal_id: str) -> FinancialGoal | None: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, status: str | None = None) -> list[FinancialGoal]: ...
    @abstractmethod
    async def update(self, goal_id: str, data: dict) -> bool: ...
    @abstractmethod
    async def delete(self, goal_id: str) -> bool: ...
    @abstractmethod
    async def get_active(self, user_id: str) -> list[FinancialGoal]: ...


class GoalProgressRepository(ABC):
    @abstractmethod
    async def create(self, progress: GoalProgress) -> GoalProgress: ...
    @abstractmethod
    async def get_by_goal(self, goal_id: str, limit: int = 12) -> list[GoalProgress]: ...
    @abstractmethod
    async def get_latest_by_goal(self, goal_id: str) -> GoalProgress | None: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[GoalProgress]: ...
    @abstractmethod
    async def get_by_goal_and_period(self, goal_id: str, period: str) -> GoalProgress | None: ...


class GoalRecommendationRepository(ABC):
    @abstractmethod
    async def create(self, rec: GoalRecommendation) -> GoalRecommendation: ...
    @abstractmethod
    async def bulk_create(self, recs: list[GoalRecommendation]) -> int: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, dismissed: bool | None = False) -> list[GoalRecommendation]: ...
    @abstractmethod
    async def dismiss(self, rec_id: str) -> bool: ...
    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int: ...


class GoalPredictionRepository(ABC):
    @abstractmethod
    async def upsert(self, prediction: GoalPrediction) -> GoalPrediction: ...
    @abstractmethod
    async def get_by_goal(self, goal_id: str) -> GoalPrediction | None: ...
    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[GoalPrediction]: ...


class GoalNotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification: GoalNotification) -> GoalNotification: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[GoalNotification]: ...
    @abstractmethod
    async def mark_read(self, notification_id: str) -> bool: ...
    @abstractmethod
    async def mark_all_read(self, user_id: str) -> int: ...
    @abstractmethod
    async def delete_old(self, user_id: str, before: datetime) -> int: ...


class MongoFinancialGoalRepository(FinancialGoalRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.financial_goals

    async def create(self, goal: FinancialGoal) -> FinancialGoal:
        doc = goal.to_mongo()
        doc["created_at"] = doc["updated_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        goal.id = str(r.inserted_id)
        return goal

    async def get_by_id(self, goal_id: str) -> FinancialGoal | None:
        d = await self._collection.find_one({"_id": goal_id})
        return FinancialGoal.from_mongo(d) if d else None

    async def get_by_user(self, user_id: str, status: str | None = None) -> list[FinancialGoal]:
        q = {"user_id": user_id}
        if status:
            q["status"] = status
        cursor = self._collection.find(q).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [FinancialGoal.from_mongo(d) for d in docs]

    async def update(self, goal_id: str, data: dict) -> bool:
        data["updated_at"] = datetime.utcnow()
        r = await self._collection.update_one({"_id": goal_id}, {"$set": data})
        return r.modified_count > 0

    async def delete(self, goal_id: str) -> bool:
        r = await self._collection.delete_one({"_id": goal_id})
        return r.deleted_count > 0

    async def get_active(self, user_id: str) -> list[FinancialGoal]:
        cursor = self._collection.find(
            {"user_id": user_id, "status": {"$in": ["active", "on_track", "at_risk"]}}
        ).sort("priority", 1)
        docs = await cursor.to_list(length=50)
        return [FinancialGoal.from_mongo(d) for d in docs]


class MongoGoalProgressRepository(GoalProgressRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.goal_progress

    async def create(self, progress: GoalProgress) -> GoalProgress:
        doc = progress.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        progress.id = str(r.inserted_id)
        return progress

    async def get_by_goal(self, goal_id: str, limit: int = 12) -> list[GoalProgress]:
        cursor = self._collection.find({"goal_id": goal_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GoalProgress.from_mongo(d) for d in docs]

    async def get_latest_by_goal(self, goal_id: str) -> GoalProgress | None:
        cursor = self._collection.find({"goal_id": goal_id}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return GoalProgress.from_mongo(docs[0]) if docs else None

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[GoalProgress]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GoalProgress.from_mongo(d) for d in docs]

    async def get_by_goal_and_period(self, goal_id: str, period: str) -> GoalProgress | None:
        d = await self._collection.find_one({"goal_id": goal_id, "period": period})
        return GoalProgress.from_mongo(d) if d else None


class MongoGoalRecommendationRepository(GoalRecommendationRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.goal_recommendations

    async def create(self, rec: GoalRecommendation) -> GoalRecommendation:
        doc = rec.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        rec.id = str(r.inserted_id)
        return rec

    async def bulk_create(self, recs: list[GoalRecommendation]) -> int:
        if not recs:
            return 0
        docs = []
        for r in recs:
            d = r.to_mongo()
            d["created_at"] = datetime.utcnow()
            docs.append(d)
        result = await self._collection.insert_many(docs)
        return len(result.inserted_ids)

    async def get_by_user(self, user_id: str, dismissed: bool | None = False) -> list[GoalRecommendation]:
        q = {"user_id": user_id}
        if dismissed is not None:
            q["dismissed"] = dismissed
        cursor = self._collection.find(q).sort("priority", 1).sort("created_at", -1)
        docs = await cursor.to_list(length=50)
        return [GoalRecommendation.from_mongo(d) for d in docs]

    async def dismiss(self, rec_id: str) -> bool:
        r = await self._collection.update_one({"_id": rec_id}, {"$set": {"dismissed": True}})
        return r.modified_count > 0

    async def delete_by_user(self, user_id: str) -> int:
        r = await self._collection.delete_many({"user_id": user_id})
        return r.deleted_count


class MongoGoalPredictionRepository(GoalPredictionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.goal_predictions

    async def upsert(self, prediction: GoalPrediction) -> GoalPrediction:
        doc = prediction.to_mongo()
        doc["created_at"] = datetime.utcnow()
        await self._collection.update_one(
            {"goal_id": prediction.goal_id},
            {"$set": doc}, upsert=True)
        return prediction

    async def get_by_goal(self, goal_id: str) -> GoalPrediction | None:
        d = await self._collection.find_one({"goal_id": goal_id})
        return GoalPrediction.from_mongo(d) if d else None

    async def get_by_user(self, user_id: str) -> list[GoalPrediction]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=50)
        return [GoalPrediction.from_mongo(d) for d in docs]


class MongoGoalNotificationRepository(GoalNotificationRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.goal_notifications

    async def create(self, notification: GoalNotification) -> GoalNotification:
        doc = notification.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        notification.id = str(r.inserted_id)
        return notification

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[GoalNotification]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GoalNotification.from_mongo(d) for d in docs]

    async def mark_read(self, notification_id: str) -> bool:
        r = await self._collection.update_one({"_id": notification_id}, {"$set": {"read": True}})
        return r.modified_count > 0

    async def mark_all_read(self, user_id: str) -> int:
        r = await self._collection.update_many(
            {"user_id": user_id, "read": False}, {"$set": {"read": True}})
        return r.modified_count

    async def delete_old(self, user_id: str, before: datetime) -> int:
        r = await self._collection.delete_many({"user_id": user_id, "created_at": {"$lt": before}})
        return r.deleted_count
