import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.goal_planning.models.goal_models import FinancialGoal, GoalProgress
from app.goal_planning.repositories.goal_repositories import (
    GoalProgressRepository, MongoFinancialGoalRepository,
    MongoGoalProgressRepository,
)

logger = logging.getLogger(__name__)

MILESTONES = [
    (0.25, "25% Complete"),
    (0.50, "Halfway There"),
    (0.75, "75% Complete"),
    (1.0, "Goal Complete"),
]


class GoalProgressService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._progress_repo: GoalProgressRepository = MongoGoalProgressRepository(db)
        self._goal_repo = MongoFinancialGoalRepository(db)
        self._db = db

    async def track_progress(self, goal: FinancialGoal) -> GoalProgress:
        now = datetime.utcnow()
        period = now.strftime("%Y-%m")
        existing = await self._progress_repo.get_by_goal_and_period(goal.id, period)
        previous = await self._progress_repo.get_latest_by_goal(goal.id)

        prev_amount = previous.current_amount if previous else goal.current_amount

        pct = min(100, round(goal.current_amount / max(goal.target_amount, 1) * 100, 1))

        milestone_hit = False
        milestone_label = ""
        for threshold, label in MILESTONES:
            if prev_amount < threshold * goal.target_amount <= goal.current_amount:
                milestone_hit = True
                milestone_label = label
                break

        monthly = 0.0
        if existing:
            monthly = goal.current_amount - existing.current_amount
        else:
            monthly = goal.current_amount - (previous.current_amount if previous else 0)

        contribution_count = (existing.contribution_count if existing else 0) + (1 if monthly > 0 else 0)
        skipped_months = 0
        if existing and monthly <= 0:
            skipped_months = (existing.skipped_months or 0) + 1

        is_on_track = monthly >= (goal.monthly_contribution or 0) or pct >= 100

        progress = GoalProgress(
            goal_id=goal.id, user_id=goal.user_id, period=period,
            previous_amount=prev_amount,
            current_amount=goal.current_amount,
            monthly_contribution=monthly,
            contribution_count=contribution_count,
            skipped_months=skipped_months,
            milestone_hit=milestone_hit,
            milestone_label=milestone_label,
            progress_percentage=pct,
            on_track=is_on_track,
            notes="",
        )

        if existing:
            progress.id = existing.id

        progress = await self._progress_repo.create(progress)
        return progress

    async def get_by_goal(self, goal_id: str) -> list[GoalProgress]:
        return await self._progress_repo.get_by_goal(goal_id)

    async def get_latest(self, goal_id: str) -> GoalProgress | None:
        return await self._progress_repo.get_latest_by_goal(goal_id)

    async def get_by_user(self, user_id: str) -> list[GoalProgress]:
        return await self._progress_repo.get_by_user(user_id)

    async def check_missed_milestones(self, goal: FinancialGoal) -> str | None:
        latest = await self._progress_repo.get_latest_by_goal(goal.id)
        if not latest:
            return None
        if latest.skipped_months >= 3:
            return f"No contributions for {latest.skipped_months} months. Consider adjusting your goal."
        if latest.progress_percentage < 10 and goal.created_at:
            age_days = (datetime.utcnow() - goal.created_at).days
            if age_days > 60:
                return "Very little progress after 2 months. Consider reducing target or increasing contributions."
        return None
