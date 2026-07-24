from pydantic import BaseModel


class SpendingCategory(BaseModel):
    category: str
    amount: float
    percentage: float


class MonthlyTrendPoint(BaseModel):
    month: str
    spending: float
    income: float


class TopMerchant(BaseModel):
    merchant: str
    amount: float
    count: int


class BudgetOverview(BaseModel):
    category: str
    limit: float
    spent: float
    remaining: float = 0
    percentage_used: float = 0
    state: str


class DashboardSummaryResponse(BaseModel):
    period: str
    total_spending: float
    total_income: float
    net_savings: float
    savings_rate: float
    expense_count: int
    spending_by_category: list[SpendingCategory] = []
    monthly_trend: list[MonthlyTrendPoint] = []
    top_merchants: list[TopMerchant] = []
    budget_overview: list[BudgetOverview] = []


class CashFlowPoint(BaseModel):
    year: int
    month: int
    total_income: float
    total_expenses: float
    net_cash_flow: float
    income_by_category: list[dict] = []
    expense_by_category: list[dict] = []


class SpendingResponse(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int = 0


class MonthlyTrendResponse(BaseModel):
    month: str
    spending: float
    income: float
    savings: float
