import logging

from app.domain.financial_transactions.models import FinancialTransaction
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.utils.date_utils import utc_now

logger = logging.getLogger("intellimoney")


class SavingsService:
    def __init__(self, cash_flow_repo: MongoCashFlowRepository):
        self._cash_flow_repo = cash_flow_repo

    async def calculate_savings(
        self, user_id: str, transactions: list[FinancialTransaction],
    ) -> dict:
        now = utc_now()
        total_income = sum(tx.amount for tx in transactions if tx.transaction_type == "CREDIT")
        total_expenses = sum(
            tx.amount for tx in transactions
            if tx.transaction_type == "DEBIT" and not tx.is_refund and not tx.is_transfer
        )

        net_savings = round(total_income - total_expenses, 2)
        savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0.0
        savings_rate = max(min(savings_rate, 100), -100)

        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        previous = await self._cash_flow_repo.get_by_user_and_month(
            user_id, prev_year, prev_month,
        )

        previous_savings_rate = previous.savings_rate if previous else 0.0
        trend = "stable"
        if previous_savings_rate > 0:
            change = savings_rate - previous_savings_rate
            if change > 5:
                trend = "improving"
            elif change < -5:
                trend = "declining"

        return {
            "net_savings": net_savings,
            "savings_rate": savings_rate,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "trend": trend,
            "previous_savings_rate": previous_savings_rate,
        }
