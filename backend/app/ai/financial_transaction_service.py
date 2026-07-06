from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.category_service import CategoryPredictionService
from app.ai.confidence_service import ConfidenceService
from app.ai.feedback_service import FeedbackLearningService
from app.ai.income_service import IncomeDetectionService
from app.ai.merchant_service import MerchantNormalizationService
from app.ai.pipeline import ProcessingPipeline
from app.ai.recurring_service import RecurringDetectionService
from app.ai.validation_service import ValidationService
from app.core.exceptions import (
    FinancialTransactionNotFoundException,
    ForbiddenException,
    InvalidReviewStateException,
)
from app.core.logging import logger
from app.domain.financial_transactions.models import FinancialTransaction
from app.domain.financial_transactions.repository import FinancialTransactionRepository
from app.domain.sync.models import BankTransaction
from app.domain.sync.repository import BankTransactionRepository
from app.infrastructure.database.repositories.intelligence.feedback_repository import (
    MongoFeedbackRepository,
)
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.infrastructure.database.repositories.intelligence.merchant_repository import (
    MongoMerchantRepository,
)
from app.infrastructure.messaging.event_bus import EventBus
from app.infrastructure.messaging.events import Event
from app.schemas.ai import (
    FeedbackResponse,
    IntelligenceStatusResponse,
    ProcessResultResponse,
    ReviewQueueItem,
    ReviewQueueResponse,
    ReviewSubmissionRequest,
)
from app.schemas.financial_transactions import FinancialTransactionResponse
from app.utils.date_utils import utc_now


