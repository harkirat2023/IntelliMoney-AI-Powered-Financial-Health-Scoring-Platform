from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.ai import (
    FeedbackResponse,
    FeedbackSubmissionRequest,
    IntelligenceStatusResponse,
    ProcessPendingRequest,
    ProcessResultResponse,
    ReviewQueueResponse,
    ReviewSubmissionRequest,
)
from app.schemas.financial_transactions import FinancialTransactionResponse
from app.services.intelligence_service import get_intelligence_service

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/process", response_model=ProcessResultResponse)
async def process_pending(
    req: ProcessPendingRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    return await service.process_pending(
        str(user["_id"]), req.bank_account_id, req.limit,
    )


@router.post("/process-all", response_model=ProcessResultResponse)
async def process_all(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    return await service.process_pending(str(user["_id"]), limit=100)


@router.get("/status", response_model=IntelligenceStatusResponse)
async def intelligence_status(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    return await service.get_status(str(user["_id"]))


@router.get("/history", response_model=list[FinancialTransactionResponse])
async def intelligence_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    txs = await service.list_transactions(str(user["_id"]), limit, offset)
    return [FinancialTransactionResponse.from_domain(tx) for tx in txs]


@router.get("/review", response_model=ReviewQueueResponse)
async def review_queue(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    return await service.get_review_queue(str(user["_id"]), limit, offset)


@router.patch("/review/{tx_id}", response_model=FinancialTransactionResponse)
async def submit_review(
    tx_id: str,
    review: ReviewSubmissionRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    updated = await service.submit_review(str(user["_id"]), tx_id, review)
    return FinancialTransactionResponse.from_domain(updated)


@router.post("/feedback/{tx_id}", response_model=FeedbackResponse)
async def submit_feedback(
    tx_id: str,
    feedback: FeedbackSubmissionRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    feedback_id = await service.record_feedback(
        user_id=str(user["_id"]), tx_id=tx_id,
        user_category=feedback.user_category,
        feedback_type=feedback.feedback_type,
    )
    return FeedbackResponse(id=feedback_id)
