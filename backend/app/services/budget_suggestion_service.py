from collections import defaultdict
from datetime import date as Date
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.documents import BudgetSuggestionDocument
from app.schemas.budget_suggestion import BudgetOptimizationReport, BudgetSuggestion
from app.services.serializers import serialize_document, utc_now


async def calculate_monthly_spending(db: AsyncIOMotorDatabase, user_id: str, months: int = 3) -> dict[str, list[float]]:
    """Calculate monthly spending per category over the last N months."""
    start_date = datetime.now() - timedelta(days=months * 30)
    
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": start_date}
        })
    ]
    
    monthly_spending: dict[str, list[float]] = defaultdict(list)
    for expense in expenses:
        monthly_spending[expense["category"]].append(expense["amount"])
    
    return monthly_spending


def calculate_suggested_limit(
    avg_spending: float,
    max_spending: float,
    min_spending: float,
    current_limit: float,
    months_analyzed: int
) -> tuple[float, str, float]:
    """
    Calculate suggested budget limit based on spending patterns.
    Returns (suggested_limit, reason, confidence)
    """
    # Calculate confidence based on consistency
    if max_spending == 0 or min_spending == 0:
        confidence = 0.5
    else:
        variance_ratio = (max_spending - min_spending) / max_spending
        confidence = max(0.5, min(0.95, 1.0 - variance_ratio))
    
    # Smart suggestion logic
    if avg_spending > current_limit * 1.2:
        # User is consistently overspending - suggest higher limit
        suggested = avg_spending * 1.15  # 15% buffer
        reason = f"You're consistently overspending by {((avg_spending / current_limit - 1) * 100):.0f}%. Consider increasing your budget."
    elif avg_spending < current_limit * 0.7:
        # User is consistently under budget - suggest lower limit
        suggested = avg_spending * 1.2  # 20% buffer
        reason = f"You're consistently under budget by {((1 - avg_spending / current_limit) * 100):.0f}%. You could reduce this budget and allocate funds elsewhere."
    elif avg_spending > current_limit:
        # Slightly overspending
        suggested = avg_spending * 1.1  # 10% buffer
        reason = "You're slightly over budget. A small increase could help you stay within limits."
    else:
        # Within budget - fine-tune
        suggested = avg_spending * 1.15  # 15% buffer for flexibility
        reason = "Your current budget is reasonable. This suggestion adds a small buffer for unexpected expenses."
    
    # Round to nearest 100
    suggested = round(suggested / 100) * 100
    
    # Ensure minimum budget of ₹500
    suggested = max(500, suggested)
    
    return suggested, reason, round(confidence, 2)


