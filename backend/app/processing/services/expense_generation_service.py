import logging
from datetime import date

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.expenses.models import Expense

logger = logging.getLogger("intellimoney")
from app.domain.financial_transactions.models import FinancialTransaction
from app.infrastructure.database.repositories.expense_repository import MongoExpenseRepository
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.utils.date_utils import utc_now


class ExpenseGenerationService:
    def __init__(
        self,
        expense_repo: MongoExpenseRepository,
        financial_tx_repo: MongoFinancialTransactionRepository,
    ):
        self._expense_repo = expense_repo
        self._financial_tx_repo = financial_tx_repo

    async def generate_expenses(
        self, transactions: list[FinancialTransaction], force: bool = False,
    ) -> tuple[list[str], list[str], list[dict]]:
        created_ids: list[str] = []
        skipped_ids: list[str] = []
        errors: list[dict] = []

        for tx in transactions:
            if not self._qualifies(tx, force):
                skipped_ids.append(tx.id)
                continue

            expense = Expense(
                user_id=tx.user_id,
                amount=tx.amount,
                description=tx.normalized_merchant or tx.original_description,
                category=tx.assigned_category,
                payment_method=tx.payment_method if hasattr(tx, "payment_method") and tx.payment_method else "Card",
                date=tx.transaction_date.date() if hasattr(tx.transaction_date, "date") else date.today(),
                created_at=utc_now(),
            )
            try:
                claimed = await self._financial_tx_repo.atomic_claim(tx.id)
                if not claimed:
                    skipped_ids.append(tx.id)
                    continue
                created = await self._expense_repo.create(expense)
                created_ids.append(created.id)
            except Exception as e:
                logger.error("expense_gen_failed user=%s tx=%s error=%s", tx.user_id, tx.id, str(e))
                errors.append({"transaction_id": tx.id, "stage": "expense_generation", "message": str(e)})

        return created_ids, skipped_ids, errors

    def _qualifies(self, tx: FinancialTransaction, force: bool = False) -> bool:
        if tx.transaction_type != "DEBIT":
            return False
        if tx.is_refund:
            return False
        if tx.is_transfer:
            return False
        if tx.review_status not in ("auto_approved", "approved") and not force:
            return False
        if tx.confidence_score < 0.7 and not tx.reviewed_by and not force:
            return False
        return True
