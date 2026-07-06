from typing import Any
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PyObjectId


class Subscription(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    description: str
    amount: float
    category: str
    frequency: str = Field(pattern="^(weekly|biweekly|monthly|yearly)$")
    start_date: Date
    end_date: Date | None
    is_active: bool
    last_payment_date: Date | None
    next_payment_date: Date | None
    total_spent: float
    payment_count: int
    created_at: datetime
    updated_at: datetime


class SubscriptionSuggestion(BaseModel):
    description: str
    amount: float
    category: str
    frequency: str
    confidence: float = Field(ge=0.0, le=1.0)
    occurrences_detected: int
    suggested_start_date: Date
    total_spent: float


class SubscriptionCreate(BaseModel):
    description: str = Field(min_length=1, max_length=240)
    amount: float = Field(gt=0)
    category: str
    frequency: str = Field(pattern="^(weekly|biweekly|monthly|yearly)$")
    start_date: Date
    end_date: Date | None = None
    is_active: bool = True


class SubscriptionUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=240)
    amount: float | None = Field(default=None, gt=0)
    category: str | None = None
    frequency: str | None = Field(default=None, pattern="^(weekly|biweekly|monthly|yearly)$")
    start_date: Date | None = None
    end_date: Date | None = None
    is_active: bool | None = None


class SubscriptionInsights(BaseModel):
    total_monthly_cost: float
    total_yearly_cost: float
    active_subscriptions: int
    top_expenses: list[dict[str, Any]]
    by_category: dict[str, float]
    insights: list[str]