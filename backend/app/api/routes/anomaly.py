from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.anomaly import AnomalyAlert, SpendingAnomaly, WeeklySpendingReport
from app.services.anomaly_service import (
    detect_anomalies,
    generate_weekly_report,
    get_anomalies,
    get_anomaly_alerts,
    mark_anomaly_read,
)


router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.get("", response_model=list[SpendingAnomaly])
async def list_anomalies(
    unread_only: bool = False,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[SpendingAnomaly]:
    items = await get_anomalies(db, current_user["_id"], unread_only=unread_only)
    return [SpendingAnomaly(**item) for item in items]


@router.get("/alerts", response_model=list[AnomalyAlert])
async def get_alerts(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[AnomalyAlert]:
    return await get_anomaly_alerts(db, current_user["_id"])


@router.post("/detect")
async def run_detection(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    anomalies = await detect_anomalies(db, current_user["_id"])
    return {
        "status": "completed",
        "anomalies_detected": str(len(anomalies)),
        "message": f"Detected {len(anomalies)} spending anomalies"
    }


@router.patch("/{anomaly_id}/read", response_model=SpendingAnomaly)
async def read_anomaly(
    anomaly_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SpendingAnomaly:
    anomaly = await mark_anomaly_read(db, current_user["_id"], anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return SpendingAnomaly(**anomaly)


@router.get("/weekly-report", response_model=WeeklySpendingReport)
async def weekly_report(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> WeeklySpendingReport:
    return await generate_weekly_report(db, current_user["_id"])