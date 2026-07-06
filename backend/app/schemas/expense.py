from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import CATEGORIES, PAYMENT_METHODS
from app.schemas.common import PyObjectId


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=240)
    category: str | None = None
    payment_method: str = "Other"
    date: Date


class ExpenseUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1, max_length=240)
    category: str | None = None
    payment_method: str | None = None
    date: Date | None = None


class ExpensePublic(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    amount: float
    description: str
    category: str
    payment_method: str
    date: Date
    created_at: datetime
