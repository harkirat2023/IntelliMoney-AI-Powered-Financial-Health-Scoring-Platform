from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.financial_transactions import (
    FinancialTransactionResponse,
    FinancialTransactionUpdateRequest,
)
from app.services.intelligence_service import get_intelligence_service

router = APIRouter(prefix="/financial-transactions", tags=["financial_transactions"])


@router.get("", response_model=list[FinancialTransactionResponse])
async def list_financial_transactions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    txs = await service.list_transactions(str(user["_id"]), limit, offset, category)
    return [FinancialTransactionResponse.from_domain(tx) for tx in txs]


@router.get("/{tx_id}", response_model=FinancialTransactionResponse)
async def get_financial_transaction(
    tx_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    tx = await service.get_transaction(str(user["_id"]), tx_id)
    return FinancialTransactionResponse.from_domain(tx)


@router.put("/{tx_id}", response_model=FinancialTransactionResponse)
async def update_financial_transaction(
    tx_id: str,
    payload: FinancialTransactionUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = get_intelligence_service(db)
    tx = await service.get_transaction(str(user["_id"]), tx_id)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return FinancialTransactionResponse.from_domain(tx)

    update_data = {}
    if "assigned_category" in updates and updates["assigned_category"]:
        update_data["assigned_category"] = updates["assigned_category"]
    if "normalized_merchant" in updates and updates["normalized_merchant"]:
        update_data["normalized_merchant"] = updates["normalized_merchant"]
    if "is_income" in updates:
        update_data["is_income"] = updates["is_income"]
    if "is_recurring" in updates:
        update_data["is_recurring"] = updates["is_recurring"]
    if "transaction_tags" in updates:
        update_data["transaction_tags"] = updates["transaction_tags"]
    if "review_note" in updates:
        update_data["review_note"] = updates["review_note"]

    updated_tx = await service.update_transaction(
        str(user["_id"]), tx_id, update_data,
    )

    if payload.assigned_category and payload.assigned_category != tx.assigned_category:
        await service.record_feedback(
            user_id=str(user["_id"]), tx_id=tx_id,
            user_category=payload.assigned_category,
        )

    return FinancialTransactionResponse.from_domain(updated_tx)
