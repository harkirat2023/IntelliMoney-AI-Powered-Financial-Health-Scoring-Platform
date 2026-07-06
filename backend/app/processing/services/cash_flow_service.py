import logging
from collections import defaultdict

from app.domain.financial_transactions.models import FinancialTransaction

logger = logging.getLogger("intellimoney")
from app.processing.models.cash_flow_summary import CashFlowSummary
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.utils.date_utils import utc_now


class CashFlowService:
    def __init__(self, cash_flow_repo: MongoCashFlowRepository):
        self._cash_flow_repo = cash_flow_repo

    async def calculate_cash_flow(
        self, user_id: str, transactions: list[FinancialTransaction],
    ) -> CashFlowSummary:
        now = utc_now()
        month, year = now.month, now.year

        income_by_category: dict[str, float] = defaultdict(float)
        expense_by_category: dict[str, float] = defaultdict(float)

        for tx in transactions:
            if tx.transaction_type == "CREDIT":
                income_by_category[tx.assigned_category or "Other"] += tx.amount
            elif tx.transaction_type == "DEBIT" and not tx.is_refund and not tx.is_transfer:
                expense_by_category[tx.assigned_category or "Other"] += tx.amount

        total_income = round(sum(income_by_category.values()), 2)
        total_expenses = round(sum(expense_by_category.values()), 2)

        summary = CashFlowSummary(
            user_id=user_id,
            year=year,
            month=month,
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=round(total_income - total_expenses, 2),
            income_by_category=[
                {"category": c, "amount": round(a, 2)}
                for c, a in sorted(income_by_category.items(), key=lambda x: -x[1])
            ],
            expense_by_category=[
                {"category": c, "amount": round(a, 2)}
                for c, a in sorted(expense_by_category.items(), key=lambda x: -x[1])
            ],
            updated_at=now,
        )

        return await self._cash_flow_repo.upsert(summary)
