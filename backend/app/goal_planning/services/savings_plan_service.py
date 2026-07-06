import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SavingsPlanService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def generate_plan(self, user_id: str, target_amount: float,
                            monthly_contribution: float = 0.0,
                            current_amount: float = 0.0) -> dict:
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)])

        net_savings = cash.get("net_savings", 0) if cash else 0
        budget_potential = 0.0

        if budget:
            categories = budget.get("categories", [])
            overspent = [c for c in categories if c.get("status") == "over"]
            for c in overspent:
                budget_potential += max(0, c.get("spent", 0) - c.get("limit", 0))

        max_available = max(0, net_savings)
        if monthly_contribution <= 0:
            monthly_contribution = min(max_available * 0.7, target_amount / max(1, target_amount / max(1, max_available)))

        effective = min(monthly_contribution, max_available * 0.9)
        remaining = max(0, target_amount - current_amount)
        months = int(remaining / max(effective, 1)) if effective > 0 else 999

        budget_adjustments = []
        discretionary_categories = ["food_delivery", "entertainment", "shopping",
                                     "dining", "subscriptions", "lifestyle"]
        if budget:
            for c in budget.get("categories", []):
                if c.get("category") in discretionary_categories and c.get("state") in ("warning", "over"):
                    overspend = max(0, c.get("spent", 0) - c.get("limit", 0))
                    if overspend > 0:
                        budget_adjustments.append({
                            "category": c["category"],
                            "current_spend": round(c["spent"], 2),
                            "recommended_reduction": round(min(overspend, c["spent"] * 0.3), 2),
                            "potential_savings": round(overspend, 2),
                        })

        potential_savings = sum(a["potential_savings"] for a in budget_adjustments)
        if potential_savings > 0:
            optimized_contribution = min(effective + potential_savings * 0.5, max_available * 0.9)
            optimized_months = int(remaining / max(optimized_contribution, 1))
        else:
            optimized_contribution = effective
            optimized_months = months

        return {
            "monthly_contribution": round(effective, 2),
            "optimized_contribution": round(optimized_contribution, 2),
            "estimated_months": months,
            "optimized_months": optimized_months,
            "remaining_amount": round(remaining, 2),
            "max_available_savings": round(max_available, 2),
            "budget_adjustments": budget_adjustments,
            "discretionary_savings_potential": round(potential_savings, 2),
            "income_usage_percentage": round(effective / max(net_savings, 1) * 100, 1) if net_savings > 0 else 0,
        }
