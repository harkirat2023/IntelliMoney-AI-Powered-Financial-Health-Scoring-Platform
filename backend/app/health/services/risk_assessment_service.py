import logging

from app.health.models.financial_health import FinancialHealth
from app.health.models.risk_profile import RiskProfile
from app.health.repositories.risk_repository import MongoRiskRepository
from app.utils.date_utils import utc_now

logger = logging.getLogger("intellimoney")


def _risk_level_for_score(score: float) -> str:
    if score >= 70:
        return "low"
    if score >= 40:
        return "moderate"
    return "high"


def _overall_risk_level(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 45:
        return "Moderate"
    if score >= 25:
        return "Needs Attention"
    return "Critical"


class RiskAssessmentService:
    def __init__(self, risk_repo: MongoRiskRepository):
        self._risk_repo = risk_repo

    async def assess(self, user_id: str, health: FinancialHealth) -> RiskProfile:
        now = utc_now()
        savings_risk = _risk_level_for_score(health.savings_component)
        budget_risk = _risk_level_for_score(health.budget_adherence)
        expense_risk = _risk_level_for_score(health.expense_stability)
        flow_risk = _risk_level_for_score(health.cash_flow_stability)
        income_risk = _risk_level_for_score(health.income_consistency)
        emergency_risk = _risk_level_for_score(health.emergency_fund_score)

        recurring_score = 100 - (health.recurring_expense_ratio * 100)
        recurring_risk = _risk_level_for_score(recurring_score)

        profile = RiskProfile(
            user_id=user_id,
            period=health.period,
            overall_risk_level=_overall_risk_level(health.score),
            overall_risk_score=100 - health.score,
            savings_risk=savings_risk,
            budget_risk=budget_risk,
            expense_risk=expense_risk,
            cash_flow_risk=flow_risk,
            income_risk=income_risk,
            emergency_risk=emergency_risk,
            recurring_risk=recurring_risk,
            calculated_at=now,
        )

        result = await self._risk_repo.upsert(profile)
        logger.info(
            "risk_assessed user=%s period=%s risk=%s score=%d",
            user_id, health.period, result.overall_risk_level, result.overall_risk_score,
        )
        return result
