from typing import Any
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PyObjectId


class BudgetSuggestion(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    category: str
    current_limit: float
    suggested_limit: float
    average_spending: float
    max_spending: float
    min_spending: float
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    months_analyzed: int
    is_applied: bool
    created_at: datetime


class BudgetOptimizationReport(BaseModel):
    total_budget: float
    total_suggested: float
    potential_savings: float
    categories_analyzed: int
    suggestions: list[dict[str, Any]]
    insights: list[str]
    generated_at: datetime