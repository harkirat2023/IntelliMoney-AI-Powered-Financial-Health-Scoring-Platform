from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.recurring import RecurringExpenseCreate, RecurringExpensePublic, RecurringExpenseSuggestion, RecurringExpenseUpdate
from app.services.recurring_service import (
    create_recurring_expense,
    delete_recurring_expense,
    detect_recurring_patterns,
    generate_upcoming_expenses,
    get_recurring_expense,
    get_recurring_expenses,
    update_recurring_expense,
)


router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("", response_model=list[RecurringExpensePublic])
async def list_recurring_expenses(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[RecurringExpensePublic]:
    items = await get_recurring_expenses(db, current_user["_id"])
    return [RecurringExpensePublic(**item) for item in items]


@router.post("", response_model=RecurringExpensePublic)
async def add_recurring_expense(
    payload: RecurringExpenseCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RecurringExpensePublic:
    item = await create_recurring_expense(db, current_user["_id"], payload.model_dump())
    return RecurringExpensePublic(**item)


@router.get("/{recurring_id}", response_model=RecurringExpensePublic)
async def read_recurring_expense(
    recurring_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RecurringExpensePublic:
    item = await get_recurring_expense(db, current_user["_id"], recurring_id)
    if not item:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return RecurringExpensePublic(**item)


@router.put("/{recurring_id}", response_model=RecurringExpensePublic)
async def edit_recurring_expense(
    recurring_id: str,
    payload: RecurringExpenseUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RecurringExpensePublic:
    item = await update_recurring_expense(db, current_user["_id"], recurring_id, payload.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return RecurringExpensePublic(**item)


@router.delete("/{recurring_id}")
async def remove_recurring_expense(
    recurring_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    deleted = await delete_recurring_expense(db, current_user["_id"], recurring_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return {"status": "deleted"}


@router.get("/suggestions/detect", response_model=list[RecurringExpenseSuggestion])
async def suggest_recurring_expenses(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[RecurringExpenseSuggestion]:
    suggestions = await detect_recurring_patterns(db, current_user["_id"])
    return [RecurringExpenseSuggestion(**item) for item in suggestions]


@router.get("/upcoming", response_model=list[dict[str, Any]])
async def upcoming_recurring_expenses(
    days_ahead: int = 30,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[dict[str, Any]]:
    return await generate_upcoming_expenses(db, current_user["_id"], days_ahead)