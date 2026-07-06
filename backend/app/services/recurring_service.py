from collections import defaultdict
from datetime import date as Date
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.documents import RecurringExpenseDocument
from app.schemas.recurring import RecurringExpenseSuggestion
from app.services.serializers import serialize_document, utc_now
from app.utils.frequency import _calculate_next_date, _detect_frequency


async def create_recurring_expense(
    db: AsyncIOMotorDatabase,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    now = utc_now()
    document: RecurringExpenseDocument = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "description": payload["description"],
        "amount": float(payload["amount"]),
        "category": payload["category"],
        "frequency": payload["frequency"],
        "start_date": datetime.combine(payload["start_date"], datetime.min.time()),
        "end_date": datetime.combine(payload["end_date"], datetime.min.time()) if payload.get("end_date") else None,
        "is_active": payload.get("is_active", True),
        "last_generated_date": None,
        "next_expected_date": _calculate_next_date(payload["start_date"], payload["frequency"]),
        "created_at": now,
        "updated_at": now,
    }
    await db.recurring_expenses.insert_one(document)
    return serialize_document(document)


async def get_recurring_expenses(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    cursor = db.recurring_expenses.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
    return [serialize_document(item) async for item in cursor]


async def get_recurring_expense(db: AsyncIOMotorDatabase, user_id: str, recurring_id: str) -> dict[str, Any] | None:
    if not ObjectId.is_valid(recurring_id):
        return None
    item = await db.recurring_expenses.find_one({
        "_id": ObjectId(recurring_id),
        "user_id": ObjectId(user_id),
    })
    return serialize_document(item) if item else None


async def update_recurring_expense(
    db: AsyncIOMotorDatabase,
    user_id: str,
    recurring_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not ObjectId.is_valid(recurring_id):
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
        update_fields["start_date"] = datetime.combine(payload["start_date"], datetime.min.time())
    if "end_date" in payload:
        update_fields["end_date"] = datetime.combine(payload["end_date"], datetime.min.time()) if payload["end_date"] else None
    if "is_active" in payload:
        update_fields["is_active"] = payload["is_active"]
    
    # Recalculate next expected date if frequency or start_date changed
    if "frequency" in payload or "start_date" in payload:
        recurring = await db.recurring_expenses.find_one({"_id": ObjectId(recurring_id)})
        if recurring:
            freq = update_fields.get("frequency", recurring["frequency"])
            start = update_fields.get("start_date", recurring["start_date"])
            update_fields["next_expected_date"] = _calculate_next_date(start.date(), freq)
    
    await db.recurring_expenses.update_one(
        {"_id": ObjectId(recurring_id), "user_id": ObjectId(user_id)},
        {"$set": update_fields},
    )
    return await get_recurring_expense(db, user_id, recurring_id)


async def delete_recurring_expense(db: AsyncIOMotorDatabase, user_id: str, recurring_id: str) -> bool:
    if not ObjectId.is_valid(recurring_id):
        return False
    result = await db.recurring_expenses.delete_one({
        "_id": ObjectId(recurring_id),
        "user_id": ObjectId(user_id),
    })
    return result.deleted_count > 0





async def detect_recurring_patterns(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    """Analyze expense history to detect potential recurring expenses."""
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({"user_id": ObjectId(user_id)}).sort("date", 1)
    ]
    
    if len(expenses) < 2:
        return []
    
    # Group expenses by normalized description
    description_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for expense in expenses:
        normalized = expense["description"].lower().strip()
        description_groups[normalized].append(expense)
    
    suggestions = []
    for description, group in description_groups.items():
        if len(group) < 2:
            continue
        
        # Check if amounts are consistent (within 10% variance)
        amounts = [e["amount"] for e in group]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = all(abs(a - avg_amount) / avg_amount < 0.1 for a in amounts)
        
        if not amount_variance:
            continue
        
        # Check if dates follow a pattern
        dates = [e["date"].date() if isinstance(e["date"], datetime) else e["date"] for e in group]
        dates.sort()
        
        # Calculate intervals between dates
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            intervals.append(interval)
        
        # Determine frequency based on intervals
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        frequency = _detect_frequency(avg_interval)
        
        if not frequency:
            continue
        
        # Calculate confidence based on consistency
        confidence = min(0.95, 0.5 + (len(group) * 0.1))
        
        suggestions.append({
            "description": group[0]["description"],
            "amount": round(avg_amount, 2),
            "category": group[0]["category"],
            "frequency": frequency,
            "confidence": round(confidence, 2),
            "occurrences_detected": len(group),
            "suggested_start_date": dates[0],
            "suggested_end_date": None,
        })
    
    # Sort by confidence and occurrences
    suggestions.sort(key=lambda x: (x["confidence"], x["occurrences_detected"]), reverse=True)
    return suggestions[:10]  # Return top 10 suggestions


async def generate_upcoming_expenses(db: AsyncIOMotorDatabase, user_id: str, days_ahead: int = 30) -> list[dict[str, Any]]:
    """Generate upcoming recurring expenses for the next N days."""
    today = Date.today()
    end_date = today + timedelta(days=days_ahead)
    
    recurring = await get_recurring_expenses(db, user_id)
    upcoming = []
    
    for item in recurring:
        if not item["is_active"]:
            continue
        
        next_date = item.get("next_expected_date")
        if not next_date:
            continue
        
        # Convert string date to Date object if needed
        if isinstance(next_date, str):
            next_date = Date.fromisoformat(next_date)
        elif isinstance(next_date, datetime):
            next_date = next_date.date()
        
        # Generate all occurrences within the date range
        current_date = next_date
        while current_date <= end_date:
            if item.get("end_date"):
                end = item["end_date"].date() if isinstance(item["end_date"], datetime) else item["end_date"]
                if current_date > end:
                    break
            
            upcoming.append({
                "description": item["description"],
                "amount": item["amount"],
                "category": item["category"],
                "expected_date": current_date.isoformat(),
                "frequency": item["frequency"],
            })
            
            # Calculate next occurrence
            current_date = _calculate_next_date(current_date, item["frequency"])
    
    # Sort by date
    upcoming.sort(key=lambda x: x["expected_date"])
    return upcoming