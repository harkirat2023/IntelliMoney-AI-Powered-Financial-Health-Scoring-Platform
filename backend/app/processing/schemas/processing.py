from datetime import datetime

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    transaction_ids: list[str] = Field(min_length=1, max_length=500)
    force: bool = False


class ReprocessRequest(BaseModel):
    transaction_ids: list[str] = Field(min_length=1, max_length=500)
    reason: str | None = None


class ProcessingSummaryResponse(BaseModel):
    expenses_created: int = 0
    expenses_skipped: int = 0
    budget_usage_updated: int = 0
    dashboard_metrics_updated: int = 0
    financial_metrics_updated: int = 0
    cash_flow_updated: int = 0
    alerts_generated: int = 0


class ProcessingStatusResponse(BaseModel):
    batch_id: str
    status: str
    total: int
    processed: int
    failed: int
    errors: list[dict] = []
    summary: ProcessingSummaryResponse | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class ProcessingHistoryResponse(BaseModel):
    batch_id: str
    status: str
    total: int
    processed: int
    failed: int
    created_at: datetime | None = None
    completed_at: datetime | None = None
