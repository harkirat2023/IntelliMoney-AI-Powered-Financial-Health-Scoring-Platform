import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import (
    FinancialGoal, GoalRecommendation,
)
from app.goal_planning.repositories.goal_repositories import (
    MongoFinancialGoalRepository, MongoGoalPredictionRepository,
    MongoGoalRecommendationRepository,
)
from app.goal_planning.services.goal_feasibility_service import GoalFeasibilityService
from app.goal_planning.services.goal_notification_service import GoalNotificationService
from app.goal_planning.services.goal_prediction_service import GoalPredictionService
from app.goal_planning.services.goal_progress_service import GoalProgressService
from app.goal_planning.services.goal_recommendation_service import GoalRecommendationService
from app.goal_planning.services.savings_plan_service import SavingsPlanService
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.infrastructure.messaging.events import Event

logger = logging.getLogger(__name__)


class GoalPlanningService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._goal_repo = MongoFinancialGoalRepository(db)
        self._prediction_repo = MongoGoalPredictionRepository(db)
        self._recommendation_repo = MongoGoalRecommendationRepository(db)
        self._feasibility = GoalFeasibilityService(db)
        self._savings_plan = SavingsPlanService(db)
        self._prediction = GoalPredictionService(db)
        self._progress = GoalProgressService(db)
        self._recommendation = GoalRecommendationService(db)
        self._notification = GoalNotificationService(db)

    async def create_goal(self, user_id: str, data: dict) -> dict:
        goal = FinancialGoal(
            user_id=user_id, goal_type=data["goal_type"],
            name=data["name"], target_amount=data["target_amount"],
            current_amount=data.get("current_amount", 0.0),
            monthly_contribution=data.get("monthly_contribution", 0.0),
            target_date=data.get("target_date", ""),
            priority=data.get("priority", "medium"),
            category=data.get("category", ""),
            description=data.get("description", ""),
            auto_adjust=data.get("auto_adjust", True),
            start_date=datetime.utcnow().strftime("%Y-%m-%d"),
        )

        feasibility = await self._feasibility.analyze(
            user_id, goal.goal_type, goal.target_amount,
            goal.target_date, goal.monthly_contribution,
        )
        goal.feasibility_score = feasibility["feasibility_score"]
        goal.affordability_score = feasibility["affordability_score"]
        goal.estimated_months = feasibility["estimated_months"]
        goal.risk_level = feasibility["risk_level"]
        goal.confidence_score = feasibility["confidence_score"]
        goal.status = "active" if feasibility["feasible"] else "at_risk"

        goal = await self._goal_repo.create(goal)

        savings_plan = await self._savings_plan.generate_plan(
            user_id, goal.target_amount, goal.monthly_contribution, goal.current_amount)
        if goal.monthly_contribution <= 0:
            goal.monthly_contribution = savings_plan["monthly_contribution"]
            await self._goal_repo.update(goal.id, {"monthly_contribution": goal.monthly_contribution})

        prediction = await self._prediction.predict(goal)
        progress = await self._progress.track_progress(goal)

        goal.completion_percentage = progress.progress_percentage
        await self._goal_repo.update(goal.id, {"completion_percentage": goal.completion_percentage})

        recs = await self._recommendation.generate(user_id, goal)

        await self._publish_event("goal.created", user_id, {
            "goal_id": goal.id, "goal_type": goal.goal_type,
            "target_amount": goal.target_amount, "feasibility_score": goal.feasibility_score,
        })

        goal_resp = self._goal_to_dict(goal)
        return {
            "goal": goal_resp,
            "prediction": self._prediction_to_dict(prediction),
            "recommendations": [self._rec_to_dict(r) for r in recs],
            "message": f"Goal '{goal.name}' created successfully",
        }

    async def update_goal(self, goal_id: str, user_id: str, data: dict) -> FinancialGoal | None:
        goal = await self._goal_repo.get_by_id(goal_id)
        if not goal or goal.user_id != user_id:
            return None

        allowed = ["name", "target_amount", "current_amount", "monthly_contribution",
                    "target_date", "priority", "status", "category", "description", "auto_adjust"]
        update = {k: v for k, v in data.items() if k in allowed and v is not None}

        if "target_amount" in update or "monthly_contribution" in update:
            tgt = update.get("target_amount", goal.target_amount)
            mc = update.get("monthly_contribution", goal.monthly_contribution)
            curr = update.get("current_amount", goal.current_amount)
            feasibility = await self._feasibility.analyze(user_id, goal.goal_type, tgt, goal.target_date, mc)
            update["feasibility_score"] = feasibility["feasibility_score"]
            update["affordability_score"] = feasibility["affordability_score"]
            update["estimated_months"] = feasibility["estimated_months"]
            update["risk_level"] = feasibility["risk_level"]
            update["confidence_score"] = feasibility["confidence_score"]

        await self._goal_repo.update(goal_id, update)

        if "current_amount" in update or "monthly_contribution" in update:
            goal = await self._goal_repo.get_by_id(goal_id)
            await self._prediction.predict(goal)
            await self._progress.track_progress(goal)

        await self._publish_event("goal.updated", user_id, {
            "goal_id": goal_id, "changes": list(update.keys()),
        })

        return await self._goal_repo.get_by_id(goal_id)

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        goal = await self._goal_repo.get_by_id(goal_id)
        if not goal or goal.user_id != user_id:
            return False
        deleted = await self._goal_repo.delete(goal_id)
        if deleted:
            await self._publish_event("goal.updated", user_id, {
                "goal_id": goal_id, "action": "deleted",
            })
        return deleted

    async def get_goals(self, user_id: str, status: str | None = None) -> list[dict]:
        goals = await self._goal_repo.get_by_user(user_id, status)
        return [self._goal_to_dict(g) for g in goals]

    async def get_goal(self, goal_id: str, user_id: str) -> FinancialGoal | None:
        goal = await self._goal_repo.get_by_id(goal_id)
        if not goal or goal.user_id != user_id:
            return None
        return goal

    async def analyze(self, user_id: str, data: dict) -> dict:
        return await self._feasibility.analyze(
            user_id, data.get("goal_type", "custom"), data["target_amount"],
            data.get("target_date", ""), data.get("monthly_contribution", 0.0))

    async def recalculate(self, user_id: str) -> dict:
        goals = await self._goal_repo.get_active(user_id)
        goals_updated = 0
        predictions_generated = 0

        for goal in goals:
            feasibility = await self._feasibility.analyze(
                user_id, goal.goal_type, goal.target_amount,
                goal.target_date, goal.monthly_contribution)
            await self._goal_repo.update(goal.id, {
                "feasibility_score": feasibility["feasibility_score"],
                "affordability_score": feasibility["affordability_score"],
                "estimated_months": feasibility["estimated_months"],
                "risk_level": feasibility["risk_level"],
                "confidence_score": feasibility["confidence_score"],
                "status": "active" if feasibility["feasible"] else "at_risk",
            })
            goals_updated += 1

            goal.feasibility_score = feasibility["feasibility_score"]
            await self._prediction.predict(goal)
            predictions_generated += 1

            goal = await self._goal_repo.get_by_id(goal.id)
            await self._progress.track_progress(goal)

        recs = await self._recommendation.generate(user_id)
        notifications = await self._notification.check_and_notify(user_id)

        await self._publish_event("goal.updated", user_id, {
            "goals_updated": goals_updated, "predictions": predictions_generated,
        })

        return {
            "goals_updated": goals_updated,
            "predictions_generated": predictions_generated,
            "recommendations_generated": len(recs),
            "message": f"Recalculated {goals_updated} goals",
        }

    async def get_recommendations(self, user_id: str) -> list[GoalRecommendation]:
        return await self._recommendation.get_by_user(user_id)

    async def get_progress(self, user_id: str) -> list[dict]:
        goals = await self._goal_repo.get_active(user_id)
        result = []
        for g in goals:
            progress_list = await self._progress.get_by_goal(g.id)
            result.append({
                "goal": self._goal_to_dict(g),
                "progress": [self._progress_to_dict(p) for p in progress_list],
            })
        return result

    def _goal_to_dict(self, goal: FinancialGoal) -> dict:
        return {k: v for k, v in goal.__dict__.items() if not k.startswith("_")}

    def _prediction_to_dict(self, prediction) -> dict:
        return {k: v for k, v in prediction.__dict__.items() if not k.startswith("_")}

    def _rec_to_dict(self, rec: GoalRecommendation) -> dict:
        return {k: v for k, v in rec.__dict__.items() if not k.startswith("_")}

    def _progress_to_dict(self, progress) -> dict:
        return {k: v for k, v in progress.__dict__.items() if not k.startswith("_")}

    async def _publish_event(self, event_type: str, user_id: str, payload: dict) -> None:
        event = Event(event_type=event_type, user_id=user_id, payload=payload)
        await global_event_bus.publish(event)
