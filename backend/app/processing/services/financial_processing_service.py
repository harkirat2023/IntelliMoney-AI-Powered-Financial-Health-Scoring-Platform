import logging
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("intellimoney")

from app.domain.financial_transactions.models import FinancialTransaction
from app.infrastructure.database.repositories.expense_repository import MongoExpenseRepository
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.utils.date_utils import month_bounds
from app.infrastructure.messaging.events import Event
from app.processing.models.processing_batch import ProcessingBatch, ProcessingSummary
from app.processing.repositories.budget_usage_repository import MongoBudgetUsageRepository
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository
from app.processing.repositories.financial_metrics_repository import MongoFinancialMetricsRepository
from app.processing.repositories.processing_batch_repository import MongoProcessingBatchRepository
from app.processing.services.budget_alert_service import BudgetAlertService
from app.processing.services.budget_processing_service import BudgetProcessingService
from app.processing.services.cash_flow_service import CashFlowService
from app.processing.services.dashboard_aggregation_service import DashboardAggregationService
from app.processing.services.expense_generation_service import ExpenseGenerationService
from app.processing.services.financial_metrics_service import FinancialMetricsService
from app.processing.services.savings_service import SavingsService
from app.utils.date_utils import utc_now


class FinancialProcessingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        expense_repo = MongoExpenseRepository(db)
        financial_tx_repo = MongoFinancialTransactionRepository(db)
        budget_usage_repo = MongoBudgetUsageRepository(db)
        cash_flow_repo = MongoCashFlowRepository(db)
        dash_repo = MongoDashboardMetricsRepository(db)
        metrics_repo = MongoFinancialMetricsRepository(db)
        batch_repo = MongoProcessingBatchRepository(db)

        self._expense_service = ExpenseGenerationService(expense_repo, financial_tx_repo)
        self._budget_service = BudgetProcessingService(db, budget_usage_repo)
        self._cash_flow_service = CashFlowService(cash_flow_repo)
        self._savings_service = SavingsService(cash_flow_repo)
        self._dash_service = DashboardAggregationService(financial_tx_repo, dash_repo)
        self._metrics_service = FinancialMetricsService(expense_repo, metrics_repo)
        self._alert_service = BudgetAlertService(db)
        self._batch_repo = batch_repo
        self._financial_tx_repo = financial_tx_repo

    async def process(
        self, user_id: str, tx_ids: list[str], force: bool = False,
    ) -> dict:
        batch_id = uuid4().hex
        batch = ProcessingBatch(
            batch_id=batch_id,
            user_id=user_id,
            status="processing",
            total=len(tx_ids),
            created_at=utc_now(),
        )
        await self._batch_repo.create(batch)
        await self._publish_event("processing.batch.started", user_id, {"batch_id": batch_id, "tx_count": len(tx_ids)})

        transactions: list[FinancialTransaction] = []
        errors: list[dict] = []
        for tx_id in tx_ids:
            tx = await self._financial_tx_repo.get_by_id(tx_id)
            if not tx:
                errors.append({"transaction_id": tx_id, "stage": "validation", "message": "Transaction not found"})
                logger.warning("tx_not_found user=%s tx=%s", user_id, tx_id)
                continue
            if tx.processed_at and not force:
                errors.append({"transaction_id": tx_id, "stage": "dedup", "message": "Already processed"})
                continue
            if not force and tx.review_status == "review_required":
                errors.append({"transaction_id": tx_id, "stage": "validation", "message": "Review required, use force=true"})
                continue
            transactions.append(tx)

        if not transactions and not errors:
            batch.status = "completed"
            batch.processed = 0
            batch.failed = 0
            batch.completed_at = utc_now()
            batch.summary = ProcessingSummary()
            await self._batch_repo.update_status(batch_id, "completed", 0, 0, [])
            await self._publish_event("processing.batch.completed", user_id, {"batch_id": batch_id, "tx_count": 0})
            logger.info("batch_empty user=%s batch=%s", user_id, batch_id)
            return {"batch_id": batch_id, "status": "completed", "total": 0, "processed": 0, "failed": 0, "errors": [], "summary": {}}

        created_ids, skipped_ids, gen_errors = await self._expense_service.generate_expenses(transactions, force)
        errors.extend(gen_errors)
        for cid in created_ids:
            await self._publish_event("processing.expense.created", user_id, {"expense_id": cid})

        budget_states = await self._budget_service.update_budget_usage(user_id)
        for bs in budget_states:
            await self._publish_event("processing.budget.updated", user_id, {
                "budget_id": bs["budget_id"], "category": bs["category"],
                "state": bs["state"], "percentage": bs["percentage_used"],
            })

        now = utc_now()
        period_start, period_end = month_bounds(now.year, now.month)
        period_txs = await self._financial_tx_repo.find_by_date_range(user_id, period_start, period_end)
        if not period_txs:
            period_txs = transactions

        cash_flow = await self._cash_flow_service.calculate_cash_flow(user_id, period_txs)
        await self._publish_event("processing.cashflow.updated", user_id, {
            "year": cash_flow.year, "month": cash_flow.month,
            "total_income": cash_flow.total_income, "total_expenses": cash_flow.total_expenses,
        })

        savings_data = await self._savings_service.calculate_savings(user_id, period_txs)

        metrics = await self._metrics_service.compute_metrics(user_id, savings_data["savings_rate"], budget_states)
        await self._publish_event("processing.financial_metrics.updated", user_id, {
            "score": metrics.score, "risk_level": metrics.risk_level, "savings_rate": metrics.savings_rate,
        })

        dashboard = await self._dash_service.aggregate(user_id, period_txs, savings_data, budget_states)
        await self._publish_event("processing.dashboard.updated", user_id, {"period": dashboard.period})

        alerts = await self._alert_service.generate_alerts(user_id, budget_states)

        processed_count = len(created_ids)
        failed_count = len(errors)

        summary = ProcessingSummary(
            expenses_created=len(created_ids),
            expenses_skipped=len(skipped_ids),
            budget_usage_updated=len(budget_states),
            dashboard_metrics_updated=1,
            financial_metrics_updated=1,
            cash_flow_updated=1,
            alerts_generated=len(alerts),
        )

        logger.info("batch_completed user=%s batch=%s total=%d processed=%d failed=%d",
                     user_id, batch_id, len(tx_ids), processed_count, failed_count)
        batch.status = "completed" if not failed_count else "failed"
        batch.processed = processed_count
        batch.failed = failed_count
        batch.errors = errors
        batch.summary = summary
        batch.completed_at = utc_now()
        await self._batch_repo.update_status(batch_id, "completed", processed_count, failed_count, errors, summary)

        await self._publish_event("processing.batch.completed", user_id, {
            "batch_id": batch_id, "tx_count": len(transactions),
        })

        return {
            "batch_id": batch_id,
            "status": "completed",
            "total": len(tx_ids),
            "processed": processed_count,
            "failed": failed_count,
            "errors": errors,
            "summary": summary.model_dump(),
        }

    async def process_all(self, user_id: str, force: bool = False, limit: int = 100) -> dict:
        if force:
            txs = await self._financial_tx_repo.find_by_user(user_id, limit=limit, offset=0)
            unprocessed_ids = [tx.id for tx in txs]
        else:
            txs = await self._financial_tx_repo.find_unprocessed(user_id, limit=limit)
            unprocessed_ids = [tx.id for tx in txs]
        if not unprocessed_ids:
            return {"batch_id": None, "status": "completed", "total": 0, "processed": 0, "failed": 0, "errors": [], "summary": {}}
        return await self.process(user_id, unprocessed_ids, force)

    async def reprocess(self, user_id: str, tx_ids: list[str], reason: str | None = None) -> dict:
        for tx_id in tx_ids:
            tx = await self._financial_tx_repo.get_by_id(tx_id)
            if not tx or tx.user_id != user_id:
                continue
            await self._financial_tx_repo.update_fields(tx_id, {"processed_at": None})
            expense = await self._db.expenses.find_one({"user_id": user_id, "transaction_id": tx_id})
            if expense:
                await self._db.expenses.delete_one({"_id": expense["_id"]})
            await self._db.budget_usage.delete_many({"user_id": user_id, "transaction_id": tx_id})
        return await self.process(user_id, tx_ids, force=True)

    async def get_status(self, batch_id: str, user_id: str) -> dict | None:
        batch = await self._batch_repo.get_by_batch_id(batch_id)
        if not batch or batch.user_id != user_id:
            return None
        return {
            "batch_id": batch.batch_id,
            "status": batch.status,
            "total": batch.total,
            "processed": batch.processed,
            "failed": batch.failed,
            "errors": batch.errors,
            "summary": batch.summary.model_dump() if batch.summary else None,
            "created_at": batch.created_at,
            "completed_at": batch.completed_at,
        }

    async def get_history(self, user_id: str, limit: int = 20, offset: int = 0) -> list[dict]:
        batches = await self._batch_repo.get_by_user(user_id, limit, offset)
        return [
            {
                "batch_id": b.batch_id,
                "status": b.status,
                "total": b.total,
                "processed": b.processed,
                "failed": b.failed,
                "created_at": b.created_at,
                "completed_at": b.completed_at,
            }
            for b in batches
        ]

    async def _publish_event(self, event_type: str, user_id: str, payload: dict) -> None:
        event = Event(event_type=event_type, user_id=user_id, payload=payload)
        await global_event_bus.publish(event)
