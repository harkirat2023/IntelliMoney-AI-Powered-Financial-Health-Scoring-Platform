from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PyObjectId


class RecurringExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=240)
    amount: float = Field(gt=0)
    category: str
    frequency: str = Field(pattern="^(weekly|biweekly|monthly|yearly)$")
    start_date: Date
    end_date: Date | None = None
    is_active: bool = True


class RecurringExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=240)
    amount: float | None = Field(default=None, gt=0)
    category: str | None = None
    frequency: str | None = Field(default=None, pattern="^(weekly|biweekly|monthly|yearly)$")
    start_date: Date | None = None
    end_date: Date | None = None
    is_active: bool | None = None


class RecurringExpensePublic(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    description: str
    amount: float
    category: str
    frequency: str
    start_date: Date
    end_date: Date | None
    is_active: bool
    last_generated_date: Date | None
    next_expected_date: Date | None
    created_at: datetime
    updated_at: datetime


class RecurringExpenseSuggestion(BaseModel):
    description: str
    amount: float
    category: str
    frequency: str
    confidence: float = Field(ge=0.0, le=1.0)
    occurrences_detected: int
    suggested_start_date: Date
    suggested_end_date: Date | None = None