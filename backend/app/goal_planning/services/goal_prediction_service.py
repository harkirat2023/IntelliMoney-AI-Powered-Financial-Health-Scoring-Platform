import logging
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import FinancialGoal, GoalPrediction
from app.goal_planning.repositories.goal_repositories import (
    GoalPredictionRepository, MongoGoalPredictionRepository,
)

logger = logging.getLogger(__name__)


class GoalPredictionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._repo: GoalPredictionRepository = MongoGoalPredictionRepository(db)
        self._db = db

    async def predict(self, goal: FinancialGoal) -> GoalPrediction:
        remaining = max(0, goal.target_amount - goal.current_amount)
        mc = goal.monthly_contribution

        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": goal.user_id}, sort=[("calculated_at", -1)])
        net_savings = cash.get("net_savings", 0) if cash else 0

        if mc <= 0:
            effective = max(0, net_savings) * 0.7
        else:
            effective = mc

        estimated_months = int(remaining / max(effective, 1)) if effective > 0 else 999

        best_months = max(1, int(remaining / max(effective * 1.2, 1)))
        worst_months = int(remaining / max(effective * 0.6, 1)) if effective > 0 else 999

        now = datetime.utcnow()

        def add_months(dt, n):
            month = dt.month - 1 + n
            year = dt.year + month // 12
            month = month % 12 + 1
            try:
                return dt.replace(year=year, month=month)
            except ValueError:
                import calendar
                last = calendar.monthrange(year, month)[1]
                return dt.replace(year=year, month=month, day=min(dt.day, last))

        predicted = add_months(now, estimated_months)
        best_case = add_months(now, best_months)
        worst_case = add_months(now, worst_months)

        projected = []
        running = goal.current_amount
        for m in range(1, min(estimated_months + 1, 60)):
            running += effective
            d = add_months(now, m)
            projected.append({
                "month": d.strftime("%Y-%m"),
                "projected_amount": round(running, 2),
                "remaining": round(max(0, goal.target_amount - running), 2),
            })
            if running >= goal.target_amount:
                break

        base_probability = min(95, max(10, 100 - (remaining / max(goal.target_amount, 1)) * 30))
        adjustment = min(10, net_savings / max(goal.monthly_contribution, 1) * 5) if goal.monthly_contribution > 0 else 0
        probability = min(99, base_probability + adjustment)

        prediction = GoalPrediction(
            goal_id=goal.id, user_id=goal.user_id,
            period=now.strftime("%Y-%m"),
            predicted_completion_date=predicted.strftime("%Y-%m-%d"),
            predicted_completion_amount=goal.target_amount,
            estimated_months_remaining=estimated_months,
            monthly_contribution_required=round(effective, 2),
            projected_amounts=projected,
            confidence_interval=[round(max(0, effective * 0.8), 2), round(effective * 1.2, 2)],
            best_case_date=best_case.strftime("%Y-%m-%d"),
            worst_case_date=worst_case.strftime("%Y-%m-%d"),
            probability_of_success=round(probability, 1),
        )
        return await self._repo.upsert(prediction)

    async def get_by_goal(self, goal_id: str) -> GoalPrediction | None:
        return await self._repo.get_by_goal(goal_id)
