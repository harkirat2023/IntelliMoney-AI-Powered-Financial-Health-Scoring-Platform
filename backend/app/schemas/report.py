from typing import Any
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import PyObjectId


class FinancialReport(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    report_type: str = Field(pattern="^(weekly|monthly)$")
    period_start: Date
    period_end: Date

    @field_validator("period_start", "period_end", mode="before")
    @classmethod
    def coerce_datetime_to_date(cls, v: Any) -> Any:
        if isinstance(v, datetime):
            return v.date()
        return v
    total_spending: float
    total_income: float
    net_savings: float
    savings_rate: float
    category_breakdown: dict[str, float]
    top_expenses: list[dict[str, Any]]
    budget_performance: dict[str, Any]
    health_score: int | None
    insights: list[str]
    recommendations: list[dict[str, str]]
    generated_at: datetime
    is_read: bool


class ReportSummary(BaseModel):
    total_reports: int
    latest_report: FinancialReport | None
    unread_count: int
    average_monthly_spending: float
    average_savings_rate: float
    spending_trend: str  # "increasing", "decreasing", "stable"