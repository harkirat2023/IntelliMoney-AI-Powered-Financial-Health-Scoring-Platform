import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dashboard.schemas import (
    ActivityFeedItem, AIInsightItem, BudgetAlertItem, BudgetStatusWidget,
    CashFlowWidget, DashboardOverviewResponse, HealthScoreWidget,
    IncomeWidget, MonthlyTrendPoint, NotificationItem, RecentTransactionItem,
    RecurringWidget, SavingsWidget, SpendingHeatmapPoint, SpendingWidget,
    SubscriptionWidget, TopCategoryItem, UpcomingBillsWidget, AnalyticsResponse,
)
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.infrastructure.messaging.events import Event
from app.infrastructure.websocket.manager import connection_manager
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.processing.repositories.dashboard_metrics_repository import MongoDashboardMetricsRepository
from app.processing.repositories.financial_metrics_repository import MongoFinancialMetricsRepository
from app.utils.date_utils import month_bounds, utc_now
from app.utils.object_id import to_object_id

logger = logging.getLogger("intellimoney")


class DashboardService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._dash_repo = MongoDashboardMetricsRepository(db)
        self._metrics_repo = MongoFinancialMetricsRepository(db)
        self._cf_repo = MongoCashFlowRepository(db)
        self._tx_repo = MongoFinancialTransactionRepository(db)

    async def get_overview(self, user_id: str, period: str) -> DashboardOverviewResponse:
        dash = await self._dash_repo.get_by_user_and_period(user_id, period)
        metrics = await self._metrics_repo.get_latest_by_user(user_id)
        now = utc_now()
        p_start, p_end = month_bounds(now.year, now.month)

        health = None
        if metrics:
            health = HealthScoreWidget(
                score=metrics.score,
                risk_level=metrics.risk_level,
                savings_rate=metrics.savings_rate,
                budget_adherence=metrics.budget_adherence,
                expense_stability=metrics.expense_stability,
                discretionary_ratio=metrics.discretionary_ratio,
                trend=metrics.trend,
                month_over_month_change=metrics.month_over_month_change,
            )

        spending = None
        income = None
        top_cats = []
        monthly_trend = []
        budget_status = None
        if dash:
            spending = SpendingWidget(
                total_spending=dash.total_spending,
                expense_count=dash.expense_count,
                top_category=dash.spending_by_category[0]["category"] if dash.spending_by_category else None,
                top_category_amount=dash.spending_by_category[0]["amount"] if dash.spending_by_category else 0,
                spending_by_category=dash.spending_by_category,
            )
            income = IncomeWidget(
                total_income=dash.total_income,
                income_by_category=[],
            )
            top_cats = [
                TopCategoryItem(**c) for c in dash.spending_by_category[:5]
            ]
            for t in dash.monthly_trend:
                monthly_trend.append(MonthlyTrendPoint(
                    month=t["month"],
                    spending=t.get("spending", 0),
                    income=t.get("income", 0),
                    savings=round(t.get("income", 0) - t.get("spending", 0), 2),
                ))
            if dash.budget_overview:
                on_track = sum(1 for b in dash.budget_overview if b.get("state") == "safe")
                warning = sum(1 for b in dash.budget_overview if b.get("state") == "warning")
                over = sum(1 for b in dash.budget_overview if b.get("state") == "over")
                budget_status = BudgetStatusWidget(
                    budget_count=len(dash.budget_overview),
                    on_track=on_track,
                    warning=warning,
                    over=over,
                    budgets=dash.budget_overview,
                )

        cash_flow = None
        cf = await self._cf_repo.get_by_user_and_month(user_id, now.year, now.month)
        if cf:
            cash_flow = CashFlowWidget(
                total_income=cf.total_income,
                total_expenses=cf.total_expenses,
                net_cash_flow=cf.net_cash_flow,
                expense_by_category=cf.expense_by_category,
                income_by_category=cf.income_by_category,
            )

        savings = None
        if dash:
            prev_period = f"{now.year}-{now.month - 1:02d}" if now.month > 1 else f"{now.year - 1}-12"
            prev_dash = await self._dash_repo.get_by_user_and_period(user_id, prev_period)
            savings = SavingsWidget(
                net_savings=dash.net_savings,
                savings_rate=dash.savings_rate,
                previous_savings_rate=prev_dash.savings_rate if prev_dash else None,
            )

        recent_expenses = []
        expenses_cursor = self._db.expenses.find(
            {"user_id": to_object_id(user_id)}
        ).sort("date", -1).limit(5)
        async for exp in expenses_cursor:
            recent_expenses.append({
                "id": str(exp["_id"]),
                "description": exp.get("description", ""),
                "amount": float(exp.get("amount", 0)),
                "category": exp.get("category", ""),
                "date": exp.get("date", "").isoformat() if hasattr(exp.get("date"), "isoformat") else str(exp.get("date", "")),
                "merchant": exp.get("merchant"),
            })

        recurring_widget = await self._get_recurring_widget(user_id)
        subscription_widget = await self._get_subscription_widget(user_id)
        upcoming_widget = await self._get_upcoming_bills(user_id)

        ai_insights = await self._get_ai_insights(user_id)
        budget_alerts = await self._get_budget_alerts(user_id)
        heatmap = await self._get_spending_heatmap(user_id, p_start, p_end)
        activity = await self._get_activity_feed(user_id)

        return DashboardOverviewResponse(
            health_score=health,
            spending=spending,
            income=income,
            savings=savings,
            cash_flow=cash_flow,
            budget_status=budget_status,
            recent_transactions=[RecentTransactionItem(**e) for e in recent_expenses],
            recurring=recurring_widget,
            subscriptions=subscription_widget,
            upcoming_bills=upcoming_widget,
            ai_insights=ai_insights,
            budget_alerts=budget_alerts,
            top_categories=top_cats,
            monthly_trend=monthly_trend,
            spending_heatmap=heatmap,
            activity=activity,
        )

    async def get_analytics(self, user_id: str, period: str) -> AnalyticsResponse:
        dash = await self._dash_repo.get_by_user_and_period(user_id, period)
        if not dash:
            return AnalyticsResponse(
                total_spending=0, total_income=0, net_savings=0, savings_rate=0,
                expense_count=0, average_daily_spending=0, busiest_day=None,
            )

        avg_daily = round(dash.total_spending / max(dash.expense_count, 1), 2) if dash.expense_count else 0

        return AnalyticsResponse(
            total_spending=dash.total_spending,
            total_income=dash.total_income,
            net_savings=dash.net_savings,
            savings_rate=dash.savings_rate,
            expense_count=dash.expense_count,
            average_daily_spending=avg_daily,
            busiest_day=None,
            top_merchants=dash.top_merchants,
            spending_by_category=dash.spending_by_category,
            monthly_trend=[
                MonthlyTrendPoint(
                    month=t["month"],
                    spending=t.get("spending", 0),
                    income=t.get("income", 0),
                    savings=round(t.get("income", 0) - t.get("spending", 0), 2),
                ) for t in dash.monthly_trend
            ],
            budget_overview=dash.budget_overview,
        )

    async def _get_recurring_widget(self, user_id: str) -> RecurringWidget | None:
        cursor = self._db.recurring_expenses.find(
            {"user_id": to_object_id(user_id), "is_active": True}
        ).limit(10)
        items = []
        total = 0.0
        async for r in cursor:
            amount = float(r.get("amount", 0))
            total += amount
            items.append({
                "id": str(r["_id"]),
                "description": r.get("description", ""),
                "amount": amount,
                "frequency": r.get("frequency", ""),
            })
        return RecurringWidget(
            total_monthly=round(total, 2),
            upcoming_count=len(items),
            items=items,
        ) if items else None

    async def _get_subscription_widget(self, user_id: str) -> SubscriptionWidget | None:
        cursor = self._db.subscriptions.find(
            {"user_id": to_object_id(user_id), "is_active": True}
        ).limit(20)
        items = []
        monthly_total = 0.0
        async for s in cursor:
            amount = float(s.get("amount", 0))
            freq = s.get("frequency", "monthly")
            monthly = amount if freq == "monthly" else amount / 12
            monthly_total += monthly
            items.append({
                "id": str(s["_id"]),
                "description": s.get("description", ""),
                "amount": amount,
                "frequency": freq,
            })
        return SubscriptionWidget(
            total_monthly=round(monthly_total, 2),
            total_yearly=round(monthly_total * 12, 2),
            active_count=len(items),
            items=items,
        ) if items else None

    async def _get_upcoming_bills(self, user_id: str) -> UpcomingBillsWidget | None:
        now = utc_now()
        cursor = self._db.recurring_expenses.find(
            {"user_id": to_object_id(user_id), "is_active": True, "next_expected_date": {"$lte": now.replace(day=1, month=now.month + 1 if now.month < 12 else 1)}}
        ).sort("next_expected_date", 1).limit(10)
        bills = []
        total = 0.0
        async for b in cursor:
            amount = float(b.get("amount", 0))
            total += amount
            bills.append({
                "id": str(b["_id"]),
                "description": b.get("description", ""),
                "amount": amount,
                "due_date": str(b.get("next_expected_date", "")),
            })
        return UpcomingBillsWidget(
            total_due=round(total, 2),
            due_soon_count=len(bills),
            bills=bills,
        ) if bills else None

    async def _get_ai_insights(self, user_id: str) -> list[AIInsightItem]:
        cursor = self._db.financial_reports.find(
            {"user_id": to_object_id(user_id)}
        ).sort("generated_at", -1).limit(5)
        insights = []
        async for r in cursor:
            for ins in r.get("insights", []):
                if isinstance(ins, str):
                    insights.append(AIInsightItem(
                        id=str(r["_id"]),
                        title="Insight",
                        message=ins,
                        severity="info",
                        category="general",
                        created_at=str(r.get("generated_at", "")),
                    ))
                else:
                    insights.append(AIInsightItem(
                        id=str(r["_id"]),
                        title=ins.get("title", "Insight"),
                        message=ins.get("message", ""),
                        severity=ins.get("severity", "info"),
                        category=ins.get("category", "general"),
                        created_at=str(r.get("generated_at", "")),
                    ))
        return insights[:5]

    async def _get_budget_alerts(self, user_id: str) -> list[BudgetAlertItem]:
        cursor = self._db.budget_alerts.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).limit(10)
        alerts = []
        async for a in cursor:
            alerts.append(BudgetAlertItem(
                id=str(a["_id"]),
                category=a.get("category", ""),
                threshold=int(a.get("threshold", 0)),
                percentage=float(a.get("percentage", 0)),
                message=a.get("message", ""),
                read=a.get("read", False),
                created_at=str(a.get("created_at", "")),
            ))
        return alerts

    async def _get_spending_heatmap(self, user_id: str, start: datetime, end: datetime) -> list[SpendingHeatmapPoint]:
        cursor = self._db.expenses.find({
            "user_id": to_object_id(user_id),
            "date": {"$gte": start, "$lt": end},
        }).sort("date", -1).limit(50)
        points = []
        async for e in cursor:
            points.append(SpendingHeatmapPoint(
                day=str(e.get("date", "")),
                amount=float(e.get("amount", 0)),
                category=e.get("category", ""),
            ))
        return points

    async def _get_activity_feed(self, user_id: str) -> list[ActivityFeedItem]:
        items = []

        batches_cursor = self._db.processing_batches.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).limit(3)
        async for b in batches_cursor:
            items.append(ActivityFeedItem(
                id=str(b["_id"]),
                type="processing",
                title="Pipeline Run",
                description=f"Processed {b.get('processed', 0)} transactions",
                timestamp=str(b.get("created_at", "")),
                metadata={"batch_id": b.get("batch_id", ""), "status": b.get("status", "")},
            ))

        sync_cursor = self._db.sync_logs.find(
            {"user_id": to_object_id(user_id)}
        ).sort("started_at", -1).limit(3)
        async for s in sync_cursor:
            items.append(ActivityFeedItem(
                id=str(s["_id"]),
                type="sync",
                title="Data Sync",
                description=f"Imported {s.get('transactions_imported', 0)} transactions",
                timestamp=str(s.get("started_at", "")),
                metadata={"status": s.get("status", ""), "fetched": s.get("transactions_fetched", 0)},
            ))

        alert_cursor = self._db.budget_alerts.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).limit(3)
        async for a in alert_cursor:
            items.append(ActivityFeedItem(
                id=str(a["_id"]),
                type="alert",
                title="Budget Alert",
                description=a.get("message", ""),
                timestamp=str(a.get("created_at", "")),
                metadata={"category": a.get("category", ""), "threshold": a.get("threshold", 0)},
            ))

        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:10]


