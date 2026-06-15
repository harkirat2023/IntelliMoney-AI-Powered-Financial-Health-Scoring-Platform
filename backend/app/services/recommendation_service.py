from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.analytics_service import category_breakdown, get_summary
from app.services.budget_service import get_budget_status


async def generate_recommendations(
    db: AsyncIOMotorDatabase, user: dict[str, Any]
) -> list[dict[str, Any]]:
    user_id = str(user["_id"])
    recommendations: list[dict[str, Any]] = []
    summary = await get_summary(db, user)
    budgets = await get_budget_status(db, user_id)

    for budget in budgets:
        if budget["state"] == "over":
            recommendations.append(
                {
                    "title": f"{budget['category']} budget exceeded",
                    "message": f"You have spent Rs. {budget['spent']} against a Rs. {budget['limit']} limit.",
                    "severity": "high",
                    "category": budget["category"],
                    "suggested_action": "Pause non-essential purchases in this category until next month.",
                }
            )
        elif budget["state"] == "warning":
            recommendations.append(
                {
                    "title": f"{budget['category']} budget nearing limit",
                    "message": f"{budget['percentage_used']}% of this budget is already used.",
                    "severity": "medium",
                    "category": budget["category"],
                    "suggested_action": "Track upcoming expenses before adding new purchases.",
                }
            )

    if summary["monthly_income"] and summary["savings_rate"] < 20:
        recommendations.append(
            {
                "title": "Improve monthly savings rate",
                "message": f"Your current estimated savings rate is {summary['savings_rate']}%.",
                "severity": "medium",
                "category": "Savings",
                "suggested_action": "Aim for a 20-30% savings rate by setting stricter discretionary budgets.",
            }
        )

    breakdown = await category_breakdown(db, user_id)
    for item in breakdown:
        if item["label"] in {"Shopping", "Entertainment", "Travel"} and item["value"] > summary["total_spending"] * 0.35:
            recommendations.append(
                {
                    "title": f"High discretionary spending in {item['label']}",
                    "message": f"{item['label']} is taking a large share of your monthly expenses.",
                    "severity": "medium",
                    "category": item["label"],
                    "suggested_action": "Review recurring habits and move avoidable spends to a wishlist.",
                }
            )

    if not recommendations:
        recommendations.append(
            {
                "title": "Spending is under control",
                "message": "Your current budget and spending patterns look stable for this month.",
                "severity": "low",
                "category": "General",
                "suggested_action": "Keep tracking expenses regularly to maintain your financial health.",
            }
        )

    await db.recommendations.insert_one(
        {"user_id": user["_id"], "items": recommendations, "created_at": datetime.utcnow()}
    )
    return recommendations
