#!/usr/bin/env python3
"""
Standalone script to create all MongoDB indexes.
Can be run independently: python scripts/create_indexes.py
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings


async def create_indexes():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db]

    print(f"Connected to MongoDB: {settings.mongodb_url}/{settings.mongodb_db}")

    await db.users.create_index("email", unique=True)
    print("  users.email (unique)")

    await db.expenses.create_index([("user_id", 1), ("date", -1)])
    print("  expenses.(user_id, date)")

    await db.budgets.create_index(
        [("user_id", 1), ("category", 1), ("month", 1), ("year", 1)],
        unique=True,
    )
    print("  budgets.(user_id, category, month, year) (unique)")

    await db.budget_alerts.create_index([("user_id", 1), ("created_at", -1)])
    await db.budget_alerts.create_index(
        [("user_id", 1), ("budget_id", 1), ("threshold", 1)], unique=True
    )
    print("  budget_alerts indexes")

    await db.financial_scores.create_index([("user_id", 1), ("calculated_at", -1)])
    print("  financial_scores.(user_id, calculated_at)")

    await db.recommendations.create_index([("user_id", 1), ("created_at", -1)])
    print("  recommendations.(user_id, created_at)")

    await db.spending_anomalies.create_index([("user_id", 1), ("created_at", -1)])
    await db.spending_anomalies.create_index([("user_id", 1), ("is_read", 1)])
    print("  spending_anomalies indexes")

    await db.budget_suggestions.create_index([("user_id", 1), ("is_applied", 1)])
    print("  budget_suggestions.(user_id, is_applied)")

    await db.financial_reports.create_index([("user_id", 1), ("generated_at", -1)])
    await db.financial_reports.create_index([("user_id", 1), ("report_type", 1)])
    print("  financial_reports indexes")

    await db.recurring_expenses.create_index([("user_id", 1), ("is_active", 1)])
    await db.recurring_expenses.create_index([("user_id", 1), ("next_expected_date", 1)])
    print("  recurring_expenses indexes")

    await db.subscriptions.create_index([("user_id", 1), ("is_active", 1)])
    await db.subscriptions.create_index([("user_id", 1), ("next_payment_date", 1)])
    print("  subscriptions indexes")

    client.close()
    print("\nAll indexes created successfully.")


if __name__ == "__main__":
    asyncio.run(create_indexes())
