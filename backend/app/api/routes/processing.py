from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.processing.schemas.processing import (
    ProcessRequest,
    ProcessingHistoryResponse,
    ProcessingStatusResponse,
    ProcessingSummaryResponse,
    ReprocessRequest,
)
from app.processing.services.financial_processing_service import FinancialProcessingService


router = APIRouter(prefix="/processing", tags=["processing"])


def _get_service(db: AsyncIOMotorDatabase) -> FinancialProcessingService:
    return FinancialProcessingService(db)


@router.post("/process", response_model=ProcessingStatusResponse, status_code=202)
async def process_transactions(
    payload: ProcessRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProcessingStatusResponse:
    service = _get_service(db)
    result = await service.process(str(current_user["_id"]), payload.transaction_ids, payload.force)
    return ProcessingStatusResponse(**result)


@router.post("/process-all", response_model=ProcessingStatusResponse, status_code=202)
async def process_all(
    force: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProcessingStatusResponse:
    service = _get_service(db)
    result = await service.process_all(str(current_user["_id"]), force, limit)
    return ProcessingStatusResponse(**result)


@router.post("/reprocess", response_model=ProcessingStatusResponse, status_code=202)
async def reprocess_transactions(
    payload: ReprocessRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProcessingStatusResponse:
    service = _get_service(db)
    result = await service.reprocess(str(current_user["_id"]), payload.transaction_ids, payload.reason)
    return ProcessingStatusResponse(**result)


@router.get("/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    batch_id: str = Query(...),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProcessingStatusResponse:
    service = _get_service(db)
    result = await service.get_status(batch_id, str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    return ProcessingStatusResponse(**result)


@router.get("/history", response_model=list[ProcessingHistoryResponse])
async def get_processing_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ProcessingHistoryResponse]:
    service = _get_service(db)
    result = await service.get_history(str(current_user["_id"]), limit, offset)
    return [ProcessingHistoryResponse(**item) for item in result]