async def generate_budget_suggestions(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Generate smart budget suggestions based on spending history."""
    # Get current budgets
    now = utc_now()
    current_budgets = [
        serialize_document(item)
        async for item in db.budgets.find({
            "user_id": ObjectId(user_id),
            "month": now.month,
            "year": now.year
        })
    ]
    
    if not current_budgets:
        return []
    
    # Get spending history
    monthly_spending = await calculate_monthly_spending(db, user_id, months=3)
    
    suggestions = []
    for budget in current_budgets:
        category = budget["category"]
        current_limit = float(budget["limit"])
        
        # Get spending data for this category
        amounts = monthly_spending.get(category, [])
        if not amounts:
            continue
        
        # Calculate statistics
        avg_spending = sum(amounts) / len(amounts)
        max_spending = max(amounts)
        min_spending = min(amounts)
        months_analyzed = len(amounts)
        
        # Calculate suggested limit
        suggested_limit, reason, confidence = calculate_suggested_limit(
            avg_spending, max_spending, min_spending, current_limit, months_analyzed
        )
        
        # Skip if suggestion is very close to current limit
        if abs(suggested_limit - current_limit) < current_limit * 0.1:
            continue
        
        # Check if suggestion already exists
        existing = await db.budget_suggestions.find_one({
            "user_id": ObjectId(user_id),
            "category": category,
            "is_applied": False
        })
        
        if existing:
            # Update existing suggestion
            await db.budget_suggestions.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "suggested_limit": suggested_limit,
                    "average_spending": round(avg_spending, 2),
                    "max_spending": round(max_spending, 2),
                    "min_spending": round(min_spending, 2),
                    "confidence": confidence,
                    "reason": reason,
                    "months_analyzed": months_analyzed,
                    "created_at": utc_now()
                }}
            )
            suggestions.append({**existing, "suggested_limit": suggested_limit})
        else:
            # Create new suggestion
            suggestion_doc: BudgetSuggestionDocument = {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "category": category,
                "current_limit": current_limit,
                "suggested_limit": suggested_limit,
                "average_spending": round(avg_spending, 2),
                "max_spending": round(max_spending, 2),
                "min_spending": round(min_spending, 2),
                "confidence": confidence,
                "reason": reason,
                "months_analyzed": months_analyzed,
                "is_applied": False,
                "created_at": utc_now(),
            }
            await db.budget_suggestions.insert_one(suggestion_doc)
            suggestions.append(serialize_document(suggestion_doc))
    
    # Sort by confidence and potential impact
    suggestions.sort(key=lambda x: (x["confidence"], abs(x["suggested_limit"] - x["current_limit"])), reverse=True)
    return suggestions


async def get_budget_suggestions(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Get all pending budget suggestions for a user."""
    cursor = db.budget_suggestions.find({
        "user_id": ObjectId(user_id),
        "is_applied": False
    }).sort("created_at", -1)
    return [serialize_document(item) async for item in cursor]


async def apply_budget_suggestion(db: AsyncIOMotorDatabase, user_id: str, suggestion_id: str) -> dict[str, Any] | None:
    """Apply a budget suggestion by updating the actual budget."""
    if not ObjectId.is_valid(suggestion_id):
        return None
    
    # Get the suggestion
    suggestion = await db.budget_suggestions.find_one({
        "_id": ObjectId(suggestion_id),
        "user_id": ObjectId(user_id),
        "is_applied": False
    })
    
    if not suggestion:
        return None
    
    # Update the budget
    now = utc_now()
    result = await db.budgets.update_one(
        {
            "user_id": ObjectId(user_id),
            "category": suggestion["category"],
            "month": now.month,
            "year": now.year
        },
        {"$set": {"limit": suggestion["suggested_limit"]}}
    )
    
    if result.modified_count > 0:
        # Mark suggestion as applied
        await db.budget_suggestions.update_one(
            {"_id": ObjectId(suggestion_id)},
            {"$set": {"is_applied": True}}
        )
        return serialize_document(suggestion)
    
    return None


async def dismiss_budget_suggestion(db: AsyncIOMotorDatabase, user_id: str, suggestion_id: str) -> bool:
    """Dismiss a budget suggestion."""
    if not ObjectId.is_valid(suggestion_id):
        return False
    
    result = await db.budget_suggestions.delete_one({
        "_id": ObjectId(suggestion_id),
        "user_id": ObjectId(user_id)
    })
    return result.deleted_count > 0


async def generate_optimization_report(db: AsyncIOMotorDatabase, user_id: str) -> BudgetOptimizationReport:
    """Generate a comprehensive budget optimization report."""
    suggestions = await get_budget_suggestions(db, user_id)
    
    # Calculate totals
    total_budget = sum(s["current_limit"] for s in suggestions)
    total_suggested = sum(s["suggested_limit"] for s in suggestions)
    potential_savings = total_budget - total_suggested
    
    # Generate insights
    insights = []
    
    if potential_savings > 0:
        insights.append(f"💰 You could save ₹{potential_savings:,.2f} per month by optimizing your budgets")
    elif potential_savings < 0:
        insights.append(f"⚠️ You may need to increase your total budget by ₹{abs(potential_savings):,.2f} to match your spending patterns")
    
    # Category-specific insights
    for suggestion in suggestions[:3]:  # Top 3 suggestions
        change_pct = ((suggestion["suggested_limit"] - suggestion["current_limit"]) / suggestion["current_limit"]) * 100
        if change_pct < -10:
            insights.append(f"📉 {suggestion['category']}: Reduce by {abs(change_pct):.0f}% (₹{suggestion['current_limit']:,.0f} → ₹{suggestion['suggested_limit']:,.0f})")
        elif change_pct > 10:
            insights.append(f"📈 {suggestion['category']}: Increase by {change_pct:.0f}% (₹{suggestion['current_limit']:,.0f} → ₹{suggestion['suggested_limit']:,.0f})")
    
    if not insights:
        insights.append("✅ Your budgets are well-optimized based on your spending patterns")
    
    return BudgetOptimizationReport(
        total_budget=round(total_budget, 2),
        total_suggested=round(total_suggested, 2),
        potential_savings=round(potential_savings, 2),
        categories_analyzed=len(suggestions),
        suggestions=[
            {
                "id": s["id"],
                "category": s["category"],
                "current_limit": s["current_limit"],
                "suggested_limit": s["suggested_limit"],
                "change": round(s["suggested_limit"] - s["current_limit"], 2),
                "change_percentage": round(((s["suggested_limit"] - s["current_limit"]) / s["current_limit"]) * 100, 1),
                "confidence": s["confidence"],
                "reason": s["reason"],
                "average_spending": s["average_spending"]
            }
            for s in suggestions
        ],
        insights=insights,
        generated_at=utc_now()
    )