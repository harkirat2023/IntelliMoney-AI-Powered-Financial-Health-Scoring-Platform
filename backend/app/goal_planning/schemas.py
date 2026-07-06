from datetime import datetime

from pydantic import BaseModel, Field


class GoalCreateRequest(BaseModel):
    goal_type: str = Field(..., pattern=r"^(emergency_fund|vacation|laptop|vehicle|house|education|wedding|retirement|investment|custom)$")
    name: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: float = 0.0
    monthly_contribution: float = 0.0
    target_date: str = ""
    priority: str = "medium"
    category: str = ""
    description: str = ""
    auto_adjust: bool = True


class GoalUpdateRequest(BaseModel):
    name: str | None = None
    target_amount: float | None = None
    current_amount: float | None = None
    monthly_contribution: float | None = None
    target_date: str | None = None
    priority: str | None = None
    status: str | None = None
    category: str | None = None
    description: str | None = None
    auto_adjust: bool | None = None


class GoalResponse(BaseModel):
    id: str
    goal_type: str
    name: str
    target_amount: float
    current_amount: float
    monthly_contribution: float
    target_date: str = ""
    status: str = "active"
    priority: str = "medium"
    category: str = ""
    description: str = ""
    feasibility_score: float = 0.0
    confidence_score: float = 0.0
    risk_level: str = "moderate"
    affordability_score: float = 0.0
    completion_percentage: float = 0.0
    estimated_months: int = 0
    start_date: str = ""
    auto_adjust: bool = True
    is_system_recommended: bool = False
    metadata: dict = {}
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GoalProgressResponse(BaseModel):
    id: str
    goal_id: str
    period: str
    previous_amount: float = 0.0
    current_amount: float = 0.0
    monthly_contribution: float = 0.0
    contribution_count: int = 0
    skipped_months: int = 0
    milestone_hit: bool = False
    milestone_label: str = ""
    progress_percentage: float = 0.0
    on_track: bool = True
    notes: str = ""
    created_at: datetime | None = None


class GoalRecommendationResponse(BaseModel):
    id: str
    goal_id: str = ""
    recommendation_type: str = ""
    title: str = ""
    description: str = ""
    reasoning: str = ""
    confidence_score: float = 0.0
    estimated_impact: dict = {}
    affected_categories: list[str] = []
    actionable_steps: list[str] = []
    assumptions: list[str] = []
    priority: int = 0
    dismissed: bool = False
    created_at: datetime | None = None


class GoalPredictionResponse(BaseModel):
    goal_id: str
    predicted_completion_date: str = ""
    predicted_completion_amount: float = 0.0
    estimated_months_remaining: int = 0
    monthly_contribution_required: float = 0.0
    projected_amounts: list[dict] = []
    confidence_interval: list[float] = []
    best_case_date: str = ""
    worst_case_date: str = ""
    probability_of_success: float = 0.0


class GoalAnalyzeRequest(BaseModel):
    goal_type: str = "custom"
    name: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    target_date: str = ""
    monthly_contribution: float = 0.0


class GoalAnalyzeResponse(BaseModel):
    feasible: bool
    feasibility_score: float
    affordability_score: float
    estimated_months: int
    monthly_savings_required: float
    risk_level: str
    confidence_score: float
    reasoning: str
    suggestions: list[str] = []


class GoalProgressResponseList(BaseModel):
    goal: GoalResponse
    progress: list[GoalProgressResponse] = []


class GoalRecalculateResponse(BaseModel):
    goals_updated: int
    predictions_generated: int
    recommendations_generated: int
    message: str


class GoalCreateResponse(BaseModel):
    goal: GoalResponse
    prediction: GoalPredictionResponse | None = None
    recommendations: list[GoalRecommendationResponse] = []
    message: str
