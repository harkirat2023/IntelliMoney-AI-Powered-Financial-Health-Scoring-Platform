import logging
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import GoalNotification
from app.goal_planning.repositories.goal_repositories import (
    GoalNotificationRepository, MongoGoalNotificationRepository,
)

logger = logging.getLogger(__name__)


class GoalNotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._repo: GoalNotificationRepository = MongoGoalNotificationRepository(db)
        self._db = db

    async def check_and_notify(self, user_id: str) -> list[GoalNotification]:
        notifications = []
        goals = await self._get_active_goals(user_id)

        for g in goals:
            if g.completion_percentage >= 100:
                n = GoalNotification(
                    user_id=user_id, goal_id=g.id,
                    notification_type="goal_completed",
                    title=f"Goal Completed: {g.name}",
                    message=f"Congratulations! You've reached your target of ₹{g.target_amount:,.0f} for {g.name}.",
                    severity="success", actionable=False,
                )
                notifications.append(await self._repo.create(n))

            elif g.completion_percentage >= 75:
                n = GoalNotification(
                    user_id=user_id, goal_id=g.id,
                    notification_type="milestone_reached",
                    title=f"75% Complete: {g.name}",
                    message=f"You're 75% of the way to your ₹{g.target_amount:,.0f} goal for {g.name}. Keep going!",
                    severity="info", actionable=False,
                )
                notifications.append(await self._repo.create(n))

            elif g.status == "at_risk":
                n = GoalNotification(
                    user_id=user_id, goal_id=g.id,
                    notification_type="goal_at_risk",
                    title=f"Goal at Risk: {g.name}",
                    message=f"Your goal '{g.name}' is at risk. Current progress is {g.completion_percentage:.0f}%. Consider adjusting your plan.",
                    severity="warning", actionable=True,
                    action_data={"goal_id": g.id, "action": "review"},
                )
                notifications.append(await self._repo.create(n))

        goals_near_completion = [g for g in goals if 90 <= g.completion_percentage < 100]
        if len(goals_near_completion) >= 2:
            n = GoalNotification(
                user_id=user_id, goal_id="",
                notification_type="multi_goal_almost_done",
                title="Multiple Goals Almost Complete",
                message=f"You have {len(goals_near_completion)} goals above 90% completion!",
                severity="info", actionable=False,
            )
            notifications.append(await self._repo.create(n))

        return notifications

    async def mark_read(self, notification_id: str) -> bool:
        return await self._repo.mark_read(notification_id)

    async def mark_all_read(self, user_id: str) -> int:
        return await self._repo.mark_all_read(user_id)

    async def get_by_user(self, user_id: str) -> list[GoalNotification]:
        return await self._repo.get_by_user(user_id)

    async def cleanup_old(self, user_id: str, days: int = 90):
        before = datetime.utcnow() - timedelta(days=days)
        return await self._repo.delete_old(user_id, before)

    async def _get_active_goals(self, user_id: str):
        from app.goal_planning.repositories.goal_repositories import MongoFinancialGoalRepository
        repo = MongoFinancialGoalRepository(self._db)
        return await repo.get_active(user_id)
