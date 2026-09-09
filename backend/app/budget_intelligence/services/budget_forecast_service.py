import logging
from datetime import datetime
from statistics import pstdev

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class BudgetForecastService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def forecast(self, user_id: str) -> dict:
        now = datetime.utcnow()
        period = f"{now.year}-{now.month:02d}"

        pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "DEBIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$limit": 500},
            {"$group": {
                "_id": {
                    "category": "$assigned_category",
                    "month": {"$month": "$transaction_date"},
                    "year": {"$year": "$transaction_date"},
                },
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
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

        budget_usages = {bu["category"]: bu for bu in await self._db.budget_usage.find({"user_id": user_id}).to_list(length=None)}

        predictions = []
        for cat, amounts in cat_monthly.items():
            if len(amounts) < 2:
                continue
            amounts = amounts[-6:]
            avg = sum(amounts) / len(amounts)
            std = pstdev(amounts) if len(amounts) > 1 else 0
            last = amounts[-1]
            mom_changes = [(amounts[i] - amounts[i - 1]) / amounts[i - 1] * 100 for i in range(1, len(amounts)) if amounts[i - 1]]
            avg_mom = sum(mom_changes) / len(mom_changes) if mom_changes else 0
            trend_dir = "increasing" if avg_mom > 5 else "decreasing" if avg_mom < -5 else "stable"

            predicted = last * (1 + avg_mom / 100) if abs(avg_mom) > 2 else last * 1.02

            bu = budget_usages.get(cat, {})
            limit = bu.get("limit", 0)
            predicted_util = (predicted / limit * 100) if limit > 0 else 100

            if predicted_util > 100:
                trend_dir = "increasing"

            predictions.append({
                "category": cat,
                "predicted_spending": round(predicted, 2),
                "predicted_utilization": round(predicted_util, 1),
                "confidence_upper": round(predicted + std * 1.5, 2),
                "confidence_lower": round(max(0, predicted - std * 1.5), 2),
                "trend_direction": trend_dir,
                "months_analyzed": len(amounts),
            })

        by_category = await self._db.budget_usage.find({"user_id": user_id}).sort("percentage_used", -1).to_list(length=None)

        return {
            "period": period,
            "predictions": predictions,
        }
