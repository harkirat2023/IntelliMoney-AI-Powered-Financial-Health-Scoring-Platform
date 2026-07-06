import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class BudgetRecommendationService:
    ESSENTIAL = {"Bills", "Rent", "Mortgage", "Groceries", "Transport", "Health", "Insurance", "Education"}
    DISCRETIONARY = {"Entertainment", "Dining", "Shopping", "Travel", "Lifestyle", "Subscriptions", "Food Delivery"}

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def generate(self, user_id: str) -> list[dict]:
        recommendations = []

        budget_usages = await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)
        financial_health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )

        trends_pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "DEBIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$limit": 500},
            {"$group": {
                "_id": {"category": "$assigned_category", "month": {"$month": "$transaction_date"}, "year": {"$year": "$transaction_date"}},
                "total": {"$sum": "$amount"},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        trend_results = await self._db.financial_transactions.aggregate(trends_pipeline).to_list(length=None)

        cat_monthly: dict[str, list] = {}
        for r in trend_results:
            cat = r["_id"]["category"]
            if cat not in cat_monthly:
                cat_monthly[cat] = []
            cat_monthly[cat].append(r["total"])

        for bu in budget_usages:
            cat = bu.get("category", "")
            limit = bu.get("limit", 0)
            spent = bu.get("spent", 0)
            percentage = bu.get("percentage_used", 0)
            amounts = cat_monthly.get(cat, [])

            if percentage > 100 and spent > 0:
                overage = spent - limit
                months_data = amounts[-3:] if len(amounts) >= 3 else amounts
                is_recurring = all(m > limit * 0.9 for m in months_data) if months_data and limit > 0 else False
                trend_text = "consistently" if is_recurring else "this month"
                steps = [
                    f"Review {cat.lower()} expenses for non-essential items.",
                    f"Set a reduced weekly allowance for {cat}.",
                    f"Look for cost-saving alternatives in {cat}.",
                ]
                if cat in self.DISCRETIONARY:
                    steps.append(f"Consider a spending freeze on {cat} for 2 weeks.")

                rec = self._make_rec(
                    user_id, cat, "overspending",
                    f"Reduce {cat} overspending by ₹{overage:.0f}/month",
                    f"You {trend_text} overspent on {cat} by ₹{overage:.0f} ({percentage:.0f}% of budget).",
                    percentage, 80, overage, 0.85 if is_recurring else 0.7,
                    [cat], f"Saves ₹{overage:.0f}/month immediately.", steps,
                )
                recommendations.append(rec)

            elif percentage > 80 and cat in self.DISCRETIONARY:
                suggested = spent * 0.85
                reduction = spent - suggested
                rec = self._make_rec(
                    user_id, cat, "reduce_spending",
                    f"Reduce {cat} spending by ₹{reduction:.0f}/month",
                    f"Your {cat} spending is at {percentage:.0f}% of budget. Reducing by 15% saves ₹{reduction:.0f}/month.",
                    spent, suggested, reduction, 0.75,
                    [cat], f"Saves ₹{reduction:.0f}/month (₹{reduction * 12:.0f}/year).",
                    [f"Set a daily or weekly cap for {cat.lower()}.",
                     f"Use cash instead of card for {cat.lower()} purchases.",
                     f"Track {cat.lower()} expenses in real-time."],
                )
                recommendations.append(rec)

            elif percentage < 50 and limit > 0 and cat in self.DISCRETIONARY:
                reduction = limit - spent
                if reduction > 500:
                    rec = self._make_rec(
                        user_id, cat, "reallocate",
                        f"Reallocate ₹{reduction:.0f} from {cat} to savings",
                        f"You use only {percentage:.0f}% of your {cat} budget. Moving ₹{reduction:.0f} to savings optimizes your finances.",
                        limit, spent + reduction * 0.5, reduction, 0.8,
                        ["Savings", cat], f"Increases savings by ₹{reduction:.0f}/month.",
                        [f"Reduce {cat} budget to ₹{spent * 1.1:.0f}.",
                         f"Auto-transfer the difference to savings on payday."],
                    )
                    recommendations.append(rec)

        if financial_health and financial_health.get("score", 0) < 65:
            score = financial_health["score"]
            gap = 65 - score
            points = min(gap * 0.5, 8)
            rec = self._make_rec(
                user_id, "Overall", "health_improvement",
                f"Improve Financial Health Score by ~{points:.0f} points",
                f"Your Financial Health Score is {score}. Smart budget optimization can improve it by ~{points:.0f} points.",
                score, 65, 0, 0.8,
                list(set(bu.get("category", "") for bu in budget_usages)),
                f"A higher score improves loan eligibility and financial stability.",
                [f"Increase savings rate by 5% of income.",
                 f"Reduce discretionary spending by 10%.",
                 f"Set up automatic bill payments to avoid late fees."],
            )
            recommendations.append(rec)

        income_trend = await self._check_income_trend(user_id)
        if income_trend:
            recommendations.append(income_trend)

        recommendations.sort(key=lambda r: r["confidence_score"], reverse=True)
        return recommendations

    def _make_rec(
        self, user_id, category, rec_type, title, message,
        current_val, target_val, savings, confidence,
        affected_cats, impact, steps,
    ) -> dict:
        priority = "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low"
        return {
            "user_id": user_id,
            "category": category,
            "recommendation_type": rec_type,
            "title": title,
            "message": message,
            "current_value": round(current_val, 1),
            "target_value": round(target_val, 1),
            "potential_savings": round(savings, 2),
            "confidence_score": round(confidence, 2),
            "priority": priority,
            "reasoning": f"Based on {category.lower()} spending analysis and budget utilization patterns.",
            "affected_categories": affected_cats,
            "estimated_impact": impact,
            "actionable_steps": steps,
        }

    async def _check_income_trend(self, user_id: str) -> dict | None:
        pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "CREDIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$limit": 200},
            {"$group": {
                "_id": {"month": {"$month": "$transaction_date"}, "year": {"$year": "$transaction_date"}},
                "total": {"$sum": "$amount"},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        results = await self._db.financial_transactions.aggregate(pipeline).to_list(length=None)
        if len(results) < 2:
            return None
        incomes = [r["total"] for r in results[-3:]]
        if len(incomes) >= 2:
            change = ((incomes[-1] - incomes[-2]) / incomes[-2] * 100) if incomes[-2] else 0
            if change < -15:
                return self._make_rec(
                    user_id, "Income", "income_decline",
                    f"Income dropped {abs(change):.0f}% — review budget allocations",
                    f"Your monthly income decreased by {abs(change):.0f}%. Consider temporary budget adjustments.",
                    incomes[-1], incomes[-2], 0, 0.85,
                    list(set(bu["category"] for bu in (results if isinstance(results, list) else []))),
                    "Protects against cash flow issues during income transition.",
                    ["Review all non-essential spending categories.",
                     "Build a 3-month reduced budget scenario.",
                     "Prioritize essential expenses and savings."],
                )
        return None
