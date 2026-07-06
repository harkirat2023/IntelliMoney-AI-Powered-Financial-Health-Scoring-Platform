import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_intelligence import BudgetIntelligence
from app.budget_intelligence.services.category_trend_service import CategoryTrendService

logger = logging.getLogger("intellimoney")


class SmartBudgetService:
    ESSENTIAL_CATEGORIES = {"Bills", "Rent", "Mortgage", "Groceries", "Transport", "Health", "Insurance", "Education"}
    DISCRETIONARY_CATEGORIES = {"Entertainment", "Dining", "Shopping", "Travel", "Lifestyle", "Subscriptions", "Food Delivery"}

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._trend_service = CategoryTrendService(db)

    async def generate_budget(self, user_id: str) -> BudgetIntelligence:
        now = datetime.utcnow()
        period = f"{now.year}-{now.month:02d}"

        budget_usages = await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)
        financial_health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        trends = await self._trend_service.analyze(user_id, 6)

        categories = []
        total_budget = 0.0
        total_spent = 0.0
        total_suggested = 0.0
        on_track_count = 0
        warning_count = 0
        over_count = 0

        seen_categories = set()

        for bu in budget_usages:
            cat = bu.get("category", "Other")
            seen_categories.add(cat)
            limit = bu.get("limit", 0)
            spent = bu.get("spent", 0)
            percentage = bu.get("percentage_used", 0)
            state = bu.get("state", "safe")
            trend_data = trends.get(cat, {})
            mom_change = trend_data.get("month_over_month_change", 0)
            trend_dir = trend_data.get("trend_direction", "stable")

            suggested = self._suggest_limit(cat, limit, percentage, mom_change)

            categories.append({
                "category": cat,
                "limit": limit,
                "spent": spent,
                "suggested": round(suggested, 2),
                "percentage_used": percentage,
                "state": state,
                "trend": trend_dir,
                "month_over_month_change": mom_change,
            })
            total_budget += limit
            total_spent += spent
            total_suggested += suggested
            if state == "safe":
                on_track_count += 1
            elif state == "warning":
                warning_count += 1
            else:
                over_count += 1

        for cat, trend_data in trends.items():
            if cat not in seen_categories:
                avg = trend_data.get("average_monthly", 0)
                if avg > 0:
                    suggested = self._suggest_limit(cat, 0, avg, trend_data.get("month_over_month_change", 0))
                    categories.append({
                        "category": cat,
                        "limit": 0,
                        "spent": avg,
                        "suggested": round(suggested, 2),
                        "percentage_used": 100 if avg > 0 else 0,
                        "state": "over",
                        "trend": trend_data.get("trend_direction", "stable"),
                        "month_over_month_change": trend_data.get("month_over_month_change", 0),
                    })
                    total_spent += avg
                    total_suggested += suggested
                    over_count += 1

        categories.sort(key=lambda c: c["spent"], reverse=True)
        potential_savings = max(0, total_suggested - total_budget)
        budget_score = self._calculate_score(on_track_count, warning_count, over_count, len(categories))

        return BudgetIntelligence(
            user_id=user_id,
            period=period,
            budget_score=budget_score,
            total_budget=total_budget,
            total_spent=total_spent,
            total_suggested=total_suggested,
            potential_savings=potential_savings,
            category_count=len(categories),
            on_track_count=on_track_count,
            warning_count=warning_count,
            over_count=over_count,
            categories=categories,
            calculated_at=now,
        )

    def _suggest_limit(self, category: str, current_limit: float, spent: float, mom_change: float) -> float:
        if current_limit <= 0 and spent <= 0:
            return 0
        if current_limit <= 0:
            base = spent * 1.1
        elif spent > current_limit * 1.2:
            base = spent * 1.05
        elif spent < current_limit * 0.5:
            base = spent * 1.2
        else:
            base = (current_limit + spent) / 2

        if mom_change > 10:
            base *= 1.08
        elif mom_change < -10:
            base *= 0.92

        if category in self.ESSENTIAL_CATEGORIES:
            base = max(base, spent * 0.95)
        elif category in self.DISCRETIONARY_CATEGORIES:
            base = min(base, max(spent * 0.9, current_limit * 0.8) if current_limit > 0 else base)

        return max(base, 0)

    def _calculate_score(self, on_track: int, warning: int, over: int, total: int) -> float:
        if total == 0:
            return 0
        score = (on_track * 100 + warning * 50 + over * 0) / total
        return round(score, 1)
