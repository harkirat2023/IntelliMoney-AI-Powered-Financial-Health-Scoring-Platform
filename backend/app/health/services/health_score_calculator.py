import logging
from statistics import mean, pstdev

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.health.models.financial_health import FinancialHealth
from app.health.repositories.financial_health_repository import MongoFinancialHealthRepository
from app.infrastructure.database.repositories.expense_repository import MongoExpenseRepository
from app.infrastructure.database.repositories.intelligence.financial_transaction_repository import (
    MongoFinancialTransactionRepository,
)
from app.processing.repositories.budget_usage_repository import MongoBudgetUsageRepository
from app.processing.repositories.cash_flow_repository import MongoCashFlowRepository
from app.utils.date_utils import month_bounds, utc_now

logger = logging.getLogger("intellimoney")

# Spec weights (normalized to sum 1.0). Raw spec: Savings 20, Debt 15, Budget 15,
# Emergency 10, Cash Flow 10, Goal 10, Expense Stability 10, Income 5, Investment 5, Trend 10.
SPEC_WEIGHTS = {
    "savings_rate": 0.1818,
    "debt_ratio": 0.1364,
    "budget_adherence": 0.1364,
    "emergency_fund": 0.0909,
    "cash_flow": 0.0909,
    "goal_completion": 0.0909,
    "expense_stability": 0.0909,
    "income_stability": 0.0455,
    "investment_habit": 0.0455,
    "financial_trend": 0.0909,
}

DEBT_KEYWORDS = ("loan", "emi", "interest", "finance", "mortgage", "credit card bill", "card dues", "hire purchase", "personal loan")
INVESTMENT_KEYWORDS = ("mutual fund", "sip", "fixed deposit", "fd ", "ppf", "shares", "stocks", "bond", "gold", "nps", "investment")
GOAL_STATUSES_ACTIVE = ("active", "on_track", "at_risk")


