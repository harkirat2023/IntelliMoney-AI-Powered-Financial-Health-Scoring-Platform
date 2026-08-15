from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.health.schemas import CalculateResponse, HealthCurrentResponse
from app.health.services.financial_health_service import FinancialHealthService
from app.schemas.analytics import FinancialHealthScore
from app.services.financial_service import calculate_financial_score


router = APIRouter(prefix="/financial-health", tags=["financial-health"])


@router.get("/score", response_model=FinancialHealthScore)
async def score(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialHealthScore:
    return FinancialHealthScore(**await calculate_financial_score(db, current_user))


@router.get("", response_model=HealthCurrentResponse)
async def current_health(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> HealthCurrentResponse:
    result = await FinancialHealthService(db).get_current(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No health data available. Run /financial-health/recalculate first.")
    return result


@router.post("/recalculate", response_model=CalculateResponse)
async def recalculate_health(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> CalculateResponse:
    return await FinancialHealthService(db).recalculate(str(current_user["_id"]))
