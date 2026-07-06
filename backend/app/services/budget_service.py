from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.analytics_service import get_month_expenses
from app.services.serializers import serialize_document, utc_now


async def get_budget_status(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    now = utc_now()
    budgets = [
        serialize_document(item)
        async for item in db.budgets.find(
            {"user_id": ObjectId(user_id), "month": now.month, "year": now.year}
        )
    ]
    expenses = await get_month_expenses(db, user_id, now.year, now.month)
    spent_by_category: dict[str, float] = {}
    for expense in expenses:
        spent_by_category[expense["category"]] = (
            spent_by_category.get(expense["category"], 0) + expense["amount"]
        )

    statuses = []
    for budget in budgets:
        spent = round(spent_by_category.get(budget["category"], 0), 2)
        limit = float(budget["limit"])
        percentage = round((spent / limit) * 100, 2) if limit else 0
        state = "safe"
        if percentage >= 100:
            state = "over"
        elif percentage >= 80:
            state = "warning"
        statuses.append(
            {
                "id": budget["id"],
                "category": budget["category"],
                "limit": limit,
                "spent": spent,
                "remaining": round(limit - spent, 2),
                "percentage_used": percentage,
                "state": state,
            }
        )
    return statuses
