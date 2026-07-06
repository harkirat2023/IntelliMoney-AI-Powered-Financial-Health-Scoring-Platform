import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import GOAL_TYPES

logger = logging.getLogger(__name__)


class GoalFeasibilityService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def analyze(self, user_id: str, goal_type: str, target_amount: float,
                      target_date: str = "",
                      monthly_contribution: float = 0.0) -> dict:
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])
        health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])

        income = cash.get("total_income", 0) if cash else 0
        expenses = cash.get("total_expenses", 0) if cash else 0
        net_savings = cash.get("net_savings", 0) if cash else 0
        health_score = health.get("score", 0) if health else 0
        budget_score = budget.get("budget_score", 0) if budget else 0

        available_monthly = max(0, net_savings)
        if monthly_contribution <= 0:
            effective_contribution = available_monthly * 0.7
        else:
            effective_contribution = min(monthly_contribution, available_monthly * 0.9)

        if effective_contribution <= 0:
            months_needed = 999
        else:
            months_needed = int(target_amount / effective_contribution)

        income_ratio = effective_contribution / max(income, 1)
        affordability = max(0, min(100, (1 - income_ratio) * 100))

        score = 0.0
        reasons = []
        suggestions = []

        if health_score >= 70:
            score += 30
        elif health_score >= 50:
            score += 15
            reasons.append("Financial health needs improvement")
        else:
            reasons.append("Low financial health score may impact goal feasibility")

        if budget_score >= 70:
            score += 25
        elif budget_score >= 50:
            score += 12
            reasons.append("Budget adherence could be better")

        income_expense_ratio = expenses / max(income, 1)
        if income_expense_ratio < 0.7:
            score += 20
        elif income_expense_ratio < 0.85:
            score += 10
            reasons.append("High expense-to-income ratio")
            suggestions.append("Consider reducing discretionary spending to free up savings")

        if months_needed <= 12:
            score += 15
        elif months_needed <= 36:
            score += 8
            suggestions.append(f"Consider extending your timeline — estimated {months_needed} months")
        else:
            suggestions.append(f"At current savings rate this will take ~{months_needed} months. Consider increasing monthly contribution.")

        if effective_contribution > 0:
            score += 10

        feasible = score >= 50
        risk_level = "low" if score >= 75 else "moderate" if score >= 50 else "high"

        if not feasible:
            reasons.append("Current financial situation does not support this goal comfortably")
            suggestions.append("Focus on improving overall financial health first")

        return {
            "feasible": feasible,
            "feasibility_score": round(score, 1),
            "affordability_score": round(affordability, 1),
            "estimated_months": months_needed,
            "monthly_savings_required": round(effective_contribution, 2),
            "risk_level": risk_level,
            "confidence_score": round(min(score + 10, 100), 1),
            "reasoning": " ".join(reasons) if reasons else "Goal appears feasible based on current finances",
            "suggestions": suggestions,
        }
