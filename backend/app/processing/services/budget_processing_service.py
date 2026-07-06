import logging
from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.repositories.budget_usage_repository import MongoBudgetUsageRepository

logger = logging.getLogger("intellimoney")
from app.utils.date_utils import month_bounds, utc_now


class BudgetProcessingService:
    def __init__(self, db: AsyncIOMotorDatabase, budget_usage_repo: MongoBudgetUsageRepository):
        self._db = db
        self._budget_usage_repo = budget_usage_repo

    async def update_budget_usage(self, user_id: str) -> list[dict]:
        now = utc_now()
        month, year = now.month, now.year

        budgets = [
            doc async for doc in self._db.budgets.find(
                {"user_id": user_id, "month": month, "year": year}
            )
        ]
        if not budgets:
            logger.info("budget_usage_no_budgets user=%s month=%d year=%d", user_id, month, year)
            return []

        start, end = month_bounds(year, month)
        expenses = [
            doc async for doc in self._db.expenses.find({
                "user_id": user_id,
                "date": {"$gte": start, "$lte": end},
            })
        ]

        spent_by_category: dict[str, float] = defaultdict(float)
        for exp in expenses:
            cat = exp.get("category", "Other")
            spent_by_category[cat] += float(exp.get("amount", 0))

        states = []
        for budget in budgets:
            category = budget["category"]
            limit = float(budget["limit"])
            spent = round(spent_by_category.get(category, 0), 2)
            percentage = round((spent / limit) * 100, 2) if limit > 0 else 0
            state = "safe"
            if percentage >= 100:
                state = "over"
            elif percentage >= 80:
                state = "warning"

            await self._budget_usage_repo.upsert(
                user_id=user_id,
                budget_id=str(budget["_id"]),
                month=month,
                year=year,
                limit=limit,
                spent=spent,
                remaining=round(limit - spent, 2),
                percentage_used=percentage,
                state=state,
                category=category,
                updated_at=now,
            )
            states.append({
                "budget_id": str(budget["_id"]),
                "category": category,
                "limit": limit,
                "spent": spent,
                "percentage_used": percentage,
                "state": state,
            })

        return states
