import json
from datetime import datetime
from typing import Any

from langchain_core.tools import tool
from motor.motor_asyncio import AsyncIOMotorDatabase


def _make_tool(db_fn):
    """Decorator to inject db dependency into tool functions."""
    return db_fn


def _serialize(doc: Any) -> Any:
    if isinstance(doc, dict):
        return {k: _serialize(v) for k, v in doc.items() if k != "_id"}
    if isinstance(doc, list):
        return [_serialize(i) for i in doc]
    if isinstance(doc, datetime):
        return doc.isoformat()
    if hasattr(doc, "__str__"):
        return str(doc)
    return doc


def _safe_readable(data: Any) -> str:
    cleaned = _serialize(data)
    return json.dumps(cleaned, default=str, indent=2)


class ToolRegistry:
    def __init__(self, db: AsyncIOMotorDatabase, user_id: str):
        self._db = db
        self._user_id = user_id

    async def _financial_health(self, _query: str = "") -> str:
        """Get the user's current financial health score, risk level, and factor breakdown. Use this when asked about health score, financial health, or overall financial wellness."""
        doc = await self._db.financial_health.find_one(
            {"user_id": self._user_id}, sort=[("calculated_at", -1)]
        )
        if not doc:
            return "No financial health data found. Run a health calculation first."
        return _safe_readable(doc)

    async def _budget_intelligence(self, _query: str = "") -> str:
        """Get budget intelligence data including budget score, category breakdown, overspending, and potential savings. Use for budget-related questions."""
        doc = await self._db.budget_intelligence.find_one(
            {"user_id": self._user_id}, sort=[("calculated_at", -1)]
        )
        if not doc:
            return "No budget intelligence data found. Run budget intelligence generation first."
        return _safe_readable(doc)

    async def _expenses(self, period: str = "") -> str:
        """Get expense data. Provide a period like '2026-07' or leave empty for current month. Use for spending questions."""
        if not period:
            now = datetime.utcnow()
            period = f"{now.year}-{now.month:02d}"
        pipeline = [
            {"$match": {"user_id": self._user_id, "transaction_type": "DEBIT"}},
            {"$group": {"_id": "$assigned_category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
            {"$sort": {"total": -1}},
        ]
        results = await self._db.financial_transactions.aggregate(pipeline).to_list(length=None)
        if not results:
            return "No expense data found."
        return _safe_readable({"period": period, "categories": results})

    async def _cash_flow(self, _query: str = "") -> str:
        """Get cash flow summary including income, expenses, net savings, and savings rate. Use for income, savings, or cash flow questions."""
        doc = await self._db.cash_flow_summary.find_one(
            {"user_id": self._user_id}, sort=[("calculated_at", -1)]
        )
        if not doc:
            return "No cash flow data found."
        return _safe_readable(doc)

    async def _dashboard_metrics(self, _query: str = "") -> str:
        """Get overall dashboard metrics including total spending, income, savings rate, and top merchants. Use for overview questions."""
        doc = await self._db.dashboard_metrics.find_one(
            {"user_id": self._user_id}, sort=[("updated_at", -1)]
        )
        if not doc:
            return "No dashboard metrics found."
        return _safe_readable(doc)

    async def _search_transactions(self, query: str = "") -> str:
        """Search financial transactions by keyword, category, or merchant name. Provide a search term. Use for specific transaction lookups."""
        if not query:
            return "Please provide a search term."
        regex = {"$regex": query, "$options": "i"}
        docs = await self._db.financial_transactions.find(
            {"user_id": self._user_id, "$or": [
                {"original_description": regex}, {"assigned_category": regex},
                {"normalized_merchant": regex}, {"cleaned_merchant": regex},
            ]}
        ).sort("transaction_date", -1).limit(10).to_list(length=10)
        if not docs:
            return f"No transactions found matching '{query}'."
        return _safe_readable(docs)

    async def _category_breakdown(self, _query: str = "") -> str:
        """Get spending broken down by category with totals and percentage. Use for 'where is my money going' questions."""
        pipeline = [
            {"$match": {"user_id": self._user_id, "transaction_type": "DEBIT"}},
            {"$group": {"_id": "$assigned_category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
            {"$sort": {"total": -1}},
        ]
        results = await self._db.financial_transactions.aggregate(pipeline).to_list(length=None)
        total = sum(r["total"] for r in results) if results else 0
        categories = []
        for r in results:
            pct = round(r["total"] / total * 100, 1) if total > 0 else 0
            categories.append({"category": r["_id"], "total": round(r["total"], 2),
                               "count": r["count"], "percentage": pct})
        return _safe_readable({"total_spending": round(total, 2), "categories": categories})

    async def _subscriptions(self, _query: str = "") -> str:
        """Get all subscriptions including active and inactive ones. Use for subscription management questions."""
        docs = await self._db.subscriptions.find({"user_id": self._user_id}).to_list(length=None)
        if not docs:
            return "No subscriptions found."
        return _safe_readable(docs)

    async def _recurring_expenses(self, _query: str = "") -> str:
        """Get all recurring expenses. Use for recurring payment or monthly committed spending questions."""
        docs = await self._db.recurring_expenses.find({"user_id": self._user_id}).to_list(length=None)
        if not docs:
            return "No recurring expenses found."
        return _safe_readable(docs)

    async def _monthly_report(self, period: str = "") -> str:
        """Generate a monthly financial report. Provide a period like '2026-07' or leave empty for current month. Use for 'summarize my month' questions."""
        if not period:
            now = datetime.utcnow()
            period = f"{now.year}-{now.month:02d}"
        health = await self._db.financial_health.find_one(
            {"user_id": self._user_id, "period": period}
        )
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": self._user_id, "period": period}
        )
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": self._user_id}
        )
        return _safe_readable({
            "period": period,
            "health_score": health["score"] if health else None,
            "budget_score": budget["budget_score"] if budget else None,
            "cash_flow": {
                "income": cash.get("total_income", 0) if cash else 0,
                "expenses": cash.get("total_expenses", 0) if cash else 0,
                "net_savings": cash.get("net_savings", 0) if cash else 0,
            } if cash else None,
            "budget_categories": budget.get("categories", []) if budget else [],
        })

    async def _recommendations(self, _query: str = "") -> str:
        """Get financial health recommendations and budget recommendations. Use for advice or suggestion questions."""
        health_recs = await self._db.health_recommendations.find(
            {"user_id": self._user_id, "dismissed": False}
        ).sort("priority", 1).to_list(length=10)
        budget_recs = await self._db.budget_recommendations.find(
            {"user_id": self._user_id, "dismissed": False}
        ).sort("priority", 1).to_list(length=10)
        return _safe_readable({
            "health_recommendations": health_recs,
            "budget_recommendations": budget_recs,
        })

    def get_tools(self) -> list:
        return [
            self._financial_health, self._budget_intelligence, self._expenses,
            self._cash_flow, self._dashboard_metrics, self._search_transactions,
            self._category_breakdown, self._subscriptions, self._recurring_expenses,
            self._monthly_report, self._recommendations,
        ]
