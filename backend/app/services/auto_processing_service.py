import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.intelligence_service import get_intelligence_service
from app.processing.services.financial_processing_service import FinancialProcessingService
from app.health.services.financial_health_service import FinancialHealthService
from app.dashboard.services import NotificationService

logger = logging.getLogger("intellimoney")


class AutoProcessingService:
    """Runs the full automatic flow after bank sync:

    Bank transactions -> ML categorization -> budget update -> cash flow -> dashboard ->
    financial health recalculation -> notification.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def process_synced(self, user_id: str, bank_account_id: str) -> dict:
        result = {
            "categorized": 0,
            "processed": 0,
            "health_recalculated": False,
            "errors": [],
        }

        try:
            intelligence = get_intelligence_service(self._db)
            ai_result = await intelligence.process_pending(user_id, bank_account_id=bank_account_id)
            result["categorized"] = ai_result.processed
        except Exception as exc:  # keep the rest of the flow working
            logger.error("auto_processing categorization failed user=%s error=%s", user_id, exc)
            result["errors"].append(f"categorization: {exc}")

        try:
            processing = FinancialProcessingService(self._db)
            proc_result = await processing.process_all(user_id, limit=5000)
            result["processed"] = proc_result.get("processed", 0)
        except Exception as exc:
            logger.error("auto_processing financial engine failed user=%s error=%s", user_id, exc)
            result["errors"].append(f"financial_engine: {exc}")

        try:
            health = FinancialHealthService(self._db)
            await health.recalculate(user_id)
            result["health_recalculated"] = True
        except Exception as exc:
            logger.error("auto_processing health recalc failed user=%s error=%s", user_id, exc)
            result["errors"].append(f"health: {exc}")

        try:
            await NotificationService(self._db).create_notification(
                user_id=user_id,
                ntype="sync",
                title="Transactions imported",
                message="Your latest bank transactions were imported, categorized and reflected in your dashboard, budgets and financial health.",
            )
        except Exception as exc:
            logger.error("auto_processing notification failed user=%s error=%s", user_id, exc)
            result["errors"].append(f"notification: {exc}")

        logger.info(
            "auto_processing complete user=%s categorized=%d processed=%d health=%s errors=%s",
            user_id, result["categorized"], result["processed"],
            result["health_recalculated"], len(result["errors"]),
        )
        return result
