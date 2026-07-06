import logging
from datetime import datetime
from statistics import pstdev

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class BudgetRiskService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def assess(self, user_id: str) -> dict:
        now = datetime.utcnow()
        period = f"{now.year}-{now.month:02d}"

        budget_usages = await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)

        pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "DEBIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$limit": 500},
            {"$group": {
                "_id": {"category": "$assigned_category", "month": {"$month": "$transaction_date"}, "year": {"$year": "$transaction_date"}},
                "total": {"$sum": "$amount"},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        results = await self._db.financial_transactions.aggregate(pipeline).to_list(length=None)

        cat_monthly: dict[str, list[float]] = {}
        for r in results:
            cat = r["_id"]["category"]
            if cat not in cat_monthly:
                cat_monthly[cat] = []
            cat_monthly[cat].append(r["total"])

        categories = []
        high_risk = medium_risk = low_risk = 0

        for bu in budget_usages:
            cat = bu.get("category", "Other")
            limit = bu.get("limit", 1)
            spent = bu.get("spent", 0)
            percentage = bu.get("percentage_used", 0)

            amounts = cat_monthly.get(cat, [])
            volatility = pstdev(amounts) / (sum(amounts) / len(amounts)) if len(amounts) > 1 and sum(amounts) > 0 else 0
            mom_changes = [(amounts[i] - amounts[i - 1]) / amounts[i - 1] * 100 for i in range(1, len(amounts)) if amounts[i - 1]]
            avg_mom = sum(mom_changes) / len(mom_changes) if mom_changes else 0

            risk_score = percentage * 0.5 + (volatility * 100) * 0.3 + max(0, avg_mom) * 0.2
            risk_score = min(100, risk_score)

            if risk_score >= 70:
                risk_level = "high"
                high_risk += 1
            elif risk_score >= 40:
                risk_level = "medium"
                medium_risk += 1
            else:
                risk_level = "low"
                low_risk += 1

            trend = "increasing" if avg_mom > 5 else "decreasing" if avg_mom < -5 else "stable"

            categories.append({
                "category": cat,
                "risk_level": risk_level,
                "risk_score": round(risk_score, 1),
                "percentage_used": percentage,
                "trend": trend,
            })

        scores = [c["risk_score"] for c in categories]
        overall_score = sum(scores) / len(scores) if scores else 0
        overall_level = "high" if overall_score >= 70 else "medium" if overall_score >= 40 else "low"
        volatility_score = pstdev(scores) if len(scores) > 1 else 0

        overspending = [c for c in categories if c["percentage_used"] > 100]
        recurring = await self._assess_recurring_risk(user_id)

        trend_risk = sum(1 for c in categories if c["trend"] == "increasing")
        total_cat = len(categories)
        trend_dir = "deteriorating" if trend_risk > total_cat / 2 else "improving" if trend_risk < total_cat / 3 else "stable"

        return {
            "period": period,
            "overall_risk_level": overall_level,
            "overall_risk_score": round(overall_score, 1),
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "volatility_score": round(volatility_score, 1),
            "trend_direction": trend_dir,
            "categories": categories,
        }

    async def _assess_recurring_risk(self, user_id: str) -> list[dict]:
        recurring = await self._db.recurring_expenses.find({"user_id": user_id}).to_list(length=None)
        high_risk_items = []
        for rec in recurring:
            amount = rec.get("amount", 0)
            frequency = rec.get("frequency", "monthly")
            if amount > 5000 and frequency == "monthly":
                high_risk_items.append({"name": rec.get("description", "Unknown"), "amount": amount, "risk": "high"})
            elif amount > 2000:
                high_risk_items.append({"name": rec.get("description", "Unknown"), "amount": amount, "risk": "medium"})
        return high_risk_items
