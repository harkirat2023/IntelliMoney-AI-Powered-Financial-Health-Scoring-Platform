from app.health.repositories.financial_health_repository import (
    MongoFinancialHealthRepository,
)
from app.health.repositories.health_history_repository import (
    MongoHealthHistoryRepository,
)
from app.health.repositories.recommendation_repository import (
    MongoRecommendationRepository,
)
from app.health.repositories.risk_repository import MongoRiskRepository
from app.health.schemas import (
    FactorDetail, HealthBreakdownResponse, HealthCurrentResponse,
    HealthFactorGroup, HealthHistoryResponse, HistoryPoint,
    HealthRecommendationItem, RiskAssessmentResponse, RiskDimension, TrendAnalysis, TrendPoint,
)


class HealthAggregationService:
    def __init__(
        self,
        health_repo: MongoFinancialHealthRepository,
        history_repo: MongoHealthHistoryRepository,
        risk_repo: MongoRiskRepository,
        rec_repo: MongoRecommendationRepository,
    ):
        self._health_repo = health_repo
        self._history_repo = history_repo
        self._risk_repo = risk_repo
        self._rec_repo = rec_repo

    WEIGHTS = {
        "Savings Rate": ("savings_component", 0.20),
        "Budget Adherence": ("budget_adherence", 0.15),
        "Expense Stability": ("expense_stability", 0.10),
        "Cash Flow Stability": ("cash_flow_stability", 0.15),
        "Income Consistency": ("income_consistency", 0.10),
        "Emergency Fund": ("emergency_fund_score", 0.10),
        "Recurring Ratio": ("recurring_expense_ratio", 0.05),
        "Essential Spending": ("essential_spending_ratio", 0.10),
        "Debt Readiness": ("debt_readiness", 0.025),
        "Investment Readiness": ("investment_readiness", 0.025),
    }

    def _status(self, val: float) -> str:
        if val >= 80:
            return "excellent"
        if val >= 60:
            return "good"
        if val >= 40:
            return "moderate"
        return "needs_attention"

    async def get_current(self, user_id: str) -> HealthCurrentResponse | None:
        health = await self._health_repo.get_latest(user_id)
        if not health:
            return None

        groups = [
            HealthFactorGroup(
                name="Saving & Budgeting",
                score=round((health.savings_component * 0.4 + health.budget_adherence * 0.6), 2),
                weight=0.35,
                factors=[
                    FactorDetail(name="Savings Rate", value=health.savings_component, weight=0.20, contribution=round(health.savings_component * 0.20, 2), status=self._status(health.savings_component)),
                    FactorDetail(name="Budget Adherence", value=health.budget_adherence, weight=0.15, contribution=round(health.budget_adherence * 0.15, 2), status=self._status(health.budget_adherence)),
                ],
            ),
            HealthFactorGroup(
                name="Stability & Cash Flow",
                score=round((health.expense_stability * 0.3 + health.cash_flow_stability * 0.4 + health.income_consistency * 0.3), 2),
                weight=0.35,
                factors=[
                    FactorDetail(name="Expense Stability", value=health.expense_stability, weight=0.10, contribution=round(health.expense_stability * 0.10, 2), status=self._status(health.expense_stability)),
                    FactorDetail(name="Cash Flow Stability", value=health.cash_flow_stability, weight=0.15, contribution=round(health.cash_flow_stability * 0.15, 2), status=self._status(health.cash_flow_stability)),
                    FactorDetail(name="Income Consistency", value=health.income_consistency, weight=0.10, contribution=round(health.income_consistency * 0.10, 2), status=self._status(health.income_consistency)),
                ],
            ),
            HealthFactorGroup(
                name="Resilience & Efficiency",
                score=round((health.emergency_fund_score * 0.5 + (100 - health.recurring_expense_ratio * 100) * 0.25 + health.essential_spending_ratio * 0.25), 2),
                weight=0.30,
                factors=[
                    FactorDetail(name="Emergency Fund", value=health.emergency_fund_score, weight=0.10, contribution=round(health.emergency_fund_score * 0.10, 2), status=self._status(health.emergency_fund_score)),
                    FactorDetail(name="Recurring Expense Ratio", value=100 - health.recurring_expense_ratio * 100, weight=0.05, contribution=round((100 - health.recurring_expense_ratio * 100) * 0.05, 2), status=self._status(100 - health.recurring_expense_ratio * 100)),
                    FactorDetail(name="Essential Spending", value=health.essential_spending_ratio, weight=0.10, contribution=round(health.essential_spending_ratio * 0.10, 2), status=self._status(health.essential_spending_ratio)),
                ],
            ),
        ]

        return HealthCurrentResponse(
            period=health.period,
            score=health.score,
            risk_level=health.risk_level,
            factor_groups=groups,
            calculated_at=health.calculated_at,
        )

    async def get_history(self, user_id: str, limit: int = 36) -> HealthHistoryResponse:
        current = await self.get_current(user_id)
        history = await self._history_repo.get_by_user(user_id, limit)
        return HealthHistoryResponse(
            current=current,
            history=[
                HistoryPoint(
                    period=h.period, score=h.score, risk_level=h.risk_level,
                    savings_rate=h.savings_rate, budget_adherence=h.budget_adherence,
                    expense_stability=h.expense_stability,
                ) for h in history
            ],
        )

    async def get_trends(self, user_id: str, months: int = 12) -> TrendAnalysis:
        history = await self._history_repo.get_by_user(user_id, months)
        if not history:
            return TrendAnalysis(overall_trend="stable", volatility=0, periods_analyzed=0)
        deltas = []
        points = []
        for i in range(len(history)):
            prev_score = history[i + 1].score if i + 1 < len(history) else history[i].score
            delta = history[i].score - prev_score if i + 1 < len(history) else 0
            deltas.append(delta)
            points.append(TrendPoint(period=history[i].period, score=history[i].score, delta=delta))
        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        trend = "improving" if avg_delta > 3 else "declining" if avg_delta < -3 else "stable"
        scores = [h.score for h in history]
        from statistics import pstdev
        volatility = round(pstdev(scores), 2) if len(scores) > 1 else 0
        return TrendAnalysis(overall_trend=trend, volatility=volatility, periods_analyzed=len(history), points=points)

    async def get_breakdown(self, user_id: str) -> HealthBreakdownResponse | None:
        health = await self._health_repo.get_latest(user_id)
        if not health:
            return None
        factors = []
        strengths = []
        weaknesses = []
        for name, (attr, weight) in self.WEIGHTS.items():
            val = getattr(health, attr, 0)
            if isinstance(val, float) and attr == "recurring_expense_ratio":
                val = 100 - val * 100
            factor = FactorDetail(
                name=name, value=round(float(val), 2), weight=weight,
                contribution=round(float(val) * weight, 2),
                status=self._status(float(val)),
            )
            factors.append(factor)
            if float(val) >= 60:
                strengths.append(f"{name} ({round(float(val), 1)})")
            else:
                weaknesses.append(f"{name} ({round(float(val), 1)})")
        return HealthBreakdownResponse(
            period=health.period, score=health.score, risk_level=health.risk_level,
            factors=factors, strengths=strengths, weaknesses=weaknesses,
        )

    async def get_recommendations(self, user_id: str) -> list[HealthRecommendationItem]:
        recs = await self._rec_repo.get_by_user(user_id)
        return [
            HealthRecommendationItem(
                id=r.id, category=r.category, priority=r.priority, title=r.title,
                message=r.message, metric=r.metric, current_value=r.current_value,
                target_value=r.target_value, impact=r.impact, action=r.action,
                dismissed=r.dismissed, created_at=r.created_at,
            ) for r in recs if r.id
        ]

    async def get_risk(self, user_id: str) -> RiskAssessmentResponse | None:
        profile = await self._risk_repo.get_latest(user_id)
        if not profile:
            return None
        return RiskAssessmentResponse(
            period=profile.period,
            overall_risk_level=profile.overall_risk_level,
            overall_risk_score=profile.overall_risk_score,
            dimensions=[
                RiskDimension(name="Savings", level=profile.savings_risk, score=100 if profile.savings_risk == "low" else 50 if profile.savings_risk == "moderate" else 20),
                RiskDimension(name="Budget", level=profile.budget_risk, score=100 if profile.budget_risk == "low" else 50 if profile.budget_risk == "moderate" else 20),
                RiskDimension(name="Expenses", level=profile.expense_risk, score=100 if profile.expense_risk == "low" else 50 if profile.expense_risk == "moderate" else 20),
                RiskDimension(name="Cash Flow", level=profile.cash_flow_risk, score=100 if profile.cash_flow_risk == "low" else 50 if profile.cash_flow_risk == "moderate" else 20),
                RiskDimension(name="Income", level=profile.income_risk, score=100 if profile.income_risk == "low" else 50 if profile.income_risk == "moderate" else 20),
                RiskDimension(name="Emergency", level=profile.emergency_risk, score=100 if profile.emergency_risk == "low" else 50 if profile.emergency_risk == "moderate" else 20),
                RiskDimension(name="Recurring", level=profile.recurring_risk, score=100 if profile.recurring_risk == "low" else 50 if profile.recurring_risk == "moderate" else 20),
            ],
        )
