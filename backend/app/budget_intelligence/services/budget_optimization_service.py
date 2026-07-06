import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class BudgetOptimizationService:
    ESSENTIAL = {"Bills", "Rent", "Mortgage", "Groceries", "Transport", "Health", "Insurance", "Education"}
    DISCRETIONARY = {"Entertainment", "Dining", "Shopping", "Travel", "Lifestyle", "Subscriptions", "Food Delivery"}

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def optimize(self, user_id: str) -> dict:
        budget_usages = await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)

        suggestions = []
        total_current = 0.0
        total_suggested = 0.0
        insights = []

        for bu in budget_usages:
            cat = bu.get("category", "Other")
            limit = bu.get("limit", 0)
            spent = bu.get("spent", 0)
            percentage = bu.get("percentage_used", 0)
            total_current += limit

            if percentage > 100:
                suggested = round(spent * 1.05, 2)
                reason = f"{cat} spending exceeds budget by {percentage - 100:.0f}%. Increasing limit to {suggested:.0f} accommodates realistic spending."
                savings = 0
                confidence = 0.7
                insights.append(f"⚠ {cat} is overspent by ₹{spent - limit:.0f}. Consider increasing budget or reducing spending.")
            elif percentage > 80:
                suggested = round((limit + spent) / 2, 2)
                reason = f"{cat} is at {percentage:.0f}% utilization. A moderate increase to {suggested:.0f} provides buffer."
                savings = round(limit - suggested, 2) if suggested < limit else 0
                confidence = 0.8
            elif percentage < 50 and limit > 0:
                suggested = round(spent * 1.2, 2)
                reduction = round(limit - suggested, 2)
                if reduction > 0 and cat in self.DISCRETIONARY:
                    reason = f"{cat} uses only {percentage:.0f}% of budget. Reducing by ₹{reduction:.0f} frees up funds."
                    savings = reduction
                    confidence = 0.85
                    insights.append(f"💰 Reduce {cat} budget by ₹{reduction:.0f} — only {percentage:.0f}% used.")
                elif cat in self.ESSENTIAL:
                    suggested = round(limit, 2)
                    reason = f"{cat} is essential and under budget. Keeping limit at ₹{limit:.0f}."
                    savings = 0
                    confidence = 0.9
                else:
                    suggested = round(limit, 2)
                    reason = f"{cat} uses only {percentage:.0f}%. Current limit of ₹{limit:.0f} is reasonable."
                    savings = reduction if reduction > 0 else 0
                    confidence = 0.8
            else:
                suggested = round(limit, 2)
                reason = f"{cat} is on track at {percentage:.0f}% utilization. Current limit of ₹{limit:.0f} is optimal."
                savings = 0
                confidence = 0.9

            total_suggested += suggested
            suggestions.append({
                "category": cat,
                "current_limit": limit,
                "suggested_limit": suggested,
                "reason": reason,
                "potential_savings": max(0, limit - suggested),
                "confidence_score": round(confidence, 2),
            })

        potential_monthly_savings = max(0, total_current - total_suggested)
        if potential_monthly_savings > 0:
            insights.append(f"📊 Total potential monthly savings: ₹{potential_monthly_savings:.0f}")
        else:
            insights.append("✅ Budget is efficiently allocated.")

        suggestions.sort(key=lambda s: s["potential_savings"], reverse=True)

        return {
            "total_budget": round(total_current, 2),
            "total_suggested": round(total_suggested, 2),
            "total_current": round(total_current, 2),
            "potential_monthly_savings": round(potential_monthly_savings, 2),
            "suggestions": suggestions,
            "insights": insights,
        }
