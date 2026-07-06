from collections import defaultdict
from datetime import date as Date
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.documents import SubscriptionDocument
from app.schemas.subscription import SubscriptionInsights, SubscriptionSuggestion
from app.services.serializers import serialize_document, utc_now
from app.utils.frequency import _calculate_next_date, _detect_frequency


async def create_subscription(
    db: AsyncIOMotorDatabase,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Create a new subscription."""
    now = utc_now()
    start_date = payload["start_date"]
    if isinstance(start_date, str):
        start_date = Date.fromisoformat(start_date)
    
    next_payment = _calculate_next_date(start_date, payload["frequency"])
    
    document: SubscriptionDocument = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "description": payload["description"],
        "amount": float(payload["amount"]),
        "category": payload.get("category", "Entertainment"),
        "frequency": payload["frequency"],
        "start_date": datetime.combine(start_date, datetime.min.time()),
        "end_date": datetime.combine(payload["end_date"], datetime.min.time()) if payload.get("end_date") else None,
        "is_active": payload.get("is_active", True),
        "last_payment_date": None,
        "next_payment_date": datetime.combine(next_payment, datetime.min.time()) if next_payment else None,
        "total_spent": 0.0,
        "payment_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    await db.subscriptions.insert_one(document)
    return serialize_document(document)


async def get_subscriptions(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Get all subscriptions for a user."""
    cursor = db.subscriptions.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
    return [serialize_document(item) async for item in cursor]


async def get_subscription(db: AsyncIOMotorDatabase, user_id: str, subscription_id: str) -> dict[str, Any] | None:
    """Get a specific subscription."""
    if not ObjectId.is_valid(subscription_id):
        return None
    item = await db.subscriptions.find_one({
        "_id": ObjectId(subscription_id),
        "user_id": ObjectId(user_id),
    })
    return serialize_document(item) if item else None


async def update_subscription(
    db: AsyncIOMotorDatabase,
    user_id: str,
    subscription_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Update a subscription."""
    if not ObjectId.is_valid(subscription_id):
        return None
    
    update_fields: dict[str, Any] = {"updated_at": utc_now()}
    
    if "description" in payload:
        update_fields["description"] = payload["description"]
    if "amount" in payload:
        update_fields["amount"] = float(payload["amount"])
    if "category" in payload:
        update_fields["category"] = payload["category"]
    if "frequency" in payload:
        update_fields["frequency"] = payload["frequency"]
    if "start_date" in payload:
        start_date = payload["start_date"]
        if isinstance(start_date, str):
            start_date = Date.fromisoformat(start_date)
        update_fields["start_date"] = datetime.combine(start_date, datetime.min.time())
        update_fields["next_payment_date"] = datetime.combine(
            _calculate_next_date(start_date, payload.get("frequency", "monthly")),
            datetime.min.time()
        )
    if "end_date" in payload:
        update_fields["end_date"] = datetime.combine(payload["end_date"], datetime.min.time()) if payload["end_date"] else None
    if "is_active" in payload:
        update_fields["is_active"] = payload["is_active"]
    
    await db.subscriptions.update_one(
        {"_id": ObjectId(subscription_id), "user_id": ObjectId(user_id)},
        {"$set": update_fields},
    )
    return await get_subscription(db, user_id, subscription_id)


async def delete_subscription(db: AsyncIOMotorDatabase, user_id: str, subscription_id: str) -> bool:
    """Delete a subscription."""
    if not ObjectId.is_valid(subscription_id):
        return False
    result = await db.subscriptions.delete_one({
        "_id": ObjectId(subscription_id),
        "user_id": ObjectId(user_id),
    })
    return result.deleted_count > 0


async def detect_subscriptions(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Detect potential subscriptions from expense history."""
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({"user_id": ObjectId(user_id)}).sort("date", 1)
    ]
    
    if len(expenses) < 2:
        return []
    
    # Group by description
    description_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for expense in expenses:
        normalized = expense["description"].lower().strip()
        description_groups[normalized].append(expense)
    
    suggestions = []
    for description, group in description_groups.items():
        if len(group) < 2:
            continue
        
        # Check for consistent amounts
        amounts = [e["amount"] for e in group]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = all(abs(a - avg_amount) / avg_amount < 0.1 for a in amounts)
        
        if not amount_variance:
            continue
        
        # Check for recurring pattern
        dates = [e["date"].date() if isinstance(e["date"], datetime) else e["date"] for e in group]
        dates.sort()
        
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        frequency = _detect_frequency(avg_interval)
        
        if not frequency:
            continue
        
        # Calculate total spent
        total_spent = sum(amounts)
        
        # Calculate confidence
        confidence = min(0.95, 0.5 + (len(group) * 0.1))
        
        suggestions.append({
            "description": group[0]["description"],
            "amount": round(avg_amount, 2),
            "category": group[0]["category"],
            "frequency": frequency,
            "confidence": round(confidence, 2),
            "occurrences_detected": len(group),
            "suggested_start_date": dates[0],
            "total_spent": round(total_spent, 2),
        })
    
    suggestions.sort(key=lambda x: (x["confidence"], x["occurrences_detected"]), reverse=True)
    return suggestions[:10]


async def get_subscription_insights(db: AsyncIOMotorDatabase, user_id: str) -> SubscriptionInsights:
    """Get insights about user's subscriptions."""
    subscriptions = await get_subscriptions(db, user_id)
    active_subs = [s for s in subscriptions if s["is_active"]]
    
    # Calculate costs
    monthly_cost = 0
    yearly_cost = 0
    by_category: dict[str, float] = defaultdict(float)
    top_expenses = []
    
    for sub in active_subs:
        amount = sub["amount"]
        frequency = sub["frequency"]
        
        # Convert to monthly cost
        if frequency == "weekly":
            monthly_cost += amount * 4.33
            yearly_cost += amount * 52
        elif frequency == "biweekly":
            monthly_cost += amount * 2.17
            yearly_cost += amount * 26
        elif frequency == "monthly":
            monthly_cost += amount
            yearly_cost += amount * 12
        elif frequency == "yearly":
            monthly_cost += amount / 12
            yearly_cost += amount
        
        by_category[sub["category"]] += amount
        
        top_expenses.append({
            "description": sub["description"],
            "amount": amount,
            "frequency": frequency,
            "total_spent": sub["total_spent"],
        })
    
    # Sort top expenses
    top_expenses.sort(key=lambda x: x["total_spent"], reverse=True)
    top_expenses = top_expenses[:5]
    
    # Generate insights
    insights = []
    
    if active_subs:
        insights.append(f"📊 You have {len(active_subs)} active subscription(s)")
        insights.append(f"💰 Monthly subscription cost: ₹{monthly_cost:,.2f}")
        insights.append(f"📅 Yearly subscription cost: ₹{yearly_cost:,.2f}")
    
    if by_category:
        top_category = max(by_category, key=by_category.get)
        insights.append(f"🏷️ Highest spending category: {top_category} (₹{by_category[top_category]:,.2f})")
    
    if monthly_cost > 5000:
        insights.append("⚠️ Your subscription costs are quite high. Consider reviewing and canceling unused subscriptions.")
    elif monthly_cost > 2000:
        insights.append("💡 Your subscription costs are moderate. Keep an eye on them to optimize spending.")
    
    if not insights:
        insights.append("✅ No active subscriptions tracked yet.")
    
    return SubscriptionInsights(
        total_monthly_cost=round(monthly_cost, 2),
        total_yearly_cost=round(yearly_cost, 2),
        active_subscriptions=len(active_subs),
        top_expenses=top_expenses,
        by_category=dict(by_category),
        insights=insights
    )


async def record_payment(db: AsyncIOMotorDatabase, user_id: str, subscription_id: str) -> dict[str, Any] | None:
    """Record a payment for a subscription."""
    if not ObjectId.is_valid(subscription_id):
        return None
    
    subscription = await db.subscriptions.find_one({
        "_id": ObjectId(subscription_id),
        "user_id": ObjectId(user_id),
    })
    
    if not subscription:
        return None
    
    today = Date.today()
    next_payment = _calculate_next_date(
        subscription["next_payment_date"].date() if isinstance(subscription["next_payment_date"], datetime) else subscription["next_payment_date"],
        subscription["frequency"]
    )
    
    await db.subscriptions.update_one(
        {"_id": ObjectId(subscription_id)},
        {
            "$set": {
                "last_payment_date": datetime.combine(today, datetime.min.time()),
                "next_payment_date": datetime.combine(next_payment, datetime.min.time()),
                "total_spent": subscription["total_spent"] + subscription["amount"],
                "payment_count": subscription["payment_count"] + 1,
                "updated_at": utc_now(),
            }
        }
    )
    
    return await get_subscription(db, user_id, subscription_id)