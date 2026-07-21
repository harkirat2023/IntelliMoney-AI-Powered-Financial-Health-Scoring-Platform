from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.budget_intelligence.schemas import (
    BudgetIntelligenceResponse, BudgetOptimizationResponse, BudgetRiskResponse,
    BudgetTrendsResponse, GenerateResponse, RecommendationResponse, SavingsOpportunityResponse,
)
from app.budget_intelligence.services.budget_intelligence_service import (
    BudgetIntelligenceService,
)
from app.db.mongodb import get_database

router = APIRouter(prefix="/budget-intelligence", tags=["budget-intelligence"])


def _get_svc(db: AsyncIOMotorDatabase) -> BudgetIntelligenceService:
    return BudgetIntelligenceService(db)


@router.post("/generate", response_model=GenerateResponse)
async def intelligence_generate(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GenerateResponse:
    svc = _get_svc(db)
    result = await svc.generate(str(current_user["_id"]))
    return GenerateResponse(**result)


@router.get("/current", response_model=BudgetIntelligenceResponse)
async def intelligence_current(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetIntelligenceResponse:
    svc = _get_svc(db)
    result = await svc.get_current(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No budget intelligence data. Run /generate first.")
    from app.budget_intelligence.schemas import CategoryBudgetInfo
    return BudgetIntelligenceResponse(
        period=result.period,
        budget_score=result.budget_score,
        total_budget=result.total_budget,
        total_spent=result.total_spent,
        total_suggested=result.total_suggested,
        potential_savings=result.potential_savings,
        category_count=result.category_count,
        on_track_count=result.on_track_count,
        warning_count=result.warning_count,
        over_count=result.over_count,
        categories=[CategoryBudgetInfo(**c) for c in result.categories],
        calculated_at=result.calculated_at,
    )


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def intelligence_recommendations(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[RecommendationResponse]:
    svc = _get_svc(db)
    recs = await svc.get_recommendations(str(current_user["_id"]))
    return [
        RecommendationResponse(
            id=r.id, category=r.category, recommendation_type=r.recommendation_type,
            title=r.title, message=r.message, current_value=r.current_value,
            target_value=r.target_value, potential_savings=r.potential_savings,
            confidence_score=r.confidence_score, priority=r.priority,
            reasoning=r.reasoning, affected_categories=r.affected_categories,
            estimated_impact=r.estimated_impact, actionable_steps=r.actionable_steps,
            dismissed=r.dismissed, created_at=r.created_at,
        ) for r in recs
    ]


@router.get("/optimization", response_model=BudgetOptimizationResponse)
async def intelligence_optimization(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetOptimizationResponse:
    svc = _get_svc(db)
    result = await svc.get_optimization(str(current_user["_id"]))
    return BudgetOptimizationResponse(**result)


@router.get("/trends", response_model=BudgetTrendsResponse)
async def intelligence_trends(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetTrendsResponse:
    svc = _get_svc(db)
    result = await svc.get_trends(str(current_user["_id"]))
    from app.budget_intelligence.schemas import CategoryPrediction
    return BudgetTrendsResponse(
        period=result["period"],
        predictions=[CategoryPrediction(**p) for p in result.get("predictions", [])],
    )


@router.get("/risk", response_model=BudgetRiskResponse)
async def intelligence_risk(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BudgetRiskResponse:
    svc = _get_svc(db)
    result = await svc.get_risk(str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="No risk data available. Run /generate first.")
    from app.budget_intelligence.schemas import RiskCategoryInfo
    return BudgetRiskResponse(
        period=result.period,
        overall_risk_level=result.overall_risk_level,
        overall_risk_score=result.overall_risk_score,
        high_risk_count=result.high_risk_count,
        medium_risk_count=result.medium_risk_count,
        low_risk_count=result.low_risk_count,
        volatility_score=result.volatility_score,
        trend_direction=result.trend_direction,
        categories=[RiskCategoryInfo(**c) for c in result.overspending_categories],
    )


@router.get("/opportunities", response_model=list[SavingsOpportunityResponse])
async def intelligence_opportunities(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[SavingsOpportunityResponse]:
    svc = _get_svc(db)
    opps = await svc.get_opportunities(str(current_user["_id"]))
    return [
        SavingsOpportunityResponse(
            id=o.id, opportunity_type=o.opportunity_type, category=o.category,
            title=o.title, message=o.message, potential_savings=o.potential_savings,
            confidence_score=o.confidence_score, monthly_impact=o.monthly_impact,
            annual_impact=o.annual_impact, reasoning=o.reasoning,
            actionable_steps=o.actionable_steps, dismissed=o.dismissed,
            created_at=o.created_at,
        ) for o in opps
    ]
