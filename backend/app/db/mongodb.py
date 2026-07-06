from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.mongodb_db]
    await database.users.create_index("email", unique=True)
    await database.expenses.create_index([("user_id", 1), ("date", -1)])
    await database.budgets.create_index(
        [("user_id", 1), ("category", 1), ("month", 1), ("year", 1)],
        unique=True,
    )
    await database.budget_alerts.create_index([("user_id", 1), ("created_at", -1)])
    await database.budget_alerts.create_index(
        [("user_id", 1), ("budget_id", 1), ("threshold", 1)],
        unique=True,
    )
    await database.financial_scores.create_index([("user_id", 1), ("calculated_at", -1)])
    await database.recommendations.create_index([("user_id", 1), ("created_at", -1)])
    await database.spending_anomalies.create_index([("user_id", 1), ("created_at", -1)])
    await database.spending_anomalies.create_index([("user_id", 1), ("is_read", 1)])
    await database.budget_suggestions.create_index([("user_id", 1), ("is_applied", 1)])
    await database.financial_reports.create_index([("user_id", 1), ("generated_at", -1)])
    await database.financial_reports.create_index([("user_id", 1), ("report_type", 1)])
    await database.recurring_expenses.create_index([("user_id", 1), ("is_active", 1)])
    await database.recurring_expenses.create_index([("user_id", 1), ("next_expected_date", 1)])
    await database.subscriptions.create_index([("user_id", 1), ("is_active", 1)])
    await database.subscriptions.create_index([("user_id", 1), ("next_payment_date", 1)])
    await database.bank_accounts.create_index([("user_id", 1), ("connection_status", 1)])
    await database.bank_accounts.create_index([("user_id", 1), ("provider", 1)])
    await database.bank_accounts.create_index([("consent_handle", 1)], unique=True, sparse=True)
    await database.bank_accounts.create_index([("consent_expiry", 1)], expireAfterSeconds=0)

    await database.consents.create_index([("user_id", 1), ("bank_account_id", 1)])
    await database.consents.create_index([("bank_account_id", 1)])
    await database.consents.create_index([("consent_status", 1), ("expires_at", 1)])

    await database.import_preferences.create_index(
        [("user_id", 1), ("bank_account_id", 1)], unique=True,
    )
    await database.import_preferences.create_index([("bank_account_id", 1)])

    await database.bank_transactions.create_index(
        [("user_id", 1), ("bank_account_id", 1), ("transaction_date", -1)],
    )
    await database.bank_transactions.create_index(
        [("provider_account_id", 1), ("transaction_id", 1)], unique=True,
    )

    await database.sync_logs.create_index(
        [("user_id", 1), ("bank_account_id", 1), ("created_at", -1)],
    )
    await database.sync_logs.create_index([("user_id", 1), ("status", 1)])

    await database.financial_transactions.create_index([("user_id", 1), ("transaction_date", -1)])
    await database.financial_transactions.create_index([("user_id", 1), ("assigned_category", 1), ("transaction_date", -1)])
    await database.financial_transactions.create_index([("user_id", 1), ("review_status", 1)])
    await database.financial_transactions.create_index([("user_id", 1), ("is_income", 1)])
    await database.financial_transactions.create_index([("user_id", 1), ("is_recurring", 1)])
    await database.financial_transactions.create_index([("bank_transaction_id", 1)], unique=True)
    await database.financial_transactions.create_index([("user_id", 1), ("normalized_merchant", 1)])

    await database.merchant_dictionary.create_index([("merchant_name", 1)], unique=True)

    await database.merchant_aliases.create_index([("alias_type", 1), ("priority", -1)])

    await database.category_feedback.create_index([("user_id", 1), ("created_at", -1)])
    await database.category_feedback.create_index([("suggested_category", 1)])

    await database.transaction_tags.create_index([("user_id", 1), ("name", 1)], unique=True)

    await database.budget_usage.create_index(
        [("user_id", 1), ("budget_id", 1), ("month", 1), ("year", 1)], unique=True,
    )
    await database.budget_usage.create_index([("user_id", 1), ("state", 1)])

    await database.dashboard_metrics.create_index(
        [("user_id", 1), ("period", 1)], unique=True,
    )
    await database.dashboard_metrics.create_index([("user_id", 1), ("updated_at", -1)])

    await database.financial_metrics.create_index([("user_id", 1), ("calculated_at", -1)])
    await database.financial_metrics.create_index([("user_id", 1), ("period", 1)], unique=True)

    await database.cash_flow_summary.create_index(
        [("user_id", 1), ("year", 1), ("month", 1)], unique=True,
    )

    await database.monthly_summary.create_index(
        [("user_id", 1), ("period", 1)], unique=True,
    )

    await database.processing_batches.create_index([("user_id", 1), ("created_at", -1)])
    await database.processing_batches.create_index([("batch_id", 1)], unique=True)
    await database.processing_batches.create_index([("created_at", 1)], expireAfterSeconds=604800)

    await database.notifications.create_index([("user_id", 1), ("created_at", -1)])
    await database.notifications.create_index([("user_id", 1), ("read", 1)])

    await database.financial_health.create_index([("user_id", 1), ("period", 1)], unique=True)
    await database.financial_health.create_index([("user_id", 1), ("calculated_at", -1)])

    await database.financial_health_history.create_index([("user_id", 1), ("calculated_at", -1)])
    await database.financial_health_history.create_index([("user_id", 1), ("period", 1)], unique=True)

    await database.financial_health_factors.create_index([("user_id", 1), ("period", 1)])

    await database.financial_risk_profile.create_index([("user_id", 1), ("period", 1)], unique=True)
    await database.financial_risk_profile.create_index([("user_id", 1), ("calculated_at", -1)])

    await database.health_recommendations.create_index([("user_id", 1), ("priority", 1), ("created_at", -1)])
    await database.health_recommendations.create_index([("user_id", 1), ("dismissed", 1)])

    await database.budget_intelligence.create_index([("user_id", 1), ("period", 1)], unique=True)
    await database.budget_intelligence.create_index([("user_id", 1), ("calculated_at", -1)])

    await database.budget_recommendations.create_index([("user_id", 1), ("created_at", -1)])
    await database.budget_recommendations.create_index([("user_id", 1), ("dismissed", 1)])
    await database.budget_recommendations.create_index([("user_id", 1), ("priority", 1)])

    await database.budget_predictions.create_index([("user_id", 1), ("period", 1), ("category", 1)], unique=True)
    await database.budget_predictions.create_index([("user_id", 1), ("calculated_at", -1)])

    await database.budget_opportunities.create_index([("user_id", 1), ("dismissed", 1)])
    await database.budget_opportunities.create_index([("user_id", 1), ("created_at", -1)])

    await database.budget_risk.create_index([("user_id", 1), ("period", 1)], unique=True)
    await database.budget_risk.create_index([("user_id", 1), ("calculated_at", -1)])

    await database.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])

    await database.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
    await database.chat_messages.create_index([("user_id", 1), ("created_at", -1)])

    await database.conversation_memory.create_index(
        [("user_id", 1), ("session_id", 1)], unique=True,
    )

    await database.conversation_summary.create_index(
        [("user_id", 1), ("session_id", 1)], unique=True,
    )

    await database.ai_feedback.create_index([("user_id", 1), ("created_at", -1)])
    await database.ai_feedback.create_index([("session_id", 1), ("message_id", 1)])

    await database.financial_goals.create_index([("user_id", 1), ("created_at", -1)])
    await database.financial_goals.create_index([("user_id", 1), ("status", 1)])
    await database.financial_goals.create_index([("user_id", 1), ("goal_type", 1)])

    await database.goal_progress.create_index([("goal_id", 1), ("created_at", -1)])
    await database.goal_progress.create_index([("user_id", 1), ("created_at", -1)])
    await database.goal_progress.create_index([("goal_id", 1), ("period", 1)], unique=True)

    await database.goal_recommendations.create_index([("user_id", 1), ("created_at", -1)])
    await database.goal_recommendations.create_index([("user_id", 1), ("dismissed", 1)])
    await database.goal_recommendations.create_index([("user_id", 1), ("priority", 1)])

    await database.goal_predictions.create_index([("goal_id", 1)], unique=True)
    await database.goal_predictions.create_index([("user_id", 1), ("created_at", -1)])

    await database.goal_notifications.create_index([("user_id", 1), ("created_at", -1)])
    await database.goal_notifications.create_index([("user_id", 1), ("read", 1)])

    await database.receipts.create_index([("user_id", 1), ("created_at", -1)])
    await database.receipts.create_index([("user_id", 1), ("status", 1)])
    await database.receipts.create_index([("user_id", 1), ("filename", 1)])

    await database.receipt_processing_logs.create_index([("receipt_id", 1), ("created_at", -1)])
    await database.receipt_processing_logs.create_index([("user_id", 1), ("created_at", -1)])


async def close_mongo_connection() -> None:
    global client, database
    if client is not None:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("MongoDB is not connected")
    return database