class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def get_notifications(self, user_id: str, limit: int = 50, offset: int = 0, unread_only: bool = False) -> list[NotificationItem]:
        query = {"user_id": to_object_id(user_id)}
        if unread_only:
            query["read"] = False
        cursor = self._db.notifications.find(query).sort("created_at", -1).skip(offset).limit(limit)
        items = []
        async for n in cursor:
            items.append(NotificationItem(
                id=str(n["_id"]),
                type=n.get("type", "general"),
                title=n.get("title", ""),
                message=n.get("message", ""),
                read=n.get("read", False),
                created_at=str(n.get("created_at", "")),
                metadata=n.get("metadata", {}),
            ))
        return items

    async def get_unread_count(self, user_id: str) -> int:
        return await self._db.notifications.count_documents(
            {"user_id": to_object_id(user_id), "read": False},
        )

    async def mark_read(self, notification_id: str, user_id: str) -> bool:
        result = await self._db.notifications.update_one(
            {"_id": to_object_id(notification_id), "user_id": to_object_id(user_id)},
            {"$set": {"read": True}},
        )
        return result.modified_count > 0

    async def mark_all_read(self, user_id: str) -> int:
        result = await self._db.notifications.update_many(
            {"user_id": to_object_id(user_id), "read": False},
            {"$set": {"read": True}},
        )
        return result.modified_count

    async def create_notification(self, user_id: str, ntype: str, title: str, message: str, metadata: dict | None = None) -> None:
        doc = {
            "user_id": to_object_id(user_id),
            "type": ntype,
            "title": title,
            "message": message,
            "read": False,
            "created_at": utc_now(),
            "metadata": metadata or {},
        }
        await self._db.notifications.insert_one(doc)


class WidgetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._dash_repo = MongoDashboardMetricsRepository(db)
        self._metrics_repo = MongoFinancialMetricsRepository(db)
        self._cf_repo = MongoCashFlowRepository(db)
        self._dash_svc = DashboardService(db)

    async def get_widget(self, user_id: str, widget_id: str, period: str) -> object:
        now = utc_now()
        dash = await self._dash_repo.get_by_user_and_period(user_id, period)

        if widget_id == "health_score":
            metrics = await self._metrics_repo.get_latest_by_user(user_id)
            if not metrics:
                return None
            return HealthScoreWidget(
                score=metrics.score, risk_level=metrics.risk_level,
                savings_rate=metrics.savings_rate, budget_adherence=metrics.budget_adherence,
                expense_stability=metrics.expense_stability, discretionary_ratio=metrics.discretionary_ratio,
                trend=metrics.trend, month_over_month_change=metrics.month_over_month_change,
            )

        if widget_id == "monthly_spending":
            if not dash:
                return None
            return SpendingWidget(
                total_spending=dash.total_spending, expense_count=dash.expense_count,
                top_category=dash.spending_by_category[0]["category"] if dash.spending_by_category else None,
                top_category_amount=dash.spending_by_category[0]["amount"] if dash.spending_by_category else 0,
                spending_by_category=dash.spending_by_category,
            )

        if widget_id == "cash_flow":
            cf = await self._cf_repo.get_by_user_and_month(user_id, now.year, now.month)
            if not cf:
                return None
            return CashFlowWidget(
                total_income=cf.total_income, total_expenses=cf.total_expenses,
                net_cash_flow=cf.net_cash_flow,
                expense_by_category=cf.expense_by_category,
                income_by_category=cf.income_by_category,
            )

        if widget_id == "budget_status":
            if not dash or not dash.budget_overview:
                return None
            on_track = sum(1 for b in dash.budget_overview if b.get("state") == "safe")
            warning = sum(1 for b in dash.budget_overview if b.get("state") == "warning")
            over = sum(1 for b in dash.budget_overview if b.get("state") == "over")
            return BudgetStatusWidget(
                budget_count=len(dash.budget_overview), on_track=on_track,
                warning=warning, over=over, budgets=dash.budget_overview,
            )

        if widget_id == "monthly_trend":
            if not dash:
                return None
            return [
                MonthlyTrendPoint(
                    month=t["month"], spending=t.get("spending", 0),
                    income=t.get("income", 0),
                    savings=round(t.get("income", 0) - t.get("spending", 0), 2),
                ) for t in dash.monthly_trend
            ]

        if widget_id == "recent_transactions":
            cursor = self._db.expenses.find(
                {"user_id": to_object_id(user_id)}
            ).sort("date", -1).limit(5)
            return [RecentTransactionItem(
                id=str(e["_id"]), description=e.get("description", ""),
                amount=float(e.get("amount", 0)), category=e.get("category", ""),
                date=str(e.get("date", "")), merchant=e.get("merchant"),
            ) async for e in cursor]

        if widget_id in ("recurring", "subscriptions", "upcoming_bills"):
            svc = self._dash_svc
            if widget_id == "recurring":
                return await svc._get_recurring_widget(user_id)
            if widget_id == "subscriptions":
                return await svc._get_subscription_widget(user_id)
            return await svc._get_upcoming_bills(user_id)

        if widget_id == "ai_insights":
            return await self._dash_svc._get_ai_insights(user_id)

        if widget_id == "budget_alerts":
            return await self._dash_svc._get_budget_alerts(user_id)

        if widget_id == "top_categories":
            if not dash:
                return None
            return [TopCategoryItem(**c) for c in dash.spending_by_category[:5]]

        if widget_id == "spending_heatmap":
            p_start, p_end = month_bounds(now.year, now.month)
            return await self._dash_svc._get_spending_heatmap(user_id, p_start, p_end)

        if widget_id == "activity":
            return await self._dash_svc._get_activity_feed(user_id)

        return None

    async def get_all_widgets(self, user_id: str, period: str) -> dict:
        widget_ids = [
            "health_score", "monthly_spending", "cash_flow", "budget_status",
            "monthly_trend", "recent_transactions", "recurring", "subscriptions",
            "upcoming_bills", "ai_insights", "budget_alerts", "top_categories",
        ]
        result = {}
        for wid in widget_ids:
            try:
                data = await self.get_widget(user_id, wid, period)
                if data is not None:
                    result[wid] = data
            except Exception as exc:
                logger.warning("widget_fetch_error user=%s widget=%s err=%s", user_id, wid, exc)
        return result


class DashboardGateway:
    def __init__(self):
        self._subscribed = False

    def subscribe_to_events(self):
        if self._subscribed:
            return
        self._subscribed = True
        event_types = [
            "processing.batch.completed", "dashboard.updated",
            "expense.created", "budget.updated", "cashflow.updated",
            "financial_metrics.updated", "notification.created",
            "budget_intelligence.updated", "budget_recommendation.generated",
            "budget_forecast.updated", "budget_risk.updated",
            "budget_opportunity.detected",
        ]
        for et in event_types:
            global_event_bus.subscribe(et, self._handle_event)
        logger.info("dashboard_gateway subscribed to %d event types", len(event_types))

    async def _handle_event(self, event: Event) -> None:
        payload = event.payload
        user_id = event.user_id
        ws_message = {
            "type": event.event_type,
            "data": payload,
            "timestamp": str(event.timestamp),
            "event_id": event.event_id,
        }
        try:
            await connection_manager.send_to_user(user_id, ws_message)
        except Exception as exc:
            logger.warning("ws_send_error user=%s event=%s err=%s", user_id, event.event_type, exc)
