from datetime import datetime

from pydantic import BaseModel


class FactorDetail(BaseModel):
    name: str
    value: float
    weight: float
    contribution: float
    status: str


class HealthFactorGroup(BaseModel):
    name: str
    score: float
    weight: float
    factors: list[FactorDetail]


class HealthCurrentResponse(BaseModel):
    period: str
    score: int
    risk_level: str
    factor_groups: list[HealthFactorGroup] = []
    calculated_at: datetime | None = None


class HistoryPoint(BaseModel):
    period: str
    score: int
    risk_level: str
    savings_rate: float
    budget_adherence: float
    expense_stability: float


class HealthHistoryResponse(BaseModel):
    current: HealthCurrentResponse | None = None
    history: list[HistoryPoint] = []


class TrendPoint(BaseModel):
    period: str
    score: int
    delta: int


class TrendAnalysis(BaseModel):
    overall_trend: str
    volatility: float
    periods_analyzed: int
    points: list[TrendPoint] = []


class HealthBreakdownResponse(BaseModel):
    period: str
    score: int
    risk_level: str
    factors: list[FactorDetail] = []
    strengths: list[str] = []
    weaknesses: list[str] = []


class HealthRecommendationItem(BaseModel):
    id: str
    category: str
    priority: str
    title: str
    message: str
    metric: str
    current_value: float
    target_value: float
    impact: str
    action: str
    dismissed: bool
    created_at: datetime | None = None


class RiskDimension(BaseModel):
    name: str
    level: str
    score: float


class RiskAssessmentResponse(BaseModel):
    period: str
    overall_risk_level: str
    overall_risk_score: int
    dimensions: list[RiskDimension] = []


class CalculateResponse(BaseModel):
    period: str
    score: int
    risk_level: str
    message: str
