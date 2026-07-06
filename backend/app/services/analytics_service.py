from collections import defaultdict
from datetime import datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.serializers import month_bounds, serialize_document, utc_now


async def get_month_expenses(
    db: AsyncIOMotorDatabase, user_id: str, year: int, month: int
) -> list[dict[str, Any]]:
    start, end = month_bounds(year, month)
    cursor = db.expenses.find(
        {"user_id": ObjectId(user_id), "date": {"$gte": start, "$lt": end}}
    ).sort("date", -1)
    return [serialize_document(item) async for item in cursor]


async def get_summary(db: AsyncIOMotorDatabase, user: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    expenses = await get_month_expenses(db, str(user["_id"]), now.year, now.month)
    total_spending = round(sum(item["amount"] for item in expenses), 2)
    monthly_income = float(user.get("monthly_income", 0))
    savings_estimate = round(monthly_income - total_spending, 2)
    savings_rate = round((savings_estimate / monthly_income) * 100, 2) if monthly_income else 0

    by_category: dict[str, float] = defaultdict(float)
    for item in expenses:
        by_category[item["category"]] += item["amount"]
    top_category = max(by_category, key=by_category.get) if by_category else None

    return {
        "monthly_income": monthly_income,
        "total_spending": total_spending,
        "savings_estimate": savings_estimate,
        "savings_rate": savings_rate,
        "expense_count": len(expenses),
        "top_category": top_category,
    }


async def category_breakdown(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    now = utc_now()
    expenses = await get_month_expenses(db, user_id, now.year, now.month)
    totals: dict[str, float] = defaultdict(float)
    for item in expenses:
        totals[item["category"]] += item["amount"]
    return [{"label": key, "value": round(value, 2)} for key, value in totals.items()]


async def payment_methods(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    now = utc_now()
    expenses = await get_month_expenses(db, user_id, now.year, now.month)
    totals: dict[str, float] = defaultdict(float)
    for item in expenses:
        totals[item["payment_method"]] += item["amount"]
    return [{"label": key, "value": round(value, 2)} for key, value in totals.items()]


async def monthly_spending(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    now = utc_now()
    points: list[dict[str, Any]] = []
    for offset in range(5, -1, -1):
        month = now.month - offset
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        expenses = await get_month_expenses(db, user_id, year, month)
        points.append(
            {
                "label": datetime(year, month, 1).strftime("%b"),
                "value": round(sum(item["amount"] for item in expenses), 2),
            }
        )
    return points


async def recent_expenses(db: AsyncIOMotorDatabase, user_id: str, limit: int = 8) -> list[dict[str, Any]]:
    cursor = db.expenses.find({"user_id": ObjectId(user_id)}).sort("date", -1).limit(limit)
    return [serialize_document(item) async for item in cursor]
