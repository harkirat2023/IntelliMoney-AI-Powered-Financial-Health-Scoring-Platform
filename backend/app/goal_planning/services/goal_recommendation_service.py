import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import FinancialGoal, GoalRecommendation
from app.goal_planning.repositories.goal_repositories import (
    GoalRecommendationRepository, MongoGoalRecommendationRepository,
)

logger = logging.getLogger(__name__)

RECOMMENDATION_TYPES = [
    "increase_contribution", "reduce_spending", "extend_timeline",
    "reduce_target", "pause_goal", "budget_reallocation",
    "improve_health", "milestone_warning", "completion_forecast",
]


class GoalRecommendationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._repo: GoalRecommendationRepository = MongoGoalRecommendationRepository(db)
        self._db = db

    async def generate(self, user_id: str, goal: FinancialGoal | None = None) -> list[GoalRecommendation]:
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])
        health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])

        net_savings = cash.get("net_savings", 0) if cash else 0
        health_score = health.get("score", 0) if health else 0
        recommendations = []

        goals = [goal] if goal else await self._get_active_goals(user_id)

        for g in goals:
            remaining = max(0, g.target_amount - g.current_amount)
            mc = g.monthly_contribution

            if mc > 0 and net_savings > mc * 1.5:
                extra = net_savings - mc
                rec = GoalRecommendation(
                    user_id=user_id, goal_id=g.id,
                    recommendation_type="increase_contribution",
                    title=f"Increase contribution to '{g.name}'",
                    description=f"You have ₹{extra:,.0f} monthly surplus. Increasing contribution by ₹{min(extra, mc):,.0f} would cut completion time significantly.",
                    reasoning=f"Net savings (₹{net_savings:,.0f}) exceed current contribution (₹{mc:,.0f}) by ₹{extra:,.0f}",
                    confidence_score=min(95, round(extra / max(mc, 1) * 50 + 50, 1)),
                    estimated_impact={"monthly_savings": round(min(extra, mc), 2)},
                    affected_categories=["savings"],
                    actionable_steps=[f"Increase monthly contribution by ₹{min(extra, mc):,.0f}",
                                      f"Set auto-transfer of ₹{mc + min(extra, mc):,.0f}/month"],
                    assumptions=["Surplus income remains stable", "No major expense increases"],
                    priority=1,
                )
                recommendations.append(rec)

            if budget:
                categories = budget.get("categories", [])
                discretionary = ["food_delivery", "entertainment", "shopping", "dining", "subscriptions"]
                overspent = [c for c in categories if c.get("category") in discretionary and c.get("state") == "over"]
                for c in overspent[:2]:
                    overspend = max(0, c.get("spent", 0) - c.get("limit", 0))
                    if overspend > 0:
                        rec = GoalRecommendation(
                            user_id=user_id, goal_id=g.id,
                            recommendation_type="reduce_spending",
                            title=f"Reduce {c['category']} spending for '{g.name}'",
                            description=f"Cutting {c['category']} by ₹{overspend:,.0f}/month would accelerate goal completion.",
                            reasoning=f"{c['category']} is overspent by ₹{overspend:,.0f}. Redirecting this saves time.",
                            confidence_score=70.0,
                            estimated_impact={"monthly_savings": round(overspend, 2),
                                              "months_saved": int(remaining / max(overspend, 1)) if overspend > 0 else 0},
                            affected_categories=[c["category"]],
                            actionable_steps=[f"Reduce {c['category']} by ₹{overspend:,.0f}/month",
                                              f"Set a monthly limit of ₹{c.get('limit', 0):,.0f}"],
                            assumptions=["Discretionary spending can be reduced without hardship"],
                            priority=2,
                        )
                        recommendations.append(rec)

            if health_score < 50 and g.priority != "critical":
                rec = GoalRecommendation(
                    user_id=user_id, goal_id=g.id,
                    recommendation_type="improve_health",
                    title=f"Improve financial health before pursuing '{g.name}'",
                    description=f"Your health score ({health_score}/100) is low. Consider postponing this goal.",
                    reasoning=f"Financial health score of {health_score} indicates unstable finances",
                    confidence_score=85.0,
                    estimated_impact={"health_score_improvement": "15-20 points expected in 3 months"},
                    affected_categories=[],
                    actionable_steps=["Focus on reducing essential expenses",
                                      "Build 3-month emergency fund first",
                                      "Revisit this goal when health score > 60"],
                    assumptions=["Following financial health recommendations will improve score"],
                    priority=3,
                )
                recommendations.append(rec)

        await self._repo.bulk_create(recommendations)
        return recommendations

    async def get_by_user(self, user_id: str, dismissed: bool | None = False) -> list[GoalRecommendation]:
        return await self._repo.get_by_user(user_id, dismissed)

    async def dismiss(self, rec_id: str) -> bool:
        return await self._repo.dismiss(rec_id)

    async def _get_active_goals(self, user_id: str) -> list[FinancialGoal]:
        from app.goal_planning.repositories.goal_repositories import MongoFinancialGoalRepository
        repo = MongoFinancialGoalRepository(self._db)
        return await repo.get_active(user_id)
