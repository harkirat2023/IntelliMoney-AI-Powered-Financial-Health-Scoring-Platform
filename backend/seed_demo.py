import asyncio
import os
from datetime import date, timedelta

from bson import ObjectId

from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.services.ml_service import categorizer
from app.services.serializers import date_to_datetime, utc_now


DEMO_EMAIL = "demo@example.com"
DEMO_CLERK_USER_ID = os.getenv("DEMO_CLERK_USER_ID", "")


async def seed() -> None:
    await connect_to_mongo()
    db = get_database()

    existing = await db.users.find_one({"email": DEMO_EMAIL})
    if existing:
        user_id = existing["_id"]
    else:
        result = await db.users.insert_one(
            {
                "_id": ObjectId(),
                "name": "Demo User",
                "email": DEMO_EMAIL,
                "clerk_user_id": DEMO_CLERK_USER_ID or "demo_clerk_user",
                "monthly_income": 60000,
                "is_verified": True,
                "is_onboarded": True,
                "auth_provider": "clerk",
                "created_at": utc_now(),
            }
        )
        user_id = result.inserted_id

    await db.expenses.delete_many({"user_id": user_id})
    await db.budgets.delete_many({"user_id": user_id})

    today = date.today()
    sample_expenses = [
        (520, "grocery shopping", "UPI", today - timedelta(days=1)),
        (320, "uber ride to office", "Card", today - timedelta(days=2)),
        (1299, "netflix monthly subscription", "Card", today - timedelta(days=3)),
        (2200, "amazon headphones order", "UPI", today - timedelta(days=4)),
        (18000, "monthly house rent", "Bank Transfer", today - timedelta(days=5)),
        (750, "pharmacy medicines", "Cash", today - timedelta(days=7)),
    ]
    for amount, description, payment_method, expense_date in sample_expenses:
        category, _ = categorizer.predict(description)
        await db.expenses.insert_one(
            {
                "user_id": user_id,
                "amount": amount,
                "description": description,
                "category": category,
                "payment_method": payment_method,
                "date": date_to_datetime(expense_date),
                "created_at": utc_now(),
            }
        )

    for category, limit in [("Food", 8000), ("Transport", 4000), ("Entertainment", 2500), ("Shopping", 5000), ("Rent", 20000)]:
        await db.budgets.insert_one(
            {
                "user_id": user_id,
                "category": category,
                "limit": limit,
                "month": today.month,
                "year": today.year,
            }
        )

    await close_mongo_connection()
    print(f"Seeded demo account: {DEMO_EMAIL} (Clerk user: {DEMO_CLERK_USER_ID or 'demo_clerk_user'})")


if __name__ == "__main__":
    asyncio.run(seed())