import logging

from app.health.models.financial_health import FinancialHealth
from app.health.models.health_recommendation import HealthRecommendation
from app.health.repositories.recommendation_repository import (
    MongoRecommendationRepository,
)
from app.utils.date_utils import utc_now

logger = logging.getLogger("intellimoney")


class RecommendationEngine:
    def __init__(self, rec_repo: MongoRecommendationRepository):
        self._rec_repo = rec_repo

    async def generate(self, user_id: str, health: FinancialHealth) -> list[HealthRecommendation]:
        now = utc_now()
        recs: list[HealthRecommendation] = []

        if health.savings_component < 30:
            recs.append(HealthRecommendation(
                user_id=user_id, category="savings", priority="high",
                title="Increase your savings rate",
                message=f"Your savings rate ({health.savings_rate:.1f}%) is well below the recommended 20%. Consider reducing discretionary spending or increasing income.",
                metric="savings_rate", current_value=health.savings_rate, target_value=20,
                impact="high", action="Set up an auto-transfer of 20% of income to savings at the start of each month.",
                created_at=now,
            ))
        elif health.savings_component < 60:
            recs.append(HealthRecommendation(
                user_id=user_id, category="savings", priority="medium",
                title="Boost your savings buffer",
                message=f"Your savings rate of {health.savings_rate:.1f}% is decent. Pushing towards 25%+ would accelerate your emergency fund growth.",
                metric="savings_rate", current_value=health.savings_rate, target_value=25,
                impact="medium", action="Review subscriptions and dining-out frequency to find an extra 5% to save.",
                created_at=now,
            ))

        if health.budget_adherence < 50:
            recs.append(HealthRecommendation(
                user_id=user_id, category="budget", priority="high",
                title="Budget adherence needs improvement",
                message=f"Your budget adherence score is {health.budget_adherence:.1f}%. Most budgets are being exceeded.",
                metric="budget_adherence", current_value=health.budget_adherence, target_value=80,
                impact="high", action="Review each budget category and set realistic limits. Use the Budget Optimizer for AI-powered suggestions.",
                created_at=now,
            ))

        if health.expense_stability < 40:
            recs.append(HealthRecommendation(
                user_id=user_id, category="expense_stability", priority="medium",
                title="Expense pattern is highly variable",
                message=f"Your expense stability score is {health.expense_stability:.1f}. Large month-to-month swings make planning difficult.",
                metric="expense_stability", current_value=health.expense_stability, target_value=70,
                impact="medium", action="Identify irregular large expenses and build a sinking fund for predictable big-ticket items.",
                created_at=now,
            ))

        if health.cash_flow_stability < 40:
            recs.append(HealthRecommendation(
                user_id=user_id, category="cashflow", priority="high",
                title="Cash flow is frequently negative",
                message=f"Your cash flow is positive only {health.cash_flow_stability:.0f}% of months. Negative cash flow months deplete savings.",
                metric="cash_flow_stability", current_value=health.cash_flow_stability, target_value=80,
                impact="high", action="Build a 1-month buffer in your current account to absorb negative cash flow months without stress.",
                created_at=now,
            ))

        if health.emergency_fund_score < 40:
            recs.append(HealthRecommendation(
                user_id=user_id, category="emergency", priority="high",
                title="Emergency fund needs attention",
                message=f"Your emergency fund readiness is {health.emergency_fund_score:.0f}/100. Aim for 3-6 months of essential expenses saved.",
                metric="emergency_fund_score", current_value=health.emergency_fund_score, target_value=80,
                impact="high", action="Set a monthly savings goal equal to one essential expense until you reach 3 months of coverage.",
                created_at=now,
            ))

        if health.recurring_expense_ratio > 0.50:
            recs.append(HealthRecommendation(
                user_id=user_id, category="recurring", priority="medium",
                title="Recurring expenses are high",
                message=f"Recurring expenses make up {health.recurring_expense_ratio * 100:.0f}% of total spending. Review subscriptions and memberships.",
                metric="recurring_expense_ratio", current_value=health.recurring_expense_ratio * 100, target_value=30,
                impact="medium", action="Audit all subscriptions and cancel unused ones. Look for annual plans that offer discounts.",
                created_at=now,
            ))

        if health.essential_spending_ratio < 30:
            recs.append(HealthRecommendation(
                user_id=user_id, category="spending", priority="medium",
                title="High discretionary spending ratio",
                message=f"Essential spending is only {health.essential_spending_ratio:.0f}% of your total. Non-essential spending may be crowding out savings.",
                metric="essential_spending_ratio", current_value=health.essential_spending_ratio, target_value=50,
                impact="medium", action="Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
                created_at=now,
            ))

        if health.debt_ratio < 50:
            recs.append(HealthRecommendation(
                user_id=user_id, category="debt", priority="high",
                title="Debt burden is high",
                message=f"Your debt-to-income score is {health.debt_ratio:.0f}/100. Loan and EMI payments are consuming a large share of income.",
                metric="debt_ratio", current_value=health.debt_ratio, target_value=80,
                impact="high", action="Prioritise high-interest debt repayment. Consider debt consolidation or an EMI pause before adding new credit.",
                created_at=now,
            ))

        if health.goal_completion < 30:
            recs.append(HealthRecommendation(
                user_id=user_id, category="goals", priority="medium",
                title="Goals are barely funded",
                message=f"Your active goal completion is {health.goal_completion:.0f}%. Savings targets are far from current balances.",
                metric="goal_completion", current_value=health.goal_completion, target_value=60,
                impact="medium", action="Break goals into monthly milestone targets and set up automatic transfers towards them.",
                created_at=now,
            ))

        if health.investment_habit < 30:
            recs.append(HealthRecommendation(
                user_id=user_id, category="investment", priority="low",
                title="Start building an investment habit",
                message=f"Your investment habit score is {health.investment_habit:.0f}/100. A healthy target is ~15% of income invested monthly.",
                metric="investment_habit", current_value=health.investment_habit, target_value=80,
                impact="medium", action="Start a small monthly SIP in an index fund and increase it by 1% each quarter.",
                created_at=now,
            ))

        if health.financial_trend < 40:
            recs.append(HealthRecommendation(
                user_id=user_id, category="trend", priority="medium",
                title="Financial health is trending down",
                message=f"Your financial trend score is {health.financial_trend:.0f}/100. Recent periods are weaker than earlier ones.",
                metric="financial_trend", current_value=health.financial_trend, target_value=60,
                impact="medium", action="Diagnose the last few months' spending spikes and correct course before the trend worsens.",
                created_at=now,
            ))

        if health.score >= 80:
            recs.append(HealthRecommendation(
                user_id=user_id, category="general", priority="low",
                title="Excellent financial health",
                message=f"Your score of {health.score}/100 places you in the {health.risk_level} category. Keep up the great habits!",
                metric="score", current_value=health.score, target_value=95,
                impact="low", action="Consider exploring investment options to grow your wealth beyond savings.",
                created_at=now,
            ))

        saved = []
        for rec in recs:
            saved.append(await self._rec_repo.create(rec))

        old = await self._rec_repo.delete_old(user_id)
        if old:
            logger.info("recommendation_cleanup user=%s removed=%d", user_id, old)

        logger.info("recommendations_generated user=%s period=%s count=%d", user_id, health.period, len(saved))
        return saved
