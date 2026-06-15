from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.budget import BudgetCreate, BudgetPublic, BudgetStatus, BudgetUpdate
from app.services.budget_service import get_budget_status
from app.services.serializers import serialize_document, to_object_id


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetPublic, status_code=201)
async def create_budget(
    payload: BudgetCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetPublic:
    document = {**payload.model_dump(), "user_id": current_user["_id"]}
    try:
        result = await db.budgets.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Budget already exists for this category and month") from exc
    document["_id"] = result.inserted_id
    return BudgetPublic(**serialize_document(document))


@router.get("", response_model=list[BudgetPublic])
async def list_budgets(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[BudgetPublic]:
    cursor = db.budgets.find({"user_id": current_user["_id"]}).sort([("year", -1), ("month", -1)])
    return [BudgetPublic(**serialize_document(item)) async for item in cursor]


@router.get("/status", response_model=list[BudgetStatus])
async def budget_status(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[BudgetStatus]:
    return [BudgetStatus(**item) for item in await get_budget_status(db, str(current_user["_id"]))]


@router.put("/{budget_id}", response_model=BudgetPublic)
async def update_budget(
    budget_id: str,
    payload: BudgetUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetPublic:
    try:
        object_id = to_object_id(budget_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Budget not found") from exc
    updates = payload.model_dump(exclude_unset=True)
    if updates:
        await db.budgets.update_one({"_id": object_id, "user_id": current_user["_id"]}, {"$set": updates})
    budget = await db.budgets.find_one({"_id": object_id, "user_id": current_user["_id"]})
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return BudgetPublic(**serialize_document(budget))


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> None:
    try:
        object_id = to_object_id(budget_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Budget not found") from exc
    result = await db.budgets.delete_one({"_id": object_id, "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
