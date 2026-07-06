from collections import defaultdict
from datetime import date as Date
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import ANOMALY_THRESHOLDS
from app.models.documents import SpendingAnomalyDocument
from app.schemas.anomaly import AnomalyAlert, WeeklySpendingReport
from app.services.serializers import serialize_document, utc_now


def get_severity(deviation_percentage: float) -> str:
    """Determine severity level based on deviation percentage."""
    if deviation_percentage >= ANOMALY_THRESHOLDS["critical"]:
        return "critical"
    elif deviation_percentage >= ANOMALY_THRESHOLDS["high"]:
        return "high"
    elif deviation_percentage >= ANOMALY_THRESHOLDS["medium"]:
        return "medium"
    elif deviation_percentage >= ANOMALY_THRESHOLDS["low"]:
        return "low"
    return "low"


def get_suggestion(severity: str, category: str, deviation: float) -> str:
    """Generate actionable suggestion based on anomaly severity."""
    suggestions = {
        "low": f"Your {category.lower()} spending is slightly higher than usual. Keep an eye on it.",
        "medium": f"You're spending significantly more on {category.lower()}. Consider reviewing your {category.lower()} expenses this week.",
        "high": f"Alert: Your {category.lower()} spending is {deviation:.0f}% above average! Try to reduce non-essential spending in this category.",
        "critical": f"Warning: Unusual spike in {category.lower()} spending detected ({deviation:.0f}% above average). Please review your recent transactions immediately."
    }
    return suggestions.get(severity, suggestions["low"])


async def calculate_category_averages(db: AsyncIOMotorDatabase, user_id: str, days: int = 90) -> dict[str, float]:
    """Calculate average spending per category over the last N days."""
    start_date = datetime.now() - timedelta(days=days)
    
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": start_date}
        })
    ]
    
    category_totals: dict[str, list[float]] = defaultdict(list)
    for expense in expenses:
        category_totals[expense["category"]].append(expense["amount"])
    
    averages = {}
    for category, amounts in category_totals.items():
        if amounts:
            averages[category] = sum(amounts) / len(amounts)
    
    return averages


