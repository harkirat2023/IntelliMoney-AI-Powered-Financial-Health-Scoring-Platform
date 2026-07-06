from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.processing.services.dashboard_read_service import DashboardReadService

def _get_dash_service(db):
    return DashboardReadService(db)

from app.processing.schemas.dashboard import (
    BudgetOverview,
    CashFlowPoint,
    DashboardSummaryResponse,
    MonthlyTrendPoint,
    MonthlyTrendResponse,
    SpendingCategory,
    SpendingResponse,
    TopMerchant,
)
from app.utils.date_utils import utc_now


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> DashboardSummaryResponse:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    dash_svc = _get_dash_service(db)
    metrics = await dash_svc.get_summary(str(current_user["_id"]), period)
    if not metrics:
        raise HTTPException(status_code=404, detail="No data for this period")
    return DashboardSummaryResponse(
        period=metrics.period,
        total_spending=metrics.total_spending,
        total_income=metrics.total_income,
        net_savings=metrics.net_savings,
        savings_rate=metrics.savings_rate,
        expense_count=metrics.expense_count,
        spending_by_category=[SpendingCategory(**c) for c in metrics.spending_by_category],
        monthly_trend=[MonthlyTrendPoint(**m) for m in metrics.monthly_trend],
        top_merchants=[TopMerchant(**m) for m in metrics.top_merchants],
        budget_overview=[BudgetOverview(**b) for b in metrics.budget_overview],
    )


@router.get("/spending", response_model=SpendingResponse)
async def dashboard_spending(
    category: str = Query(...),
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SpendingResponse:
    now = utc_now()
    period = period or f"{now.year}-{now.month:02d}"
    dash_svc = _get_dash_service(db)
    metrics = await dash_svc.get_summary(str(current_user["_id"]), period)
    if not metrics:
        raise HTTPException(status_code=404, detail="No data for this period")
    for cat in metrics.spending_by_category:
        if cat["category"] == category:
            return SpendingResponse(
                category=cat["category"],
                amount=cat["amount"],
                percentage=cat["percentage"],
                transaction_count=0,
            )
    raise HTTPException(status_code=404, detail=f"No spending data for category '{category}'")


@router.get("/cashflow", response_model=list[CashFlowPoint])
async def dashboard_cashflow(
    months: int = Query(6, ge=1, le=24),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[CashFlowPoint]:
    dash_svc = _get_dash_service(db)
    summaries = await dash_svc.get_cashflow(str(current_user["_id"]), months)
    return [
        CashFlowPoint(
            year=s.year,
            month=s.month,
            total_income=s.total_income,
            total_expenses=s.total_expenses,
            net_cash_flow=s.net_cash_flow,
            income_by_category=s.income_by_category,
            expense_by_category=s.expense_by_category,
        )
        for s in summaries
    ]


@router.get("/monthly", response_model=list[MonthlyTrendResponse])
async def dashboard_monthly(
    months: int = Query(6, ge=1, le=24),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[MonthlyTrendResponse]:
    dash_svc = _get_dash_service(db)
    all_metrics = await dash_svc.get_monthly_trends(str(current_user["_id"]), months)
    result: list[MonthlyTrendResponse] = []
    for m in all_metrics:
        for trend in m.monthly_trend:
            result.append(MonthlyTrendResponse(
                month=trend["month"],
                spending=trend.get("spending", 0),
                income=trend.get("income", 0),
                savings=round(trend.get("income", 0) - trend.get("spending", 0), 2),
            ))
    return result[:months]
