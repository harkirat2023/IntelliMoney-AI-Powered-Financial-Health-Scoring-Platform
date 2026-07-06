from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.alert import BudgetAlertPublic
from app.services.alert_service import list_alerts, mark_alert_read


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[BudgetAlertPublic])
async def get_alerts(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[BudgetAlertPublic]:
    return [BudgetAlertPublic(**item) for item in await list_alerts(db, current_user)]


@router.patch("/{alert_id}/read", response_model=BudgetAlertPublic)
async def read_alert(
    alert_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetAlertPublic:
    alert = await mark_alert_read(db, current_user, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return BudgetAlertPublic(**alert)
