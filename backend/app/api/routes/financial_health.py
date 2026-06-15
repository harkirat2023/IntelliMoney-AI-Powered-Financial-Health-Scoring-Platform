from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.analytics import FinancialHealthScore
from app.services.financial_service import calculate_financial_score


router = APIRouter(prefix="/financial-health", tags=["financial-health"])


@router.get("/score", response_model=FinancialHealthScore)
async def score(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialHealthScore:
    return FinancialHealthScore(**await calculate_financial_score(db, current_user))
