import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.budget_intelligence.models.budget_intelligence import BudgetIntelligence
from app.budget_intelligence.models.budget_opportunity import BudgetOpportunity
from app.budget_intelligence.models.budget_prediction import BudgetPrediction
from app.budget_intelligence.models.budget_recommendation import BudgetRecommendation
from app.budget_intelligence.models.budget_risk import BudgetRisk
from app.budget_intelligence.repositories.budget_intelligence_repository import (
    MongoBudgetIntelligenceRepository,
)
from app.budget_intelligence.repositories.budget_opportunity_repository import (
    MongoBudgetOpportunityRepository,
)
from app.budget_intelligence.repositories.budget_prediction_repository import (
    MongoBudgetPredictionRepository,
)
from app.budget_intelligence.repositories.budget_recommendation_repository import (
    MongoBudgetRecommendationRepository,
)
from app.budget_intelligence.repositories.budget_risk_repository import (
    MongoBudgetRiskRepository,
)
from app.budget_intelligence.services.budget_forecast_service import BudgetForecastService
from app.budget_intelligence.services.budget_optimization_service import (
    BudgetOptimizationService,
)
from app.budget_intelligence.services.budget_recommendation_service import (
    BudgetRecommendationService,
)
from app.budget_intelligence.services.budget_risk_service import BudgetRiskService
from app.budget_intelligence.services.category_trend_service import CategoryTrendService
from app.budget_intelligence.services.savings_opportunity_service import (
    SavingsOpportunityService,
)
from app.budget_intelligence.services.smart_budget_service import SmartBudgetService
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.infrastructure.messaging.events import Event

logger = logging.getLogger("intellimoney")


class BudgetIntelligenceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._intel_repo = MongoBudgetIntelligenceRepository(db)
        self._rec_repo = MongoBudgetRecommendationRepository(db)
        self._pred_repo = MongoBudgetPredictionRepository(db)
        self._opp_repo = MongoBudgetOpportunityRepository(db)
        self._risk_repo = MongoBudgetRiskRepository(db)

        self._smart_budget = SmartBudgetService(db)
        self._recommendation = BudgetRecommendationService(db)
        self._optimization = BudgetOptimizationService(db)
        self._forecast = BudgetForecastService(db)
        self._risk = BudgetRiskService(db)
        self._savings = SavingsOpportunityService(db)
        self._trends = CategoryTrendService(db)

    async def generate(self, user_id: str) -> dict:
        now = datetime.utcnow()
        period = f"{now.year}-{now.month:02d}"

        existing = await self._intel_repo.get_by_user_and_period(user_id, period)
        if existing:
            return {"period": existing.period, "budget_score": existing.budget_score, "message": "Already generated for this period. Use /recalculate to regenerate."}

        intelligence = await self._smart_budget.generate_budget(user_id)
        await self._intel_repo.upsert(intelligence)

        recs = await self._recommendation.generate(user_id)
        rec_models = [BudgetRecommendation(**r) for r in recs]
        if rec_models:
            await self._rec_repo.bulk_create(rec_models)
        await self._rec_repo.delete_old(user_id, 50)

        forecast = await self._forecast.forecast(user_id)
        for p in forecast.get("predictions", []):
            pred = BudgetPrediction(
                user_id=user_id, period=period, category=p["category"],
                predicted_spending=p["predicted_spending"],
                predicted_utilization=p["predicted_utilization"],
                confidence_upper=p["confidence_upper"], confidence_lower=p["confidence_lower"],
                trend_direction=p["trend_direction"], months_analyzed=p["months_analyzed"],
            )
            await self._pred_repo.upsert(pred)

        risk_data = await self._risk.assess(user_id)
        risk_data["user_id"] = user_id
        risk_data["overspending_categories"] = risk_data.pop("categories", [])
        risk = BudgetRisk(**risk_data)
        await self._risk_repo.upsert(risk)

        opps = await self._savings.detect(user_id)
        opp_models = [BudgetOpportunity(**o) for o in opps]
        if opp_models:
            await self._opp_repo.bulk_create(opp_models)
        await self._opp_repo.delete_old(user_id, 50)

        await self._publish_event("budget_intelligence.updated", user_id, {
            "period": period, "budget_score": intelligence.budget_score,
        })
        await self._publish_event("budget_recommendation.generated", user_id, {
            "count": len(rec_models),
        })
        await self._publish_event("budget_forecast.updated", user_id, {
            "period": period, "predictions": len(forecast.get("predictions", [])),
        })
        await self._publish_event("budget_risk.updated", user_id, {
            "period": period, "risk_level": risk.overall_risk_level,
        })
        await self._publish_event("budget_opportunity.detected", user_id, {
            "count": len(opp_models), "total_savings": sum(o.potential_savings for o in opp_models),
        })

        return {
            "period": intelligence.period,
            "budget_score": intelligence.budget_score,
            "recommendations_count": len(rec_models),
            "opportunities_count": len(opp_models),
            "message": "Budget intelligence generated successfully.",
        }

    async def recalculate(self, user_id: str) -> dict:
        now = datetime.utcnow()
        period = f"{now.year}-{now.month:02d}"

        intelligence = await self._smart_budget.generate_budget(user_id)
        await self._intel_repo.upsert(intelligence)

        recs = await self._recommendation.generate(user_id)
        rec_models = [BudgetRecommendation(**r) for r in recs]
        await self._rec_repo.bulk_create(rec_models)
        await self._rec_repo.delete_old(user_id, 50)

        forecast = await self._forecast.forecast(user_id)
        for p in forecast.get("predictions", []):
            pred = BudgetPrediction(
                user_id=user_id, period=period, category=p["category"],
                predicted_spending=p["predicted_spending"],
                predicted_utilization=p["predicted_utilization"],
                confidence_upper=p["confidence_upper"], confidence_lower=p["confidence_lower"],
                trend_direction=p["trend_direction"], months_analyzed=p["months_analyzed"],
            )
            await self._pred_repo.upsert(pred)

        risk_data = await self._risk.assess(user_id)
        risk_data["user_id"] = user_id
        risk_data["overspending_categories"] = risk_data.pop("categories", [])
        risk = BudgetRisk(**risk_data)
        await self._risk_repo.upsert(risk)

        opps = await self._savings.detect(user_id)
        opp_models = [BudgetOpportunity(**o) for o in opps]
        await self._opp_repo.bulk_create(opp_models)
        await self._opp_repo.delete_old(user_id, 50)

        await self._publish_event("budget_intelligence.updated", user_id, {
            "period": period, "budget_score": intelligence.budget_score,
        })

        return {
            "period": intelligence.period,
            "budget_score": intelligence.budget_score,
            "recommendations_count": len(rec_models),
            "opportunities_count": len(opp_models),
            "message": "Budget intelligence recalculated successfully.",
        }

    async def get_current(self, user_id: str) -> BudgetIntelligence | None:
        return await self._intel_repo.get_latest(user_id)

    async def get_recommendations(self, user_id: str) -> list[BudgetRecommendation]:
        return await self._rec_repo.get_active(user_id)

    async def get_optimization(self, user_id: str) -> dict:
        return await self._optimization.optimize(user_id)

    async def get_trends(self, user_id: str) -> dict:
        return await self._forecast.forecast(user_id)

    async def get_risk(self, user_id: str) -> BudgetRisk | None:
        return await self._risk_repo.get_latest(user_id)

    async def get_opportunities(self, user_id: str) -> list[BudgetOpportunity]:
        return await self._opp_repo.get_active(user_id)

    async def _publish_event(self, event_type: str, user_id: str, payload: dict) -> None:
        event = Event(event_type=event_type, user_id=user_id, payload=payload)
        await global_event_bus.publish(event)
