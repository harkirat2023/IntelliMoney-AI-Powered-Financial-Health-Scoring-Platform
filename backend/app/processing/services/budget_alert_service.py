import logging
from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.date_utils import utc_now

logger = logging.getLogger("intellimoney")


ALERT_THRESHOLDS = [75, 90, 100]


class BudgetAlertService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    def _threshold_for_percentage(self, percentage: float) -> int | None:
        reached = [t for t in ALERT_THRESHOLDS if percentage >= t]
        return max(reached) if reached else None

    def _alert_message(self, category: str, percentage: float, threshold: int) -> str:
        if threshold >= 100:
            return f"{category} budget exceeded at {percentage:.2f}% usage."
        return f"{category} budget reached {threshold}% usage. Current usage is {percentage:.2f}%."

    async def generate_alerts(self, user_id: str, budget_states: list[dict]) -> list[dict]:
        now = utc_now()
        alerts = []

        for bs in budget_states:
            percentage = bs["percentage_used"]
            threshold = self._threshold_for_percentage(percentage)
            if threshold is None:
                continue

            budget_oid = bs["budget_id"]
            existing = await self._db.budget_alerts.find_one(
                {"user_id": user_id, "budget_id": budget_oid, "threshold": threshold}
            )
            if existing:
                await self._db.budget_alerts.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "percentage": percentage,
                            "message": self._alert_message(bs["category"], percentage, threshold),
                        }
                    },
                )
                continue

            message = self._alert_message(bs["category"], percentage, threshold)
            await self._db.budget_alerts.insert_one(
                {
                    "user_id": user_id,
                    "budget_id": budget_oid,
                    "threshold": threshold,
                    "percentage": percentage,
                    "message": message,
                    "created_at": now,
                    "read": False,
                    "email_queued": False,
                    "email_sent_at": None,
                }
            )
            alerts.append({
                "budget_id": budget_oid,
                "category": bs["category"],
                "threshold": threshold,
                "percentage": percentage,
                "message": message,
            })

        logger.info("budget_alerts_generated user=%s count=%d", user_id, len(alerts))
        return alerts
