from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.dashboard.schemas import (
    AnalyticsResponse, DashboardOverviewResponse, NotificationItem,
    WidgetsResponse,
)
from app.dashboard.services import DashboardService, NotificationService, WidgetService
from app.db.mongodb import get_database
from app.utils.date_utils import utc_now

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_dash_svc(db: AsyncIOMotorDatabase) -> DashboardService:
    return DashboardService(db)


def _get_notif_svc(db: AsyncIOMotorDatabase) -> NotificationService:
    return NotificationService(db)


def _get_widget_svc(db: AsyncIOMotorDatabase) -> WidgetService:
    return WidgetService(db)


@router.get("/overview", response_model=DashboardOverviewResponse)
async def dashboard_overview(
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> DashboardOverviewResponse:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    svc = _get_dash_svc(db)
    return await svc.get_overview(str(current_user["_id"]), period)


@router.get("/analytics", response_model=AnalyticsResponse)
async def dashboard_analytics(
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> AnalyticsResponse:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    svc = _get_dash_svc(db)
    return await svc.get_analytics(str(current_user["_id"]), period)


@router.get("/budgets")
async def dashboard_budgets(
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    dash_svc = _get_dash_svc(db)
    from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository
    dash_repo = MongoDashboardMetricsRepository(db)
    dash = await dash_repo.get_by_user_and_period(str(current_user["_id"]), period)
    if not dash:
        return {"budgets": [], "on_track": 0, "warning": 0, "over": 0}
    overview = dash.budget_overview
    return {
        "budgets": overview,
        "on_track": sum(1 for b in overview if b.get("state") == "safe"),
        "warning": sum(1 for b in overview if b.get("state") == "warning"),
        "over": sum(1 for b in overview if b.get("state") == "over"),
    }


@router.get("/insights")
async def dashboard_insights(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    dash_svc = _get_dash_svc(db)
    insights = await dash_svc._get_ai_insights(str(current_user["_id"]))
    alerts = await dash_svc._get_budget_alerts(str(current_user["_id"]))
    return {"insights": [i.model_dump() for i in insights], "alerts": [a.model_dump() for a in alerts]}


@router.get("/notifications", response_model=list[NotificationItem])
async def dashboard_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[NotificationItem]:
    svc = _get_notif_svc(db)
    return await svc.get_notifications(str(current_user["_id"]), limit, offset, unread_only)


@router.get("/notifications/unread-count")
async def notifications_unread_count(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_notif_svc(db)
    count = await svc.get_unread_count(str(current_user["_id"]))
    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_notif_svc(db)
    ok = await svc.mark_read(notification_id, str(current_user["_id"]))
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "ok"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_notif_svc(db)
    count = await svc.mark_all_read(str(current_user["_id"]))
    return {"marked_read": count}


@router.get("/activity")
async def dashboard_activity(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[dict]:
    dash_svc = _get_dash_svc(db)
    activity = await dash_svc._get_activity_feed(str(current_user["_id"]))
    return [a.model_dump() for a in activity]


@router.get("/widgets", response_model=WidgetsResponse)
async def dashboard_widgets(
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    widget: list[str] = Query(default=[], description="Specific widget IDs to fetch"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> WidgetsResponse:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    svc = _get_widget_svc(db)
    if widget:
        result = {}
        for wid in widget:
            data = await svc.get_widget(str(current_user["_id"]), wid, period)
            if data is not None:
                result[wid] = data
        return WidgetsResponse(widgets=result)
    all_widgets = await svc.get_all_widgets(str(current_user["_id"]), period)
    return WidgetsResponse(widgets=all_widgets)
