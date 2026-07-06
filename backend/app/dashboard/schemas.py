from pydantic import BaseModel


class WidgetMetric(BaseModel):
    label: str
    value: float | str
    change: float | None = None
    change_type: str = "neutral"


class HealthScoreWidget(BaseModel):
    score: int
    risk_level: str
    savings_rate: float
    budget_adherence: float
    expense_stability: float
    discretionary_ratio: float
    trend: str
    month_over_month_change: float


class SpendingWidget(BaseModel):
    total_spending: float
    expense_count: int
    top_category: str | None = None
    top_category_amount: float = 0
    spending_by_category: list[dict] = []


class IncomeWidget(BaseModel):
    total_income: float
    primary_source: str | None = None
    income_by_category: list[dict] = []


class SavingsWidget(BaseModel):
    net_savings: float
    savings_rate: float
    previous_savings_rate: float | None = None


class CashFlowWidget(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    expense_by_category: list[dict] = []
    income_by_category: list[dict] = []


class BudgetStatusWidget(BaseModel):
    budget_count: int
    on_track: int
    warning: int
    over: int
    budgets: list[dict] = []


class RecentTransactionItem(BaseModel):
    id: str
    description: str
    amount: float
    category: str
    date: str
    merchant: str | None = None


class RecurringWidget(BaseModel):
    total_monthly: float
    upcoming_count: int
    items: list[dict] = []


class SubscriptionWidget(BaseModel):
    total_monthly: float
    total_yearly: float
    active_count: int
    items: list[dict] = []


class UpcomingBillsWidget(BaseModel):
    total_due: float
    due_soon_count: int
    bills: list[dict] = []


class AIInsightItem(BaseModel):
    id: str
    title: str
    message: str
    severity: str
    category: str
    created_at: str | None = None


class BudgetAlertItem(BaseModel):
    id: str
    category: str
    threshold: int
    percentage: float
    message: str
    read: bool = False
    created_at: str | None = None


class TopCategoryItem(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int = 0


class MonthlyTrendPoint(BaseModel):
    month: str
    spending: float
    income: float
    savings: float


class SpendingHeatmapPoint(BaseModel):
    day: str
    amount: float
    category: str


class ActivityFeedItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    metadata: dict = {}


class NotificationItem(BaseModel):
    id: str
    type: str
    title: str
    message: str
    read: bool = False
    created_at: str
    metadata: dict = {}


class DashboardOverviewResponse(BaseModel):
    health_score: HealthScoreWidget | None = None
    spending: SpendingWidget | None = None
    income: IncomeWidget | None = None
    savings: SavingsWidget | None = None
    cash_flow: CashFlowWidget | None = None
    budget_status: BudgetStatusWidget | None = None
    recent_transactions: list[RecentTransactionItem] = []
    recurring: RecurringWidget | None = None
    subscriptions: SubscriptionWidget | None = None
    upcoming_bills: UpcomingBillsWidget | None = None
    ai_insights: list[AIInsightItem] = []
    budget_alerts: list[BudgetAlertItem] = []
    top_categories: list[TopCategoryItem] = []
    monthly_trend: list[MonthlyTrendPoint] = []
    spending_heatmap: list[SpendingHeatmapPoint] = []
    activity: list[ActivityFeedItem] = []


class AnalyticsResponse(BaseModel):
    total_spending: float
    total_income: float
    net_savings: float
    savings_rate: float
    expense_count: int
    average_daily_spending: float
    busiest_day: str | None = None
    top_merchants: list[dict] = []
    spending_by_category: list[dict] = []
    monthly_trend: list[MonthlyTrendPoint] = []
    budget_overview: list[dict] = []


class WidgetsResponse(BaseModel):
    widgets: dict[str, object] = {}
