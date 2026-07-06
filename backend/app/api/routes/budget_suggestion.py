from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.budget_suggestion import BudgetOptimizationReport, BudgetSuggestion
from app.services.budget_suggestion_service import (
    apply_budget_suggestion,
    dismiss_budget_suggestion,
    generate_budget_suggestions,
    generate_optimization_report,
    get_budget_suggestions,
)


router = APIRouter(prefix="/budget-suggestions", tags=["budget-suggestions"])


@router.get("", response_model=list[BudgetSuggestion])
async def list_suggestions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[BudgetSuggestion]:
    items = await get_budget_suggestions(db, current_user["_id"])
    return [BudgetSuggestion(**item) for item in items]


@router.post("/generate")
async def generate_suggestions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    suggestions = await generate_budget_suggestions(db, current_user["_id"])
    return {
        "status": "completed",
        "suggestions_generated": str(len(suggestions)),
        "message": f"Generated {len(suggestions)} budget suggestions"
    }


@router.post("/{suggestion_id}/apply", response_model=BudgetSuggestion)
async def apply_suggestion(
    suggestion_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetSuggestion:
    suggestion = await apply_budget_suggestion(db, current_user["_id"], suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found or already applied")
    return BudgetSuggestion(**suggestion)


@router.delete("/{suggestion_id}")
async def dismiss_suggestion(
    suggestion_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    deleted = await dismiss_budget_suggestion(db, current_user["_id"], suggestion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return {"status": "dismissed"}


@router.get("/optimization-report", response_model=BudgetOptimizationReport)
async def optimization_report(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetOptimizationReport:
    return await generate_optimization_report(db, current_user["_id"])