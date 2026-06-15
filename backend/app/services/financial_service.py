from datetime import datetime
from statistics import mean, pstdev
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.analytics_service import get_month_expenses, get_summary
from app.services.budget_service import get_budget_status


def risk_level(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 45:
        return "Moderate"
    return "Needs Attention"


async def calculate_financial_score(
    db: AsyncIOMotorDatabase, user: dict[str, Any]
) -> dict[str, Any]:
    user_id = str(user["_id"])
    now = datetime.utcnow()
    summary = await get_summary(db, user)
    savings_rate = max(min(summary["savings_rate"], 100), -100)
    savings_component = max(min(savings_rate / 30 * 100, 100), 0)

    budget_statuses = await get_budget_status(db, user_id)
    if budget_statuses:
        adherence_values = [max(0, 100 - max(0, item["percentage_used"] - 100)) for item in budget_statuses]
        budget_adherence = mean(adherence_values)
    else:
        budget_adherence = 70

    monthly_totals = []
    for offset in range(5, -1, -1):
        month = now.month - offset
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        expenses = await get_month_expenses(db, user_id, year, month)
        monthly_totals.append(sum(item["amount"] for item in expenses))
    avg_spend = mean(monthly_totals) if monthly_totals else 0
    stability = 100
    if avg_spend > 0:
        stability = max(0, 100 - (pstdev(monthly_totals) / avg_spend * 100))

    current_expenses = await get_month_expenses(db, user_id, now.year, now.month)
    discretionary = sum(
        item["amount"]
        for item in current_expenses
        if item["category"] in {"Shopping", "Entertainment", "Travel"}
    )
    total_spending = summary["total_spending"] or 1
    category_risk = max(0, 100 - (discretionary / total_spending * 100))

    score = round(
        savings_component * 0.35
        + budget_adherence * 0.30
        + stability * 0.20
        + category_risk * 0.15
    )
    result = {
        "user_id": ObjectId(user_id),
        "score": int(max(0, min(score, 100))),
        "risk_level": risk_level(int(max(0, min(score, 100)))),
        "savings_rate": round(savings_rate, 2),
        "budget_adherence": round(budget_adherence, 2),
        "expense_stability": round(stability, 2),
        "calculated_at": now,
    }
    await db.financial_scores.insert_one(result.copy())
    result["calculated_at"] = now.isoformat()
    result.pop("user_id")
    return result
