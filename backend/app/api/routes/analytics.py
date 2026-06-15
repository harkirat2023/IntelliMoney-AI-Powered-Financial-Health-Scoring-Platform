from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.analytics import ChartPoint, RecentExpense, SummaryResponse
from app.services import analytics_service


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SummaryResponse:
    return SummaryResponse(**await analytics_service.get_summary(db, current_user))


@router.get("/monthly-spending", response_model=list[ChartPoint])
async def monthly_spending(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ChartPoint]:
    return [ChartPoint(**item) for item in await analytics_service.monthly_spending(db, str(current_user["_id"]))]


@router.get("/category-breakdown", response_model=list[ChartPoint])
async def categories(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ChartPoint]:
    return [ChartPoint(**item) for item in await analytics_service.category_breakdown(db, str(current_user["_id"]))]


@router.get("/payment-methods", response_model=list[ChartPoint])
async def payment_methods(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ChartPoint]:
    return [ChartPoint(**item) for item in await analytics_service.payment_methods(db, str(current_user["_id"]))]


@router.get("/recent-expenses", response_model=list[RecentExpense])
async def recent_expenses(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[RecentExpense]:
    return [RecentExpense(**item) for item in await analytics_service.recent_expenses(db, str(current_user["_id"]))]
