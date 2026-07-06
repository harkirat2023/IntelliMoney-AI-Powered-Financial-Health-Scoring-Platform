import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class SavingsOpportunityService:
    DISCRETIONARY_CATEGORIES = {"Entertainment", "Dining", "Shopping", "Travel", "Lifestyle", "Subscriptions", "Food Delivery"}

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def detect(self, user_id: str) -> list[dict]:
        now = datetime.utcnow()
        opportunities = []

        budget_usages = await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)

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

        cat_monthly: dict[str, list[float]] = {}
        for r in trend_results:
            cat = r["_id"]["category"]
            if cat not in cat_monthly:
                cat_monthly[cat] = []
            cat_monthly[cat].append(r["total"])

        total_monthly_pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "DEBIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$group": {
                "_id": {"month": {"$month": "$transaction_date"}, "year": {"$year": "$transaction_date"}},
                "total": {"$sum": "$amount"},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        total_results = await self._db.financial_transactions.aggregate(total_monthly_pipeline).to_list(length=None)
        monthly_totals = [r["total"] for r in total_results[-6:]] if total_results else []
        avg_total = sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0

        for bu in budget_usages:
            cat = bu.get("category", "")
            limit = bu.get("limit", 0)
            spent = bu.get("spent", 0)
            percentage = bu.get("percentage_used", 0)

            amounts = cat_monthly.get(cat, [])
            if len(amounts) < 2:
                continue
            amounts = amounts[-3:]
            avg_monthly = sum(amounts) / len(amounts)
            mom_change = ((amounts[-1] - amounts[-2]) / amounts[-2] * 100) if len(amounts) > 1 and amounts[-2] else 0

            if cat in self.DISCRETIONARY_CATEGORIES and percentage > 80 and avg_monthly > 2000:
                reduction_target = avg_monthly * 0.15
                target = avg_monthly * 0.85
                annual = reduction_target * 12
                confidence = 0.75 if percentage < 100 else 0.6

                opp = self._build_opportunity(
                    user_id, "reduce_spending", cat, reduction_target, annual,
                    f"Reduce {cat} spending by ₹{reduction_target:.0f}/month",
                    f"Your {cat} spending averages ₹{avg_monthly:.0f}/month at {percentage:.0f}% budget utilization. "
                    f"Reducing by 15% saves ₹{reduction_target:.0f}/month.",
                    confidence,
                    [f"Set a monthly limit of ₹{target:.0f} for {cat}.",
                     f"Track {cat} expenses weekly to stay within target.",
                     f"Look for alternatives or reduce frequency of {cat.lower()} purchases."],
                )
                opportunities.append(opp)

            if mom_change > 20 and avg_monthly > 3000 and cat in self.DISCRETIONARY_CATEGORIES:
                reduction = avg_monthly * 0.1
                annual = reduction * 12
                opp = self._build_opportunity(
                    user_id, "trend_reversal", cat, reduction, annual,
                    f"{cat} spending increased {mom_change:.0f}% — reverse the trend",
                    f"Your {cat} spending jumped {mom_change:.0f}% in the last month to ₹{amounts[-1]:.0f}. "
                    f"Reversing this trend saves ₹{reduction:.0f}/month.",
                    0.65,
                    [f"Review recent {cat.lower()} purchases for necessity.",
                     f"Set a weekly {cat.lower()} budget cap.",
                     f"Identify subscription services in {cat} that may be unused."],
                )
                opportunities.append(opp)

        total_monthly_spending = sum(amounts[-1] for amounts in cat_monthly.values() if amounts)
        if avg_total > 0:
            savings_target = avg_total * 0.05
            annual = savings_target * 12
            opp = self._build_opportunity(
                user_id, "overall_reduction", "All Categories", savings_target, annual,
                f"Reduce overall spending by 5% — save ₹{savings_target:.0f}/month",
                f"Your average monthly spending is ₹{avg_total:.0f}. A 5% reduction across all categories saves "
                f"₹{savings_target:.0f}/month (₹{annual:.0f}/year).",
                0.7,
                [f"Review all recurring subscriptions for unused services.",
                 f"Track every expense for 30 days to identify waste.",
                 f"Apply the 24-hour rule for non-essential purchases."],
            )
            opportunities.append(opp)

        subscriptions = await self._db.subscriptions.find({"user_id": user_id}).to_list(length=None)
        unused_subs = [s for s in subscriptions if not s.get("active", True)]
        if unused_subs:
            total_unused = sum(s.get("amount", 0) for s in unused_subs)
            annual = total_unused * 12
            opp = self._build_opportunity(
                user_id, "subscription_audit", "Subscriptions", total_unused, annual,
                f"Cancel {len(unused_subs)} unused subscription(s) — save ₹{total_unused:.0f}/month",
                f"You have {len(unused_subs)} inactive subscription(s) totaling ₹{total_unused:.0f}/month. "
                f"Cancelling them saves ₹{annual:.0f}/year.",
                0.9,
                [f"Review each inactive subscription and cancel if not needed.",
                 f"Contact providers to confirm cancellation.",
                 f"Set up monthly subscription audit reminder."],
            )
            opportunities.append(opp)

        health = await self._db.financial_health.find_one({"user_id": user_id}, sort=[("calculated_at", -1)])
        if health and health.get("score", 0) < 65:
            score_gap = 65 - health["score"]
            improvement = min(score_gap * 0.5, 8)
            opp = self._build_opportunity(
                user_id, "health_improvement", "Savings", avg_total * 0.1 if avg_total > 0 else 1000,
                (avg_total * 0.1 if avg_total > 0 else 1000) * 12,
                f"Improve Financial Health Score by ~{improvement:.0f} points through smart budgeting",
                f"Your Financial Health Score is {health['score']}. Optimizing budgets and increasing savings by 10% "
                f"can boost your score by approximately {improvement:.0f} points.",
                0.8,
                [f"Increase savings allocation by 10% of monthly income.",
                 f"Reduce discretionary spending categories.",
                 f"Set up automatic transfers to savings on payday."],
            )
            opportunities.append(opp)

        opportunities.sort(key=lambda o: o["potential_savings"], reverse=True)
        return opportunities

    def _build_opportunity(
        self, user_id: str, opp_type: str, category: str, monthly: float,
        annual: float, title: str, message: str, confidence: float, steps: list[str],
    ) -> dict:
        return {
            "user_id": user_id,
            "opportunity_type": opp_type,
            "category": category,
            "title": title,
            "message": message,
            "potential_savings": round(monthly, 2),
            "confidence_score": round(confidence, 2),
            "monthly_impact": round(monthly, 2),
            "annual_impact": round(annual, 2),
            "reasoning": message,
            "actionable_steps": steps,
        }
