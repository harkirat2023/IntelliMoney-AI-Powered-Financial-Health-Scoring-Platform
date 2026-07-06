import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.repositories.financial_health_repository import (
    MongoFinancialHealthRepository,
)
from app.health.repositories.health_history_repository import (
    MongoHealthHistoryRepository,
)
from app.health.repositories.recommendation_repository import (
    MongoRecommendationRepository,
)
from app.health.repositories.risk_repository import MongoRiskRepository
from app.health.schemas import (
    CalculateResponse, HealthBreakdownResponse, HealthCurrentResponse,
    HealthHistoryResponse, HealthRecommendationItem, RiskAssessmentResponse, TrendAnalysis,
)
from app.health.services.health_history_service import HealthHistoryService
from app.health.services.health_score_calculator import HealthScoreCalculator
from app.health.services.health_aggregation_service import HealthAggregationService
from app.health.services.recommendation_engine import RecommendationEngine
from app.health.services.risk_assessment_service import RiskAssessmentService
from app.health.services.trend_analysis_service import TrendAnalysisService
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.infrastructure.messaging.events import Event
from app.utils.date_utils import utc_now

logger = logging.getLogger("intellimoney")


class FinancialHealthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        health_repo = MongoFinancialHealthRepository(db)
        history_repo = MongoHealthHistoryRepository(db)
        risk_repo = MongoRiskRepository(db)
        rec_repo = MongoRecommendationRepository(db)

        self._calculator = HealthScoreCalculator(db)
        self._risk_service = RiskAssessmentService(risk_repo)
        self._history_service = HealthHistoryService(history_repo)
        self._trend_service = TrendAnalysisService(history_repo)
        self._rec_engine = RecommendationEngine(rec_repo)
        self._aggregator = HealthAggregationService(health_repo, history_repo, risk_repo, rec_repo)
        self._health_repo = health_repo

    async def calculate(self, user_id: str) -> CalculateResponse:
        now = utc_now()
        period = f"{now.year}-{now.month:02d}"

        existing = await self._health_repo.get_by_user_and_period(user_id, period)
        if existing:
            return CalculateResponse(
                period=existing.period, score=existing.score,
                risk_level=existing.risk_level,
                message="Health score already calculated for this period",
            )

        health = await self._calculator.calculate(user_id)
        health = await self._health_repo.upsert(health)
        await self._history_service.record(health)
        await self._risk_service.assess(user_id, health)
        await self._rec_engine.generate(user_id, health)

        await self._publish_event("financial_health.updated", user_id, {
            "period": health.period, "score": health.score, "risk_level": health.risk_level,
        })

        logger.info("health_calculated user=%s period=%s score=%d", user_id, period, health.score)
        return CalculateResponse(
            period=health.period, score=health.score,
            risk_level=health.risk_level,
            message="Health score calculated successfully",
        )

    async def recalculate(self, user_id: str) -> CalculateResponse:
        now = utc_now()
        period = f"{now.year}-{now.month:02d}"

        health = await self._calculator.calculate(user_id)
        health = await self._health_repo.upsert(health)
        await self._history_service.record(health)
        await self._risk_service.assess(user_id, health)
        await self._rec_engine.generate(user_id, health)

        await self._publish_event("financial_health.recalculated", user_id, {
            "period": health.period, "score": health.score, "risk_level": health.risk_level,
        })

        logger.info("health_recalculated user=%s period=%s score=%d", user_id, period, health.score)
        return CalculateResponse(
            period=health.period, score=health.score,
            risk_level=health.risk_level,
            message="Health score recalculated successfully",
        )

    async def get_current(self, user_id: str) -> HealthCurrentResponse | None:
        return await self._aggregator.get_current(user_id)

    async def get_history(self, user_id: str, limit: int = 36) -> HealthHistoryResponse:
        return await self._aggregator.get_history(user_id, limit)

    async def get_trends(self, user_id: str, months: int = 12) -> TrendAnalysis:
        return await self._aggregator.get_trends(user_id, months)

    async def get_breakdown(self, user_id: str) -> HealthBreakdownResponse | None:
        return await self._aggregator.get_breakdown(user_id)

    async def get_recommendations(self, user_id: str) -> list[HealthRecommendationItem]:
        return await self._aggregator.get_recommendations(user_id)

    async def get_risk(self, user_id: str) -> RiskAssessmentResponse | None:
        return await self._aggregator.get_risk(user_id)

    async def _publish_event(self, event_type: str, user_id: str, payload: dict) -> None:
        event = Event(event_type=event_type, user_id=user_id, payload=payload)
        await global_event_bus.publish(event)
