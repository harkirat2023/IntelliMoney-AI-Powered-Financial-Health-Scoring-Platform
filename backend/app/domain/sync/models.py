from datetime import datetime
from typing import Literal

from bson import ObjectId
from pydantic import BaseModel

from app.utils.date_utils import utc_now


class BankTransaction(BaseModel):
    id: str | None = None
    user_id: str
    bank_account_id: str
    sync_log_id: str | None = None
    provider_account_id: str
    transaction_id: str
    description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    category: str | None = None
    reference: str | None = None
    created_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "BankTransaction":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            bank_account_id=str(doc["bank_account_id"]),
            sync_log_id=str(doc["sync_log_id"]) if doc.get("sync_log_id") else None,
            provider_account_id=doc["provider_account_id"],
            transaction_id=doc["transaction_id"],
            description=doc["description"],
            amount=float(doc["amount"]),
            transaction_type=doc["transaction_type"],
            transaction_date=doc["transaction_date"],
            category=doc.get("category"),
            reference=doc.get("reference"),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "bank_account_id", "sync_log_id"})
        data["user_id"] = ObjectId(self.user_id)
        data["bank_account_id"] = ObjectId(self.bank_account_id)
        if self.sync_log_id:
            data["sync_log_id"] = ObjectId(self.sync_log_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data


SyncLogStatus = Literal["pending", "running", "completed", "failed"]
SyncLogType = Literal["initial", "manual", "retry"]
SyncErrorCategory = Literal["consent_expired", "provider_error", "network_error", "none"]


class SyncLog(BaseModel):
    id: str | None = None
    user_id: str
    bank_account_id: str
    sync_type: SyncLogType = "manual"
    status: SyncLogStatus = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    transactions_fetched: int = 0
    transactions_imported: int = 0
    transactions_skipped: int = 0
    error_message: str | None = None
    error_category: SyncErrorCategory = "none"
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime | None = None

    def mark_running(self) -> None:
        now = utc_now()
        self.status = "running"
        self.started_at = now

    def mark_completed(self, fetched: int, imported: int, skipped: int) -> None:
        self.status = "completed"
        self.completed_at = utc_now()
        self.transactions_fetched = fetched
        self.transactions_imported = imported
        self.transactions_skipped = skipped

    def mark_failed(self, error_message: str, category: SyncErrorCategory = "network_error") -> None:
        self.status = "failed"
        self.completed_at = utc_now()
        self.error_message = error_message
        self.error_category = category

    def can_retry(self) -> bool:
        return (
            self.status == "failed"
            and self.retry_count < self.max_retries
        )

    @classmethod
    def from_mongo(cls, doc: dict) -> "SyncLog":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            bank_account_id=str(doc["bank_account_id"]),
            sync_type=doc.get("sync_type", "manual"),
            status=doc.get("status", "pending"),
            started_at=doc.get("started_at"),
            completed_at=doc.get("completed_at"),
            transactions_fetched=doc.get("transactions_fetched", 0),
            transactions_imported=doc.get("transactions_imported", 0),
            transactions_skipped=doc.get("transactions_skipped", 0),
            error_message=doc.get("error_message"),
            error_category=doc.get("error_category", "none"),
            retry_count=doc.get("retry_count", 0),
            max_retries=doc.get("max_retries", 3),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "bank_account_id"})
        data["user_id"] = ObjectId(self.user_id)
        data["bank_account_id"] = ObjectId(self.bank_account_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
