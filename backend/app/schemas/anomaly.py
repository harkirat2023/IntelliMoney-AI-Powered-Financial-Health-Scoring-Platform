from datetime import date as Date
from datetime import datetime

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import PyObjectId


class SpendingAnomaly(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    category: str
    date: Date
    amount: float
    average_amount: float
    deviation_percentage: float = Field(ge=0, le=500)
    severity: str = Field(pattern="^(low|medium|high|critical)$")
    message: str
    is_read: bool
    created_at: datetime


class AnomalyAlert(BaseModel):
    category: str
    date: Date
    amount: float
    average_amount: float
    deviation_percentage: float
    severity: str
    message: str
    suggestion: str


class WeeklySpendingReport(BaseModel):
    week_start: Date
    week_end: Date
    total_spending: float
    category_breakdown: dict[str, float]
    top_categories: list[dict[str, Any]]
    anomalies_detected: int
    comparison_to_previous_week: float | None = None
    insights: list[str]