class FinancialTransactionService:
    def __init__(
        self,
        bank_tx_repo: BankTransactionRepository,
        financial_tx_repo: MongoFinancialTransactionRepository,
        feedback_repo: MongoFeedbackRepository,
        db: AsyncIOMotorDatabase,
        pipeline: ProcessingPipeline,
        feedback_service: FeedbackLearningService,
        event_bus: EventBus,
    ):
        self._bank_tx_repo = bank_tx_repo
        self._financial_tx_repo = financial_tx_repo
        self._feedback_repo = feedback_repo
        self._db = db
        self._pipeline = pipeline
        self._feedback_service = feedback_service
        self._event_bus = event_bus

    async def process_pending(
        self, user_id: str, bank_account_id: str | None = None, limit: int = 100
    ) -> ProcessResultResponse:
        if bank_account_id:
            bank_txs = await self._bank_tx_repo.find_by_account(
                user_id, bank_account_id, limit=limit, offset=0,
            )
        else:
            bank_txs = await self._bank_tx_repo.find_by_user(
                user_id, limit=limit, offset=0,
            )

        if not bank_txs:
            return ProcessResultResponse(total_available=0, processed=0, skipped=0, failed=0)

        unprocessed_ids = await self._financial_tx_repo.find_unprocessed_bank_tx_ids(
            user_id, [tx.id for tx in bank_txs if tx.id],
        )

        txs_to_process = [tx for tx in bank_txs if tx.id in unprocessed_ids]

        if not txs_to_process:
            return ProcessResultResponse(
                total_available=len(bank_txs),
                processed=0,
                skipped=len(bank_txs),
                failed=0,
                message="All bank transactions already processed",
            )

        result = await self._pipeline.process_batch(txs_to_process)

        await self._event_bus.publish(Event(
            event_type="ai.pipeline.completed",
            user_id=user_id,
            payload={
                "processed_count": result["processed"],
                "failed_count": result["failed"],
                "bank_account_id": bank_account_id,
            },
        ))

        logger.info("AI pipeline completed", extra={
            "user_id": user_id,
            "bank_account_id": bank_account_id,
            "total": result["total"],
            "processed": result["processed"],
            "failed": result["failed"],
        })

        return ProcessResultResponse(
            total_available=len(bank_txs),
            processed=result["processed"],
            skipped=result["skipped"],
            failed=result["failed"],
        )

    async def get_review_queue(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> ReviewQueueResponse:
        txs = await self._financial_tx_repo.find_by_review_status(
            user_id, "review_required", limit, offset,
        )
        total = await self._financial_tx_repo.count_by_review_status(user_id, "review_required")

        items = [
            ReviewQueueItem(
                id=tx.id,
                original_description=tx.original_description,
                cleaned_merchant=tx.cleaned_merchant,
                amount=tx.amount,
                transaction_date=tx.transaction_date,
                assigned_category=tx.assigned_category,
                confidence_score=tx.confidence_score,
                is_income=tx.is_income,
                is_recurring=tx.is_recurring,
            )
            for tx in txs
        ]

        return ReviewQueueResponse(items=items, total=total, limit=limit, offset=offset)

    async def submit_review(
        self, user_id: str, tx_id: str, review: ReviewSubmissionRequest,
    ) -> FinancialTransaction:
        tx = await self._financial_tx_repo.get_by_id(tx_id)
        if not tx:
            raise FinancialTransactionNotFoundException()
        if tx.user_id != user_id:
            raise ForbiddenException("You do not own this financial transaction")

        now = utc_now()
        updated = await self._financial_tx_repo.atomic_review_update(
            tx_id=tx_id,
            expected_review_status="review_required",
            review_status=review.review_status,
            reviewed_by=user_id,
            reviewed_at=now,
            review_note=review.review_note,
            assigned_category=review.assigned_category,
        )

        if not updated:
            tx = await self._financial_tx_repo.get_by_id(tx_id)
            if tx and tx.review_status != "review_required":
                raise InvalidReviewStateException()
            raise FinancialTransactionNotFoundException()

        if review.assigned_category and review.assigned_category != tx.assigned_category:
            await self._feedback_service.record_category_feedback(
                user_id=user_id, tx=tx, user_category=review.assigned_category,
            )

        await self._event_bus.publish(Event(
            event_type="ai.review.submitted",
            user_id=user_id,
            payload={
                "tx_id": tx_id,
                "review_status": review.review_status,
                "assigned_category": review.assigned_category or tx.assigned_category,
            },
        ))

        return updated

    async def update_transaction(
        self, user_id: str, tx_id: str, update_data: dict,
    ) -> FinancialTransaction:
        tx = await self.get_transaction(user_id, tx_id)
        updated = await self._financial_tx_repo.update_fields(tx_id, update_data)
        if not updated:
            raise FinancialTransactionNotFoundException()
        return updated

    async def record_feedback(
        self, user_id: str, tx_id: str,
        user_category: str | None = None,
        feedback_type: str = "category",
    ) -> str:
        tx = await self.get_transaction(user_id, tx_id)
        feedback = await self._feedback_service.record_category_feedback(
            user_id=user_id,
            tx=tx,
            user_category=user_category or tx.assigned_category,
            feedback_type=feedback_type,
        )
        return str(feedback.get("_id", ""))

    async def get_transaction(
        self, user_id: str, tx_id: str,
    ) -> FinancialTransaction:
        tx = await self._financial_tx_repo.get_by_id(tx_id)
        if not tx:
            raise FinancialTransactionNotFoundException()
        if tx.user_id != user_id:
            raise ForbiddenException("You do not own this financial transaction")
        return tx

    async def list_transactions(
        self, user_id: str, limit: int = 50, offset: int = 0,
        category: str | None = None,
    ) -> list[FinancialTransaction]:
        if category:
            return await self._financial_tx_repo.find_by_user_and_category(
                user_id, category, limit, offset,
            )
        return await self._financial_tx_repo.find_by_user(user_id, limit, offset)

    async def get_status(self, user_id: str) -> IntelligenceStatusResponse:
        total = await self._financial_tx_repo.count_by_user(user_id)
        review_queue = await self._financial_tx_repo.count_by_review_status(
            user_id, "review_required",
        )
        return IntelligenceStatusResponse(
            is_healthy=True,
            pending_transactions=0,
            total_processed_all_time=total,
            total_in_review_queue=review_queue,
        )