async def detect_anomalies(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Detect spending anomalies by comparing recent expenses to historical averages."""
    # Get averages from last 90 days
    averages = await calculate_category_averages(db, user_id, days=90)
    
    # Get recent expenses (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": week_ago}
        }).sort("date", -1)
    ]
    
    anomalies = []
    for expense in recent_expenses:
        category = expense["category"]
        amount = expense["amount"]
        
        # Skip if we don't have enough historical data
        if category not in averages:
            continue
        
        average = averages[category]
        if average == 0:
            continue
        
        # Calculate deviation
        deviation_percentage = ((amount - average) / average) * 100
        
        # Only flag if spending is significantly higher (not lower)
        if deviation_percentage < ANOMALY_THRESHOLDS["low"]:
            continue
        
        severity = get_severity(deviation_percentage)
        message = f"Spending anomaly detected in {category}: ₹{amount:,.2f} spent (avg: ₹{average:,.2f})"
        suggestion = get_suggestion(severity, category, deviation_percentage)
        
        # Check if anomaly already exists for this expense
        existing = await db.spending_anomalies.find_one({
            "user_id": ObjectId(user_id),
            "category": category,
            "date": expense["date"],
            "amount": amount
        })
        
        if not existing:
            anomaly_doc: SpendingAnomalyDocument = {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "category": category,
                "date": expense["date"],
                "amount": amount,
                "average_amount": round(average, 2),
                "deviation_percentage": round(deviation_percentage, 2),
                "severity": severity,
                "message": message,
                "is_read": False,
                "created_at": utc_now(),
            }
            await db.spending_anomalies.insert_one(anomaly_doc)
            anomalies.append(serialize_document(anomaly_doc))
    
    return anomalies


async def get_anomalies(db: AsyncIOMotorDatabase, user_id: str, unread_only: bool = False) -> list[dict[str, Any]]:
    """Get all anomalies for a user."""
    query = {"user_id": ObjectId(user_id)}
    if unread_only:
        query["is_read"] = False
    
    cursor = db.spending_anomalies.find(query).sort("created_at", -1)
    return [serialize_document(item) async for item in cursor]


async def mark_anomaly_read(db: AsyncIOMotorDatabase, user_id: str, anomaly_id: str) -> dict[str, Any] | None:
    """Mark an anomaly as read."""
    if not ObjectId.is_valid(anomaly_id):
        return None
    
    await db.spending_anomalies.update_one(
        {"_id": ObjectId(anomaly_id), "user_id": ObjectId(user_id)},
        {"$set": {"is_read": True}}
    )
    
    anomaly = await db.spending_anomalies.find_one({
        "_id": ObjectId(anomaly_id),
        "user_id": ObjectId(user_id)
    })
    return serialize_document(anomaly) if anomaly else None


async def generate_weekly_report(db: AsyncIOMotorDatabase, user_id: str) -> WeeklySpendingReport:
    """Generate a weekly spending report with insights."""
    today = Date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    week_start_dt = datetime.combine(week_start, datetime.min.time())
    week_end_dt = datetime.combine(week_end, datetime.max.time())
    
    # Get this week's expenses
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": week_start_dt, "$lte": week_end_dt}
        })
    ]
    
    # Calculate totals
    total_spending = sum(e["amount"] for e in expenses)
    category_breakdown: dict[str, float] = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense["category"]] += expense["amount"]
    
    # Top categories
    top_categories = [
        {"category": cat, "amount": round(amount, 2)}
        for cat, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Get anomalies for this week
    anomalies = await get_anomalies(db, user_id, unread_only=False)
    week_anomalies = [a for a in anomalies if week_start_dt <= a["date"] <= week_end_dt]
    
    # Compare to previous week
    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)
    prev_week_start_dt = datetime.combine(prev_week_start, datetime.min.time())
    prev_week_end_dt = datetime.combine(prev_week_end, datetime.max.time())
    
    prev_week_expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": prev_week_start_dt, "$lte": prev_week_end_dt}
        })
    ]
    prev_week_total = sum(e["amount"] for e in prev_week_expenses)
    
    comparison = None
    if prev_week_total > 0:
        comparison = round(((total_spending - prev_week_total) / prev_week_total) * 100, 1)
    
    # Generate insights
    insights = []
    if total_spending > prev_week_total and comparison:
        insights.append(f"⚠️ Spending increased by {comparison}% compared to last week")
    elif total_spending < prev_week_total and comparison:
        insights.append(f"✅ Great job! Spending decreased by {abs(comparison)}% compared to last week")
    
    if len(week_anomalies) > 0:
        insights.append(f"⚠️ {len(week_anomalies)} spending anomaly(ies) detected this week")
    
    if top_categories:
        top_cat = top_categories[0]["category"]
        top_cat_amount = top_categories[0]["amount"]
        insights.append(f"📊 Highest spending category: {top_cat} (₹{top_cat_amount:,.2f})")
    
    if not insights:
        insights.append("✅ No unusual spending patterns detected this week")
    
    return WeeklySpendingReport(
        week_start=week_start,
        week_end=week_end,
        total_spending=round(total_spending, 2),
        category_breakdown=dict(category_breakdown),
        top_categories=top_categories,
        anomalies_detected=len(week_anomalies),
        comparison_to_previous_week=comparison,
        insights=insights
    )


async def get_anomaly_alerts(db: AsyncIOMotorDatabase, user_id: str) -> list[AnomalyAlert]:
    """Get formatted anomaly alerts for the user."""
    anomalies = await get_anomalies(db, user_id, unread_only=True)
    
    alerts = []
    for anomaly in anomalies[:10]:  # Return top 10
        alerts.append(AnomalyAlert(
            category=anomaly["category"],
            date=anomaly["date"].date() if isinstance(anomaly["date"], datetime) else anomaly["date"],
            amount=anomaly["amount"],
            average_amount=anomaly["average_amount"],
            deviation_percentage=anomaly["deviation_percentage"],
            severity=anomaly["severity"],
            message=anomaly["message"],
            suggestion=get_suggestion(anomaly["severity"], anomaly["category"], anomaly["deviation_percentage"])
        ))
    
    return alerts