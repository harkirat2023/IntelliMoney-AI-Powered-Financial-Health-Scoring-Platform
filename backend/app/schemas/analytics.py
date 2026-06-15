from datetime import date as Date

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    monthly_income: float
    total_spending: float
    savings_estimate: float
    savings_rate: float
    expense_count: int
    top_category: str | None


class ChartPoint(BaseModel):
    label: str
    value: float


class RecentExpense(BaseModel):
    id: str
    amount: float
    description: str
    category: str
    payment_method: str
    date: Date


class FinancialHealthScore(BaseModel):
    score: int
    risk_level: str
    savings_rate: float
    budget_adherence: float
    expense_stability: float
    calculated_at: str


class Recommendation(BaseModel):
    title: str
    message: str
    severity: str
    category: str
    suggested_action: str
