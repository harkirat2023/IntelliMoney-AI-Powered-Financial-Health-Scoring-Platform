from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class MongoFeedbackRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create_category_feedback(
        self, user_id: str, financial_tx_id: str,
        original_description: str, original_merchant: str,
        suggested_category: str, user_category: str,
        feedback_type: str = "category",
    ) -> dict:
        doc = {
            "user_id": to_object_id(user_id),
            "financial_transaction_id": to_object_id(financial_tx_id),
            "original_description": original_description,
            "original_merchant": original_merchant,
            "suggested_category": suggested_category,
            "user_category": user_category,
            "feedback_type": feedback_type,
            "created_at": utc_now(),
        }
        result = await self._db.category_feedback.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def count_by_user(self, user_id: str) -> int:
        return await self._db.category_feedback.count_documents(
            {"user_id": to_object_id(user_id)},
        )
