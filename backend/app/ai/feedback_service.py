from app.domain.financial_transactions.models import FinancialTransaction
from app.infrastructure.database.repositories.intelligence.feedback_repository import (
    MongoFeedbackRepository,
)
from app.infrastructure.messaging.event_bus import EventBus
from app.infrastructure.messaging.events import Event


class FeedbackLearningService:
    def __init__(
        self,
        feedback_repo: MongoFeedbackRepository,
        event_bus: EventBus,
    ):
        self._feedback_repo = feedback_repo
        self._event_bus = event_bus

    async def record_category_feedback(
        self,
        user_id: str,
        tx: FinancialTransaction,
        user_category: str,
        feedback_type: str = "category",
    ) -> dict:
        feedback = await self._feedback_repo.create_category_feedback(
            user_id=user_id,
            financial_tx_id=tx.id,
            original_description=tx.original_description,
            original_merchant=tx.normalized_merchant,
            suggested_category=tx.assigned_category,
            user_category=user_category,
            feedback_type=feedback_type,
        )
        await self._event_bus.publish(Event(
            event_type="ai.feedback.recorded",
            user_id=user_id,
            payload={
                "tx_id": tx.id,
                "feedback_type": feedback_type,
                "original_category": tx.assigned_category,
                "user_category": user_category,
            },
        ))
        return {"_id": str(feedback.get("_id", ""))}

    async def record_merchant_feedback(
        self,
        user_id: str,
        tx: FinancialTransaction,
        user_merchant: str,
    ) -> dict:
        return await self.record_category_feedback(
            user_id=user_id,
            tx=tx,
            user_category=user_merchant,
            feedback_type="merchant",
        )
