from fastapi import APIRouter

from app.api.routes import (
    alerts, analytics, anomaly, auth, bank, budgets, budget_intelligence_v2,
    budget_suggestion, consent, copilot_v2, dashboard_v2,
    expenses, financial_health, goal_planning_v2, health_v2, import_preference,
    ml, receipt_ocr_v2, recommendations, recurring,
    reports, subscriptions, sync,
)
from app.api.v1 import websocket

router = APIRouter()

router.include_router(auth.router, tags=["auth"])
router.include_router(expenses.router, tags=["expenses"])
router.include_router(budgets.router, tags=["budgets"])
router.include_router(analytics.router, tags=["analytics"])
router.include_router(financial_health.router, tags=["financial_health"])
router.include_router(recommendations.router, tags=["recommendations"])
router.include_router(ml.router, tags=["ml"])
router.include_router(alerts.router, tags=["alerts"])
router.include_router(anomaly.router, tags=["anomaly"])
router.include_router(budget_suggestion.router, tags=["budget_suggestions"])
router.include_router(reports.router, tags=["reports"])
router.include_router(subscriptions.router, tags=["subscriptions"])
router.include_router(bank.router, tags=["bank"])
router.include_router(consent.router, tags=["consent"])
router.include_router(import_preference.router, tags=["import_preference"])
router.include_router(recurring.router, tags=["recurring"])
router.include_router(sync.router, tags=["sync"])
router.include_router(dashboard_v2.router, tags=["dashboard"])
router.include_router(budget_intelligence_v2.router, tags=["budget-intelligence"])
router.include_router(health_v2.router, tags=["health"])
router.include_router(copilot_v2.router, tags=["copilot"])
router.include_router(goal_planning_v2.router, tags=["goals"])
router.include_router(receipt_ocr_v2.router, tags=["receipts"])
router.include_router(websocket.router, tags=["websocket"])
