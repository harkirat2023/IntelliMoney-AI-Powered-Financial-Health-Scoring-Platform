from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.health.schemas import (
    CalculateResponse, HealthBreakdownResponse, HealthCurrentResponse,
    HealthHistoryResponse, HealthRecommendationItem, RiskAssessmentResponse, TrendAnalysis,
)
from app.health.services.financial_health_service import FinancialHealthService

router = APIRouter(prefix="/health", tags=["health"])


def _get_svc(db: AsyncIOMotorDatabase) -> FinancialHealthService:
    return FinancialHealthService(db)


@router.post("/calculate", response_model=CalculateResponse)
async def health_calculate(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> CalculateResponse:
    svc = _get_svc(db)
    return await svc.calculate(str(current_user["_id"]))


@router.post("/recalculate", response_model=CalculateResponse)
async def health_recalculate(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> CalculateResponse:
    svc = _get_svc(db)
    return await svc.recalculate(str(current_user["_id"]))


@router.get("/current", response_model=HealthCurrentResponse)
async def health_current(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> HealthCurrentResponse:
    svc = _get_svc(db)
    result = await svc.get_current(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No health data available. Run /health/calculate first.")
    return result


@router.get("/history", response_model=HealthHistoryResponse)
async def health_history(
    limit: int = Query(36, ge=1, le=120),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> HealthHistoryResponse:
    svc = _get_svc(db)
    return await svc.get_history(str(current_user["_id"]), limit)


@router.get("/trends", response_model=TrendAnalysis)
async def health_trends(
    months: int = Query(12, ge=2, le=60),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TrendAnalysis:
    svc = _get_svc(db)
    return await svc.get_trends(str(current_user["_id"]), months)


@router.get("/breakdown", response_model=HealthBreakdownResponse)
async def health_breakdown(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> HealthBreakdownResponse:
    svc = _get_svc(db)
    result = await svc.get_breakdown(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No health data available.")
    return result


@router.get("/recommendations", response_model=list[HealthRecommendationItem])
async def health_recommendations(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[HealthRecommendationItem]:
    svc = _get_svc(db)
    return await svc.get_recommendations(str(current_user["_id"]))


@router.get("/risk", response_model=RiskAssessmentResponse)
async def health_risk(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RiskAssessmentResponse:
    svc = _get_svc(db)
    result = await svc.get_risk(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No risk data available.")
    return result
