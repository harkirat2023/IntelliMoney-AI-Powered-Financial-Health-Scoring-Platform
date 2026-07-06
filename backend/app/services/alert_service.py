from collections import defaultdict
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.analytics_service import get_month_expenses
from app.services.notification_service import notifier
from app.services.serializers import serialize_document, utc_now


ALERT_THRESHOLDS = [75, 90, 100]


def threshold_for_percentage(percentage: float) -> int | None:
    reached = [threshold for threshold in ALERT_THRESHOLDS if percentage >= threshold]
    return max(reached) if reached else None


def alert_message(category: str, percentage: float, threshold: int) -> str:
    if threshold >= 100:
        return f"{category} budget exceeded at {percentage:.2f}% usage."
    return f"{category} budget reached {threshold}% usage. Current usage is {percentage:.2f}%."


async def sync_budget_alerts(db: AsyncIOMotorDatabase, user: dict[str, Any]) -> None:
    user_id = user["_id"]
    now = utc_now()
    budgets = [
        item
        async for item in db.budgets.find(
            {"user_id": user_id, "month": now.month, "year": now.year}
        )
    ]
    expenses = await get_month_expenses(db, str(user_id), now.year, now.month)
    spent_by_category: dict[str, float] = defaultdict(float)
    for expense in expenses:
        spent_by_category[expense["category"]] += expense["amount"]

    for budget in budgets:
        limit = float(budget["limit"])
        if limit <= 0:
            continue
        spent = spent_by_category.get(budget["category"], 0)
        percentage = round((spent / limit) * 100, 2)
        threshold = threshold_for_percentage(percentage)
        if threshold is None:
            continue

        existing = await db.budget_alerts.find_one(
            {
                "user_id": user_id,
                "budget_id": budget["_id"],
                "threshold": threshold,
            }
        )
        if existing:
            await db.budget_alerts.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "percentage": percentage,
                        "message": alert_message(budget["category"], percentage, threshold),
                    }
                },
            )
            continue

        message = alert_message(budget["category"], percentage, threshold)
        await db.budget_alerts.insert_one(
            {
                "user_id": user_id,
                "budget_id": budget["_id"],
                "threshold": threshold,
                "percentage": percentage,
                "message": message,
                "created_at": utc_now(),
                "read": False,
                "email_queued": False,
                "email_sent_at": None,
            }
        )
        if user.get("email"):
            await notifier.send_budget_alert(user["email"], message)


async def list_alerts(db: AsyncIOMotorDatabase, user: dict[str, Any]) -> list[dict[str, Any]]:
    await sync_budget_alerts(db, user)
    cursor = db.budget_alerts.find({"user_id": user["_id"]}).sort("created_at", -1)
    return [serialize_document(item) async for item in cursor]


async def mark_alert_read(
    db: AsyncIOMotorDatabase, user: dict[str, Any], alert_id: str
) -> dict[str, Any] | None:
    if not ObjectId.is_valid(alert_id):
        return None
    object_id = ObjectId(alert_id)
    await db.budget_alerts.update_one(
        {"_id": object_id, "user_id": user["_id"]},
        {"$set": {"read": True}},
    )
    alert = await db.budget_alerts.find_one({"_id": object_id, "user_id": user["_id"]})
    return serialize_document(alert) if alert else None
