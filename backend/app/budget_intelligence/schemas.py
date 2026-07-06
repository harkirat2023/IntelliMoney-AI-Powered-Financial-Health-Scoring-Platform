from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBudgetInfo(BaseModel):
    category: str
    limit: float = 0.0
    spent: float = 0.0
    suggested: float | None = None
    percentage_used: float = 0.0
    state: str = "safe"
    trend: str = "stable"
    month_over_month_change: float = 0.0


class BudgetIntelligenceResponse(BaseModel):
    period: str
    budget_score: float
    total_budget: float
    total_spent: float
    total_suggested: float
    potential_savings: float
    category_count: int
    on_track_count: int
    warning_count: int
    over_count: int
    categories: list[CategoryBudgetInfo] = []
    calculated_at: datetime | None = None


class RecommendationResponse(BaseModel):
    id: str
    category: str
    recommendation_type: str
    title: str
    message: str
    current_value: float = 0.0
    target_value: float = 0.0
    potential_savings: float = 0.0
    confidence_score: float = 0.0
    priority: str = "medium"
    reasoning: str = ""
    affected_categories: list[str] = []
    estimated_impact: str = ""
    actionable_steps: list[str] = []
    dismissed: bool = False
    created_at: datetime | None = None


class OptimizationSuggestion(BaseModel):
    category: str
    current_limit: float = 0.0
    suggested_limit: float = 0.0
    reason: str = ""
    potential_savings: float = 0.0
    confidence_score: float = 0.0


class BudgetOptimizationResponse(BaseModel):
    total_budget: float
    total_suggested: float
    total_current: float
    potential_monthly_savings: float
    suggestions: list[OptimizationSuggestion] = []
    insights: list[str] = []


class CategoryPrediction(BaseModel):
    category: str
    predicted_spending: float = 0.0
    predicted_utilization: float = 0.0
    confidence_upper: float = 0.0
    confidence_lower: float = 0.0
    trend_direction: str = "stable"
    months_analyzed: int = 0


class BudgetTrendsResponse(BaseModel):
    period: str
    predictions: list[CategoryPrediction] = []


class RiskCategoryInfo(BaseModel):
    category: str
    risk_level: str = "low"
    risk_score: float = 0.0
    percentage_used: float = 0.0
    trend: str = "stable"


class BudgetRiskResponse(BaseModel):
    period: str
    overall_risk_level: str = "low"
    overall_risk_score: float = 0.0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    volatility_score: float = 0.0
    trend_direction: str = "stable"
    categories: list[RiskCategoryInfo] = []


class SavingsOpportunityResponse(BaseModel):
    id: str
    opportunity_type: str
    category: str
    title: str
    message: str
    potential_savings: float = 0.0
    confidence_score: float = 0.0
    monthly_impact: float = 0.0
    annual_impact: float = 0.0
    reasoning: str = ""
    actionable_steps: list[str] = []
    dismissed: bool = False
    created_at: datetime | None = None


class GenerateResponse(BaseModel):
    period: str
    budget_score: float
    recommendations_count: int = 0
    opportunities_count: int = 0
    message: str