def risk_level_for_score(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 50:
        return "Average"
    if score >= 35:
        return "Poor"
    return "Critical"


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 45:
        return "C"
    return "D"


def factor_score(value: float, ideal: float, max_val: float = 100) -> float:
    return max(0, min(value / ideal * 100 if ideal else 0, max_val))


class HealthScoreCalculator:
    WEIGHTS = SPEC_WEIGHTS

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._expense_repo = MongoExpenseRepository(db)
        self._tx_repo = MongoFinancialTransactionRepository(db)
        self._budget_usage_repo = MongoBudgetUsageRepository(db)
        self._cf_repo = MongoCashFlowRepository(db)
        self._health_repo = MongoFinancialHealthRepository(db)

    def _clamp(self, value: float, min_v: float = 0, max_v: float = 100) -> float:
        return max(min_v, min(value, max_v))

    async def calculate(self, user_id: str) -> FinancialHealth:
        now = utc_now()
        period = f"{now.year}-{now.month:02d}"
        p_start, p_end = month_bounds(now.year, now.month)

        savings_rate_val = await self._calc_savings_rate(user_id, now)
        budget_adherence_val = await self._calc_budget_adherence(user_id, now)
        expense_stability_val = await self._calc_expense_stability(user_id, now)
        cash_flow_stability_val = await self._calc_cash_flow_stability(user_id, now)
        income_consistency_val = await self._calc_income_consistency(user_id, now)
        emergency_fund_val = await self._calc_emergency_fund(user_id, now)
        debt_ratio_val = await self._calc_debt_ratio(user_id, now)
        goal_completion_val = await self._calc_goal_completion(user_id)
        investment_habit_val = await self._calc_investment_habit(user_id, now)
        financial_trend_val = await self._calc_financial_trend(user_id, now)

        components = {
            "savings_rate": self._clamp(savings_rate_val),
            "debt_ratio": self._clamp(debt_ratio_val),
            "budget_adherence": self._clamp(budget_adherence_val),
            "emergency_fund": self._clamp(emergency_fund_val),
            "cash_flow": self._clamp(cash_flow_stability_val),
            "goal_completion": self._clamp(goal_completion_val),
            "expense_stability": self._clamp(expense_stability_val),
            "income_stability": self._clamp(income_consistency_val),
            "investment_habit": self._clamp(investment_habit_val),
            "financial_trend": self._clamp(financial_trend_val),
        }

        score = round(sum(components[k] * self.WEIGHTS[k] for k in self.WEIGHTS))
        score = int(self._clamp(score))

        logger.info(
            "health_calculated user=%s period=%s score=%d savings=%.1f debt=%.1f budget=%.1f emergency=%.1f cf=%.1f goal=%.1f stability=%.1f income=%.1f invest=%.1f trend=%.1f",
            user_id, period, score,
            components["savings_rate"], components["debt_ratio"],
            components["budget_adherence"], components["emergency_fund"],
            components["cash_flow"], components["goal_completion"],
            components["expense_stability"], components["income_stability"],
            components["investment_habit"], components["financial_trend"],
        )

        return FinancialHealth(
            user_id=user_id,
            period=period,
            score=score,
            risk_level=risk_level_for_score(score),
            grade=grade_for_score(score),
            savings_rate=round(savings_rate_val, 2),
            savings_component=round(components["savings_rate"], 2),
            budget_adherence=round(components["budget_adherence"], 2),
            expense_stability=round(components["expense_stability"], 2),
            cash_flow_stability=round(components["cash_flow"], 2),
            income_consistency=round(components["income_stability"], 2),
            emergency_fund_score=round(components["emergency_fund"], 2),
            recurring_expense_ratio=round(await self._calc_recurring_ratio(user_id, now), 4),
            essential_spending_ratio=round(await self._calc_essential_spending(user_id, p_start, p_end), 2),
            debt_ratio=round(components["debt_ratio"], 2),
            goal_completion=round(components["goal_completion"], 2),
            investment_habit=round(components["investment_habit"], 2),
            financial_trend=round(components["financial_trend"], 2),
            calculated_at=now,
        )

    async def _calc_savings_rate(self, user_id: str, now) -> float:
        cf = await self._cf_repo.get_by_user_and_month(user_id, now.year, now.month)
        if not cf or cf.total_income <= 0:
            return 0.0
        rate = (cf.net_cash_flow / cf.total_income) * 100
        return self._clamp(rate)

    async def _calc_budget_adherence(self, user_id: str, now) -> float:
        usages = await self._budget_usage_repo.get_by_user_and_period(user_id, now.month, now.year)
        if not usages:
            return 70.0
        scores = []
        for u in usages:
            if u.limit > 0:
                overage = max(0, u.percentage_used - 100)
                score = 100 - overage
                scores.append(self._clamp(score))
        return mean(scores) if scores else 70.0

    async def _calc_expense_stability(self, user_id: str, now) -> float:
        totals = []
        for offset in range(5, -1, -1):
            m = now.month - offset
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            start, end = month_bounds(y, m)
            expenses = await self._expense_repo.get_by_user(user_id, date_from=start, date_to=end)
            total = sum(e.amount for e in expenses)
            totals.append(total)
        avg = mean(totals) if totals else 0
        if avg <= 0:
            return 100.0
        std = pstdev(totals)
        cv = std / avg if avg > 0 else 0
        stability = max(0, 100 - (cv * 100))
        return self._clamp(stability)

    async def _calc_cash_flow_stability(self, user_id: str, now) -> float:
        summaries = await self._cf_repo.get_by_user(user_id, limit=6)
        if len(summaries) < 2:
            return 50.0
        positive_months = sum(1 for s in summaries if s.net_cash_flow >= 0)
        ratio = positive_months / len(summaries)
        return ratio * 100

    async def _calc_income_consistency(self, user_id: str, now) -> float:
        incomes = []
        for offset in range(5, -1, -1):
            m = now.month - offset
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            start, end = month_bounds(y, m)
            txs = await self._tx_repo.find_by_date_range(user_id, start, end)
            month_income = sum(
                abs(tx.amount) for tx in txs
                if tx.transaction_type == "CREDIT" and not getattr(tx, "is_refund", False)
            )
            incomes.append(month_income)
        avg = mean(incomes) if incomes else 0
        if avg <= 0:
            return 0.0
        std = pstdev(incomes)
        cv = std / avg if avg > 0 else 0
        return self._clamp(max(0, 100 - (cv * 120)))

    async def _calc_emergency_fund(self, user_id: str, now) -> float:
        cf = await self._cf_repo.get_by_user_and_month(user_id, now.year, now.month)
        cfs = await self._cf_repo.get_by_user(user_id, limit=3)
        avg_expenses = mean(s.total_expenses for s in cfs) if cfs else 0
        if avg_expenses <= 0 or not cf or cf.total_income <= 0:
            return 30.0
        savings_rate = cf.net_cash_flow / cf.total_income if cf.total_income > 0 else 0
        if savings_rate <= 0:
            return max(0, savings_rate * 100 + 20)
        months_to_3mo_emergency = (3 * avg_expenses) / (cf.net_cash_flow) if cf.net_cash_flow > 0 else 99
        if months_to_3mo_emergency <= 3:
            return self._clamp(80 + (3 - months_to_3mo_emergency) * 5)
        if months_to_3mo_emergency <= 6:
            return self._clamp(60 + (6 - months_to_3mo_emergency) * 6)
        if months_to_3mo_emergency <= 12:
            return self._clamp(40 + (12 - months_to_3mo_emergency) * 3)
        return max(20, 40 - (months_to_3mo_emergency - 12) * 2)

    async def _calc_recurring_ratio(self, user_id: str, now) -> float:
        p_start, p_end = month_bounds(now.year, now.month)
        expenses = await self._expense_repo.get_by_user(user_id, date_from=p_start, date_to=p_end)
        total = sum(e.amount for e in expenses) or 1
        recurring_total = 0.0
        recurring = self._db.recurring_expenses.find({
            "user_id": user_id, "is_active": True,
        })
        async for r in recurring:
            amount = float(r.get("amount", 0))
            freq = r.get("frequency", "monthly")
            recurring_total += amount if freq == "monthly" else amount * (52 if freq == "weekly" else 26 if freq == "biweekly" else 1)
        return self._clamp(recurring_total / total, max_v=1)

    async def _calc_essential_spending(self, user_id: str, start, end) -> float:
        expenses = await self._expense_repo.get_by_user(user_id, date_from=start, date_to=end)
        total = sum(e.amount for e in expenses) or 1
        essential_categories = {"Bills", "Rent", "Food", "Health", "Transport", "Education"}
        essential = sum(e.amount for e in expenses if e.category in essential_categories)
        return (essential / total) * 100

    async def _calc_debt_ratio(self, user_id: str, now) -> float:
        debt_totals = []
        income_totals = []
        for offset in range(2, -1, -1):
            m = now.month - offset
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            start, end = month_bounds(y, m)
            txs = await self._tx_repo.find_by_date_range(user_id, start, end)
            debt = sum(
                tx.amount for tx in txs
                if tx.transaction_type == "DEBIT"
                and any(kw in (tx.original_description or "").lower() for kw in DEBT_KEYWORDS)
            )
            debt_totals.append(debt)
            income_totals.append(sum(
                abs(tx.amount) for tx in txs
                if tx.transaction_type == "CREDIT" and not getattr(tx, "is_refund", False)
            ))
        avg_income = mean(income_totals) if income_totals else 0
        if avg_income <= 0:
            return 50.0
        avg_debt = mean(debt_totals)
        dti = avg_debt / avg_income
        if dti <= 0:
            return 100.0
        score = max(0, 100 - dti * 180)
        return self._clamp(score)

    async def _calc_goal_completion(self, user_id: str) -> float:
        completions = []
        cursor = self._db.financial_goals.find({
            "user_id": user_id, "status": {"$in": list(GOAL_STATUSES_ACTIVE)},
        })
        async for g in cursor:
            target = float(g.get("target_amount", 0)) or 1
            current = float(g.get("current_amount", 0))
            completions.append(max(0, min(current / target * 100, 100)))
        if not completions:
            return 50.0
        return self._clamp(mean(completions))

    async def _calc_investment_habit(self, user_id: str, now) -> float:
        invested = []
        incomes = []
        for offset in range(5, -1, -1):
            m = now.month - offset
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            start, end = month_bounds(y, m)
            txs = await self._tx_repo.find_by_date_range(user_id, start, end)
            month_invested = sum(
                tx.amount for tx in txs
                if tx.transaction_type == "DEBIT"
                and (
                    tx.assigned_category == "Investment"
                    or any(kw in (tx.original_description or "").lower() for kw in INVESTMENT_KEYWORDS)
                )
            )
            invested.append(month_invested)
            incomes.append(sum(
                abs(tx.amount) for tx in txs
                if tx.transaction_type == "CREDIT" and not getattr(tx, "is_refund", False)
            ))
        avg_income = mean(incomes) if incomes else 0
        if avg_income <= 0:
            return 40.0
        avg_invested = mean(invested)
        rate = avg_invested / avg_income
        return self._clamp(rate / 0.15 * 100)

    async def _calc_financial_trend(self, user_id: str, now) -> float:
        cursor = self._db.financial_health_history.find(
            {"user_id": user_id},
        ).sort("calculated_at", -1).limit(6)
        scores = [int(doc.get("score", 50)) async for doc in cursor]
        if len(scores) < 2:
            return 50.0
        scores = list(reversed(scores))
        change = scores[-1] - scores[0]
        return self._clamp(50 + change * 6)
