from datetime import date
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.expense import ExpenseCreate, ExpensePublic, ExpenseUpdate
from app.services.ml_service import categorizer
from app.services.serializers import date_to_datetime, serialize_document, to_object_id, utc_now


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpensePublic, status_code=201)
async def create_expense(
    payload: ExpenseCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ExpensePublic:
    category = payload.category or categorizer.predict(payload.description)[0]
    document = {
        "user_id": current_user["_id"],
        "amount": payload.amount,
        "description": payload.description,
        "category": category,
        "payment_method": payload.payment_method,
        "date": date_to_datetime(payload.date),
        "created_at": utc_now(),
    }
    result = await db.expenses.insert_one(document)
    document["_id"] = result.inserted_id
    return ExpensePublic(**serialize_document(document))


@router.get("", response_model=list[ExpensePublic])
async def list_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    category: str | None = None,
    payment_method: str | None = None,
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ExpensePublic]:
    query: dict[str, Any] = {"user_id": current_user["_id"]}
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = date_to_datetime(start_date)
        if end_date:
            query["date"]["$lte"] = date_to_datetime(end_date)
    if category:
        query["category"] = category
    if payment_method:
        query["payment_method"] = payment_method
    if min_amount is not None or max_amount is not None:
        query["amount"] = {}
        if min_amount is not None:
            query["amount"]["$gte"] = min_amount
        if max_amount is not None:
            query["amount"]["$lte"] = max_amount

    cursor = db.expenses.find(query).sort("date", -1)
    return [ExpensePublic(**serialize_document(item)) async for item in cursor]


@router.get("/{expense_id}", response_model=ExpensePublic)
async def get_expense(
    expense_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ExpensePublic:
    try:
        object_id = to_object_id(expense_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Expense not found") from exc
    expense = await db.expenses.find_one({"_id": object_id, "user_id": current_user["_id"]})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpensePublic(**serialize_document(expense))


@router.put("/{expense_id}", response_model=ExpensePublic)
async def update_expense(
    expense_id: str,
    payload: ExpenseUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ExpensePublic:
    try:
        object_id = to_object_id(expense_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Expense not found") from exc
    updates = payload.model_dump(exclude_unset=True)
    if "date" in updates:
        updates["date"] = date_to_datetime(updates["date"])
    if updates:
        await db.expenses.update_one(
            {"_id": object_id, "user_id": current_user["_id"]},
            {"$set": updates},
        )
    expense = await db.expenses.find_one({"_id": object_id, "user_id": current_user["_id"]})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpensePublic(**serialize_document(expense))


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    try:
        object_id = to_object_id(expense_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Expense not found") from exc
    result = await db.expenses.delete_one({"_id": object_id, "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}
