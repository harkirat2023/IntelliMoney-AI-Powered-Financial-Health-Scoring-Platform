from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CATEGORIES


class FinancialTransactionResponse(BaseModel):
    id: str
    bank_account_id: str
    bank_transaction_id: str | None = None
    original_description: str
    cleaned_merchant: str
    normalized_merchant: str
    amount: float
    transaction_type: str
    transaction_date: datetime
    assigned_category: str
    confidence_score: float
    is_income: bool
    is_recurring: bool
    is_refund: bool
    is_transfer: bool
    transaction_tags: list[str]
    review_status: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, tx) -> "FinancialTransactionResponse":
        return cls(
            id=tx.id,
            bank_account_id=tx.bank_account_id,
            bank_transaction_id=tx.bank_transaction_id,
            original_description=tx.original_description,
            cleaned_merchant=tx.cleaned_merchant,
            normalized_merchant=tx.normalized_merchant,
            amount=tx.amount,
            transaction_type=tx.transaction_type,
            transaction_date=tx.transaction_date,
            assigned_category=tx.assigned_category,
            confidence_score=tx.confidence_score,
            is_income=tx.is_income,
            is_recurring=tx.is_recurring,
            is_refund=tx.is_refund,
            is_transfer=tx.is_transfer,
            transaction_tags=tx.transaction_tags,
            review_status=tx.review_status,
            reviewed_by=tx.reviewed_by,
            reviewed_at=tx.reviewed_at,
            review_note=tx.review_note,
            created_at=tx.created_at,
        )


class FinancialTransactionUpdateRequest(BaseModel):
    assigned_category: str | None = None
    normalized_merchant: str | None = None
    is_income: bool | None = None
    is_recurring: bool | None = None
    transaction_tags: list[str] | None = None
    review_note: str | None = None

    @field_validator("assigned_category")
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in CATEGORIES:
            raise ValueError(f"Category must be one of {CATEGORIES}")
        return v
