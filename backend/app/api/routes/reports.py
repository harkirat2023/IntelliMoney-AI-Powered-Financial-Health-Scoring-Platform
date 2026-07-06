from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.report import FinancialReport, ReportSummary
from app.services.report_service import (
    generate_monthly_report,
    generate_weekly_report,
    get_report,
    get_report_summary,
    get_reports,
    mark_report_read,
)


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[FinancialReport])
async def list_reports(
    report_type: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[FinancialReport]:
    items = await get_reports(db, current_user["_id"], report_type)
    return [FinancialReport(**item) for item in items]


@router.get("/summary", response_model=ReportSummary)
async def get_summary(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReportSummary:
    return await get_report_summary(db, current_user["_id"])


@router.get("/{report_id}", response_model=FinancialReport)
async def read_report(
    report_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialReport:
    report = await get_report(db, current_user["_id"], report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return FinancialReport(**report)


@router.post("/generate/weekly", response_model=FinancialReport)
async def create_weekly_report(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialReport:
    report = await generate_weekly_report(db, current_user["_id"])
    return FinancialReport(**report)


@router.post("/generate/monthly", response_model=FinancialReport)
async def create_monthly_report(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialReport:
    report = await generate_monthly_report(db, current_user["_id"])
    return FinancialReport(**report)


@router.patch("/{report_id}/read", response_model=FinancialReport)
async def mark_report_read_endpoint(
    report_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FinancialReport:
    report = await mark_report_read(db, current_user["_id"], report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return FinancialReport(**report)