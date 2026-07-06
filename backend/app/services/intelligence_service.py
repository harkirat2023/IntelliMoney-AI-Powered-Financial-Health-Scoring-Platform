from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.category_service import CategoryPredictionService
from app.ai.confidence_service import ConfidenceService
from app.ai.feedback_service import FeedbackLearningService
from app.ai.financial_transaction_service import FinancialTransactionService
from app.ai.income_service import IncomeDetectionService
from app.ai.merchant_service import MerchantNormalizationService
from app.ai.pipeline import ProcessingPipeline
from app.ai.recurring_service import RecurringDetectionService
from app.ai.validation_service import ValidationService
from app.infrastructure.database.repositories.intelligence.feedback_repository import (
    MongoFeedbackRepository,
)
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.infrastructure.database.repositories.intelligence.merchant_repository import (
    MongoMerchantRepository,
)
from app.infrastructure.database.repositories.sync_repository import (
    MongoBankTransactionRepository,
)
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus


_service_instance: FinancialTransactionService | None = None


def get_intelligence_service(
    db: AsyncIOMotorDatabase,
) -> FinancialTransactionService:
    global _service_instance
    if _service_instance is not None:
        return _service_instance

    bank_tx_repo = MongoBankTransactionRepository(db)
    financial_tx_repo = MongoFinancialTransactionRepository(db)
    feedback_repo = MongoFeedbackRepository(db)
    merchant_repo = MongoMerchantRepository(db)

    merchant_service = MerchantNormalizationService()
    category_service = CategoryPredictionService()
    confidence_service = ConfidenceService()
    recurring_service = RecurringDetectionService()
    income_service = IncomeDetectionService()
    validation_service = ValidationService()

    feedback_service = FeedbackLearningService(feedback_repo, global_event_bus)

    pipeline = ProcessingPipeline(
        merchant_service=merchant_service,
        category_service=category_service,
        confidence_service=confidence_service,
        recurring_service=recurring_service,
        income_service=income_service,
        validation_service=validation_service,
        financial_tx_repo=financial_tx_repo,
        event_bus=global_event_bus,
    )

    service = FinancialTransactionService(
        bank_tx_repo=bank_tx_repo,
        financial_tx_repo=financial_tx_repo,
        feedback_repo=feedback_repo,
        db=db,
        pipeline=pipeline,
        feedback_service=feedback_service,
        event_bus=global_event_bus,
    )

    _service_instance = service
    return service
