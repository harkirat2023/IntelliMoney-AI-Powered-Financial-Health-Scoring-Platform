from datetime import datetime
from typing import Literal

from bson import ObjectId
from pydantic import BaseModel


ReviewStatus = Literal["auto_approved", "approved", "review_required"]


class FinancialTransaction(BaseModel):
    id: str | None = None
    user_id: str
    bank_account_id: str
    bank_transaction_id: str
    sync_log_id: str | None = None
    provider_account_id: str
    transaction_id: str
    original_description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    original_category: str | None = None
    reference: str | None = None
    cleaned_merchant: str = ""
    normalized_merchant: str = ""
    merchant_id: str | None = None
    assigned_category: str = "Other"
    confidence_score: float = 0.0
    is_income: bool = False
    is_recurring: bool = False
    recurring_id: str | None = None
    transaction_tags: list[str] = []
    is_refund: bool = False
    is_transfer: bool = False
    review_status: ReviewStatus = "review_required"
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None
    processed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "FinancialTransaction":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            bank_account_id=str(doc["bank_account_id"]),
            bank_transaction_id=str(doc["bank_transaction_id"]),
            sync_log_id=str(doc["sync_log_id"]) if doc.get("sync_log_id") else None,
            provider_account_id=doc["provider_account_id"],
            transaction_id=doc["transaction_id"],
            original_description=doc["original_description"],
            amount=float(doc["amount"]),
            transaction_type=doc["transaction_type"],
            transaction_date=doc["transaction_date"],
            original_category=doc.get("original_category"),
            reference=doc.get("reference"),
            cleaned_merchant=doc.get("cleaned_merchant", ""),
            normalized_merchant=doc.get("normalized_merchant", ""),
            merchant_id=str(doc["merchant_id"]) if doc.get("merchant_id") else None,
            assigned_category=doc.get("assigned_category", "Other"),
            confidence_score=float(doc.get("confidence_score", 0.0)),
            is_income=bool(doc.get("is_income", False)),
            is_recurring=bool(doc.get("is_recurring", False)),
            recurring_id=str(doc["recurring_id"]) if doc.get("recurring_id") else None,
            transaction_tags=list(doc.get("transaction_tags", [])),
            is_refund=bool(doc.get("is_refund", False)),
            is_transfer=bool(doc.get("is_transfer", False)),
            review_status=doc.get("review_status", "review_required"),
            reviewed_by=str(doc["reviewed_by"]) if doc.get("reviewed_by") else None,
            reviewed_at=doc.get("reviewed_at"),
            review_note=doc.get("review_note"),
            processed_at=doc.get("processed_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "bank_account_id", "bank_transaction_id", "sync_log_id", "merchant_id", "recurring_id", "reviewed_by"})
        data["user_id"] = ObjectId(self.user_id)
        data["bank_account_id"] = ObjectId(self.bank_account_id)
        data["bank_transaction_id"] = ObjectId(self.bank_transaction_id)
        if self.sync_log_id:
            data["sync_log_id"] = ObjectId(self.sync_log_id)
        if self.merchant_id:
            data["merchant_id"] = ObjectId(self.merchant_id)
        if self.recurring_id:
            data["recurring_id"] = ObjectId(self.recurring_id)
        if self.reviewed_by:
            data["reviewed_by"] = ObjectId(self.reviewed_by)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
