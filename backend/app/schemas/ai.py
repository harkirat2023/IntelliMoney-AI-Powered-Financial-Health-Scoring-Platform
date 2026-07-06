from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ProcessPendingRequest(BaseModel):
    bank_account_id: str | None = None
    limit: int = 100

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError("limit must be between 1 and 1000")
        return v


class ProcessResultResponse(BaseModel):
    total_available: int
    processed: int
    skipped: int
    failed: int
    message: str = ""


class ReviewQueueItem(BaseModel):
    id: str
    original_description: str
    cleaned_merchant: str
    amount: float
    transaction_date: datetime
    assigned_category: str
    confidence_score: float
    is_income: bool
    is_recurring: bool


class ReviewQueueResponse(BaseModel):
    items: list[ReviewQueueItem]
    total: int
    limit: int
    offset: int


class ReviewSubmissionRequest(BaseModel):
    review_status: Literal["approved", "auto_approved"]
    assigned_category: str | None = None
    normalized_merchant: str | None = None
    is_income: bool | None = None
    is_recurring: bool | None = None
    transaction_tags: list[str] | None = None
    review_note: str | None = None


class FeedbackSubmissionRequest(BaseModel):
    feedback_type: Literal["category", "merchant", "income_flag"]
    user_category: str | None = None
    user_merchant: str | None = None
    is_income: bool | None = None


class FeedbackResponse(BaseModel):
    id: str
    message: str = "Feedback recorded. Thank you!"


class IntelligenceStatusResponse(BaseModel):
    is_healthy: bool
    pending_transactions: int
    total_processed_all_time: int
    total_in_review_queue: int
