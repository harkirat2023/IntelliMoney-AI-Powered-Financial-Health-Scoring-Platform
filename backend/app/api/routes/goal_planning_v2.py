import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.goal_planning.schemas import (
    GoalAnalyzeRequest, GoalAnalyzeResponse, GoalCreateRequest,
    GoalCreateResponse, GoalPredictionResponse, GoalProgressResponseList,
    GoalRecommendationResponse, GoalResponse,
    GoalUpdateRequest,
)
from app.goal_planning.services.goal_planning_service import GoalPlanningService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/goals", tags=["goals"])


def _get_svc(db: AsyncIOMotorDatabase) -> GoalPlanningService:
    return GoalPlanningService(db)


@router.post("", response_model=GoalCreateResponse)
async def create_goal(
    body: GoalCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GoalCreateResponse:
    svc = _get_svc(db)
    result = await svc.create_goal(str(current_user["_id"]), body.model_dump())
    return GoalCreateResponse(**result)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str, body: GoalUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GoalResponse:
    svc = _get_svc(db)
    goal = await svc.update_goal(goal_id, str(current_user["_id"]),
                                  body.model_dump(exclude_none=True))
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse(**svc._goal_to_dict(goal))


@router.delete("/{goal_id}", response_model=dict)
async def delete_goal(
    goal_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_svc(db)
    deleted = await svc.delete_goal(goal_id, str(current_user["_id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}


@router.get("", response_model=list[GoalResponse])
async def get_goals(
    status: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[GoalResponse]:
    svc = _get_svc(db)
    goals = await svc.get_goals(str(current_user["_id"]), status)
    return [GoalResponse(**g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GoalResponse:
    svc = _get_svc(db)
    goal = await svc.get_goal(goal_id, str(current_user["_id"]))
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse(**svc._goal_to_dict(goal))


@router.post("/recalculate")
async def goals_recalculate(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_svc(db)
    return await svc.recalculate(str(current_user["_id"]))


@router.post("/analyze", response_model=GoalAnalyzeResponse)
async def analyze_goal(
    body: GoalAnalyzeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GoalAnalyzeResponse:
    svc = _get_svc(db)
    result = await svc.analyze(str(current_user["_id"]), body.model_dump())
    return GoalAnalyzeResponse(**result)


@router.get("/recommendations", response_model=list[GoalRecommendationResponse])
async def get_goal_recommendations(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[GoalRecommendationResponse]:
    svc = _get_svc(db)
    recs = await svc.get_recommendations(str(current_user["_id"]))
    return [GoalRecommendationResponse(**svc._rec_to_dict(r)) for r in recs]


@router.get("/progress", response_model=list[GoalProgressResponseList])
async def get_goal_progress(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[GoalProgressResponseList]:
    svc = _get_svc(db)
    result = await svc.get_progress(str(current_user["_id"]))
    return [GoalProgressResponseList(**r) for r in result]
