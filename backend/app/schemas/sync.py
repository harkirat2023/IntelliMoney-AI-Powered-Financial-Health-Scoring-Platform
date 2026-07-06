from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SyncStartRequest(BaseModel):
    bank_account_id: str


class SyncStartResponse(BaseModel):
    sync_log_id: str
    status: str
    message: str


class SyncManualResponse(BaseModel):
    results: list[SyncStartResponse]


class SyncLogSummary(BaseModel):
    id: str
    status: str
    sync_type: str
    transactions_imported: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class SyncStatusResponse(BaseModel):
    bank_account_id: str
    bank_name: str
    masked_account_number: str
    last_synced_at: datetime | None = None
    sync_status: Literal["idle", "pending", "running", "completed", "failed", "never"]
    latest_sync: SyncLogSummary | None = None


class SyncLogDetail(BaseModel):
    id: str
    bank_account_id: str
    sync_type: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    transactions_fetched: int
    transactions_imported: int
    transactions_skipped: int
    error_message: str | None = None
    error_category: str
    retry_count: int
    created_at: datetime | None = None


class SyncHistoryResponse(BaseModel):
    items: list[SyncLogDetail]
    total: int
    limit: int
    offset: int


class SyncRetryRequest(BaseModel):
    sync_log_id: str


class SyncRetryResponse(BaseModel):
    sync_log_id: str
    status: str
    message: str
