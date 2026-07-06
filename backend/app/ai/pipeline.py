import asyncio
from datetime import datetime
from typing import Any

from app.ai.category_service import CategoryPredictionService
from app.ai.confidence_service import ConfidenceService
from app.ai.income_service import IncomeDetectionService
from app.ai.merchant_service import MerchantNormalizationService
from app.ai.recurring_service import RecurringDetectionService
from app.ai.validation_service import ValidationService
from app.core.constants import CATEGORIES
from app.core.logging import logger
from app.domain.financial_transactions.models import FinancialTransaction
from app.domain.sync.models import BankTransaction
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.infrastructure.messaging.event_bus import EventBus
from app.infrastructure.messaging.events import Event
from app.utils.date_utils import utc_now


class ProcessingPipeline:
    def __init__(
        self,
        merchant_service: MerchantNormalizationService,
        category_service: CategoryPredictionService,
        confidence_service: ConfidenceService,
        recurring_service: RecurringDetectionService,
        income_service: IncomeDetectionService,
        validation_service: ValidationService,
        financial_tx_repo: MongoFinancialTransactionRepository,
        event_bus: EventBus,
    ):
        self._merchant_service = merchant_service
        self._category_service = category_service
        self._confidence_service = confidence_service
        self._recurring_service = recurring_service
        self._income_service = income_service
        self._validation_service = validation_service
        self._financial_tx_repo = financial_tx_repo
        self._event_bus = event_bus

    async def process_transaction(self, bank_tx: BankTransaction) -> FinancialTransaction | None:
        try:
            self._validation_service.validate_bank_transaction(bank_tx.model_dump())
        except Exception as e:
            logger.warning("Validation failed for bank transaction", extra={
                "bank_tx_id": bank_tx.id, "error": str(e),
            })
            return None

        merchant_result = self._merchant_service.normalize(bank_tx.description)

        income_result = self._income_service.classify(
            bank_tx.transaction_type, bank_tx.description,
        )

        merchant_category = merchant_result.category
        merchant_confidence = merchant_result.confidence

        ml_category, ml_confidence = self._category_service.predict(
            bank_tx.description, merchant_category,
        )

        assigned_category = merchant_category if (
            merchant_category and merchant_confidence >= 0.85
        ) else ml_category
        if assigned_category not in CATEGORIES:
            assigned_category = "Other"

        is_recurring, recurring_tags = self._recurring_service.detect(
            merchant_result.normalized_merchant,
            bank_tx.amount,
            bank_tx.description,
        )

        keyword_confidence = self._category_service.get_keyword_confidence(
            bank_tx.description, assigned_category,
        )

        confidence_result = self._confidence_service.calculate(
            merchant_confidence=merchant_confidence,
            merchant_category=merchant_category,
            ml_confidence=ml_confidence,
            ml_category=ml_category,
            is_recurring=is_recurring,
            keyword_confidence=keyword_confidence,
        )

        review_status = self._confidence_service.determine_review_status(
            confidence_result["score"],
        )

        all_tags = list(set(
            income_result["tags"] + recurring_tags
        ))

        now = utc_now()
        financial_tx = FinancialTransaction(
            user_id=bank_tx.user_id,
            bank_account_id=bank_tx.bank_account_id,
            bank_transaction_id=bank_tx.id,
            sync_log_id=bank_tx.sync_log_id,
            provider_account_id=bank_tx.provider_account_id,
            transaction_id=bank_tx.transaction_id,
            original_description=bank_tx.description,
            amount=bank_tx.amount,
            transaction_type=bank_tx.transaction_type,
            transaction_date=bank_tx.transaction_date,
            original_category=bank_tx.category,
            reference=bank_tx.reference,
            cleaned_merchant=merchant_result.cleaned_merchant,
            normalized_merchant=merchant_result.normalized_merchant,
            merchant_id=merchant_result.merchant_id,
            assigned_category=assigned_category,
            confidence_score=confidence_result["score"],
            is_income=income_result["is_income"],
            is_recurring=is_recurring,
            transaction_tags=all_tags,
            is_refund=income_result["is_refund"],
            is_transfer=income_result["is_transfer"],
            review_status=review_status,
            processed_at=now,
            created_at=now,
            updated_at=now,
        )

        return financial_tx

    async def process_batch(
        self, bank_txs: list[BankTransaction]
    ) -> dict[str, Any]:
        failures = []

        async def safe_process(bank_tx):
            try:
                result = await self.process_transaction(bank_tx)
                if result:
                    return result
                failures.append({"bank_tx_id": bank_tx.id, "error": "Validation failed"})
            except Exception as e:
                logger.error("Pipeline processing error", extra={
                    "bank_tx_id": bank_tx.id, "error": str(e),
                })
                failures.append({"bank_tx_id": bank_tx.id, "error": str(e)})
            return None

        sem = asyncio.Semaphore(10)
        async def throttled_process(bank_tx):
            async with sem:
                return await safe_process(bank_tx)

        tasks = [throttled_process(tx) for tx in bank_txs]
        results = await asyncio.gather(*tasks)
        successes = [r for r in results if r is not None]

        inserted = 0
        if successes:
            inserted = await self._financial_tx_repo.bulk_create(successes)

        return {
            "total": len(bank_txs),
            "processed": inserted,
            "skipped": len(bank_txs) - len(successes),
            "failed": len(failures),
            "success_ids": [tx.id for tx in successes],
            "failures": failures,
        }
