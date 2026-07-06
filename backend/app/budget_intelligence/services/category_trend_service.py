import logging
from datetime import datetime
from statistics import pstdev

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")


class CategoryTrendService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def analyze(self, user_id: str, months: int = 6) -> dict[str, dict]:
        pipeline = [
            {"$match": {"user_id": user_id, "transaction_type": "DEBIT"}},
            {"$sort": {"transaction_date": -1}},
            {"$limit": 500},
            {"$group": {
                "_id": {"category": "$assigned_category", "month": {"$month": "$transaction_date"}, "year": {"$year": "$transaction_date"}},
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        results = await self._db.financial_transactions.aggregate(pipeline).to_list(length=None)

        period_map: dict[str, dict[str, float]] = {}
        for r in results:
            key = r["_id"]
            period = f"{key['year']}-{key['month']:02d}"
            if period not in period_map:
                period_map[period] = {}
            period_map[period][key["category"]] = r["total"]

        periods = sorted(period_map.keys())[-months:]
        categories: dict[str, dict] = {}

        for period in periods:
            for cat, total in period_map.get(period, {}).items():
                if cat not in categories:
                    categories[cat] = {"totals": [], "count": 0, "total_all": 0}
                categories[cat]["totals"].append(total)
                categories[cat]["count"] += 1
                categories[cat]["total_all"] += total

        trends = {}
        for cat, data in categories.items():
            totals = data["totals"]
            avg = sum(totals) / len(totals) if totals else 0
            change = ((totals[-1] - totals[0]) / totals[0] * 100) if len(totals) > 1 and totals[0] else 0
            volatility = pstdev(totals) / avg if avg > 0 else 0
            mom_changes = []
            for i in range(1, len(totals)):
                if totals[i - 1]:
                    mom_changes.append((totals[i] - totals[i - 1]) / totals[i - 1] * 100)
            avg_mom = sum(mom_changes) / len(mom_changes) if mom_changes else 0
            trend_dir = "increasing" if avg_mom > 5 else "decreasing" if avg_mom < -5 else "stable"

            trends[cat] = {
                "category": cat,
                "average_monthly": round(avg, 2),
                "latest_monthly": round(totals[-1], 2) if totals else 0,
                "total_over_period": round(data["total_all"], 2),
                "change_percentage": round(change, 1),
                "trend_direction": trend_dir,
                "volatility": round(volatility, 3),
                "month_over_month_change": round(avg_mom, 1),
                "months_analyzed": len(totals),
            }
        return trends

    async def get_top_trends(self, user_id: str, months: int = 6, top_n: int = 10) -> list[dict]:
        trends = await self.analyze(user_id, months)
        sorted_trends = sorted(trends.values(), key=lambda x: abs(x["change_percentage"]), reverse=True)
        return sorted_trends[:top_n]
