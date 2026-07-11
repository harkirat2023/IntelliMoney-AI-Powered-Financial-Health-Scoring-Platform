from collections import defaultdict
from datetime import date as Date
from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.documents import FinancialReportDocument
from app.schemas.report import FinancialReport, ReportSummary
from app.services.analytics_service import get_month_expenses
from app.services.serializers import serialize_document, utc_now


async def generate_weekly_report(db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any]:
    """Generate a weekly financial report."""
    today = Date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    return await _generate_report(db, user_id, "weekly", week_start, week_end)


async def generate_monthly_report(db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any]:
    """Generate a monthly financial report."""
    today = Date.today()
    month_start = Date(today.year, today.month, 1)
    # Get last day of month
    if today.month == 12:
        month_end = Date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = Date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    return await _generate_report(db, user_id, "monthly", month_start, month_end)


async def _generate_report(
    db: AsyncIOMotorDatabase,
    user_id: str,
    report_type: str,
    period_start: Date,
    period_end: Date
) -> dict[str, Any]:
    """Internal function to generate financial reports."""
    # Convert dates to datetime for MongoDB queries
    period_start_dt = datetime.combine(period_start, datetime.min.time())
    period_end_dt = datetime.combine(period_end + timedelta(days=1), datetime.min.time())
    
    # Get expenses for the period
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": period_start_dt, "$lt": period_end_dt}
        })
    ]
    
    # Calculate totals
    total_spending = sum(e["amount"] for e in expenses)
    
    # Get user's monthly income
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    monthly_income = user.get("monthly_income", 0) if user else 0
    
    # Calculate income for the period
    if report_type == "weekly":
        total_income = monthly_income / 4  # Approximate weekly income
    else:
        total_income = monthly_income
    
    net_savings = total_income - total_spending
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Category breakdown
    category_breakdown: dict[str, float] = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense["category"]] += expense["amount"]
    
    # Top expenses
    top_expenses = sorted(expenses, key=lambda x: x["amount"], reverse=True)[:10]
    top_expenses_list = [
        {
            "description": e["description"],
            "amount": e["amount"],
            "category": e["category"],
            "date": e["date"].date().isoformat() if isinstance(e["date"], datetime) else e["date"]
        }
        for e in top_expenses
    ]
    
    # Budget performance
    budget_performance = await _calculate_budget_performance(db, user_id, period_start, period_end)
    
    # Health score
    health_score = None
    health_doc = await db.financial_scores.find_one(
        {"user_id": ObjectId(user_id)},
        sort=[("calculated_at", -1)]
    )
    if health_doc:
        health_score = health_doc.get("score")
    
    # Generate insights
    insights = _generate_insights(
        total_spending, total_income, net_savings, savings_rate,
        category_breakdown, budget_performance, report_type
    )
    
    # Get recommendations
    recommendations = await _get_recommendations(db, user_id, insights)
    
    # Create report document
    report_doc: FinancialReportDocument = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "report_type": report_type,
        "period_start": datetime.combine(period_start, datetime.min.time()),
        "period_end": datetime.combine(period_end, datetime.min.time()),
        "total_spending": round(total_spending, 2),
        "total_income": round(total_income, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": round(savings_rate, 2),
        "category_breakdown": dict(category_breakdown),
        "top_expenses": top_expenses_list,
        "budget_performance": budget_performance,
        "health_score": health_score,
        "insights": insights,
        "recommendations": recommendations,
        "generated_at": utc_now(),
        "is_read": False,
    }
    
    await db.financial_reports.insert_one(report_doc)
    return serialize_document(report_doc)


async def _calculate_budget_performance(
    db: AsyncIOMotorDatabase,
    user_id: str,
    period_start: Date,
    period_end: Date
) -> dict[str, Any]:
    """Calculate budget performance for the period."""
    # Get budgets for the period
    budgets = [
        serialize_document(item)
        async for item in db.budgets.find({"user_id": ObjectId(user_id)})
    ]
    
    if not budgets:
        return {"total_budget": 0, "spent": 0, "remaining": 0, "categories": {}}
    
    # Get expenses for the period
    period_start_dt = datetime.combine(period_start, datetime.min.time())
    period_end_dt = datetime.combine(period_end + timedelta(days=1), datetime.min.time())
    
    expenses = [
        serialize_document(item)
        async for item in db.expenses.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": period_start_dt, "$lt": period_end_dt}
        })
    ]
    
    # Calculate spending by category
    spent_by_category: dict[str, float] = defaultdict(float)
    for expense in expenses:
        spent_by_category[expense["category"]] += expense["amount"]
    
    # Calculate performance
    total_budget = sum(b["limit"] for b in budgets)
    total_spent = sum(spent_by_category.get(b["category"], 0) for b in budgets)
    
    categories = {}
    for budget in budgets:
        category = budget["category"]
        limit = float(budget["limit"])
        spent = spent_by_category.get(category, 0)
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        categories[category] = {
            "budget": limit,
            "spent": round(spent, 2),
            "remaining": round(limit - spent, 2),
            "percentage": round(percentage, 2),
            "status": "over" if percentage >= 100 else "warning" if percentage >= 80 else "safe"
        }
    
    return {
        "total_budget": round(total_budget, 2),
        "spent": round(total_spent, 2),
        "remaining": round(total_budget - total_spent, 2),
        "categories": categories
    }


def _generate_insights(
    total_spending: float,
    total_income: float,
    net_savings: float,
    savings_rate: float,
    category_breakdown: dict[str, float],
    budget_performance: dict[str, Any],
    report_type: str
) -> list[str]:
    """Generate actionable insights for the report."""
    insights = []
    
    # Savings insights
    if savings_rate >= 20:
        insights.append(f"✅ Excellent! You saved {savings_rate:.1f}% of your income this {report_type}")
    elif savings_rate >= 10:
        insights.append(f"👍 Good job! You saved {savings_rate:.1f}% of your income. Try to reach 20% for better financial health.")
    elif savings_rate > 0:
        insights.append(f"⚠️ Your savings rate is {savings_rate:.1f}%. Aim to save at least 10-20% of your income.")
    else:
        insights.append("🚨 You're spending more than you earn! Review your expenses immediately.")
    
    # Top spending category
    if category_breakdown:
        top_category = max(category_breakdown, key=category_breakdown.get)
        top_amount = category_breakdown[top_category]
        top_percentage = (top_amount / total_spending * 100) if total_spending > 0 else 0
        insights.append(f"📊 Highest spending: {top_category} at ₹{top_amount:,.2f} ({top_percentage:.1f}% of total)")
    
    # Budget performance
    if budget_performance.get("categories"):
        over_budget = [cat for cat, data in budget_performance["categories"].items() if data["status"] == "over"]
        warning_budget = [cat for cat, data in budget_performance["categories"].items() if data["status"] == "warning"]
        
        if over_budget:
            insights.append(f"⚠️ Over budget in: {', '.join(over_budget)}")
        if warning_budget:
            insights.append(f"⚡ Approaching budget limit in: {', '.join(warning_budget)}")
    
    # Spending trend
    if total_spending > 0:
        insights.append(f"💰 Total spending this {report_type}: ₹{total_spending:,.2f}")
    
    return insights


async def _get_recommendations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    insights: list[str]
) -> list[dict[str, str]]:
    """Get personalized recommendations based on insights."""
    recommendations = []
    
    # Check for existing recommendations
    existing = await db.recommendations.find_one(
        {"user_id": ObjectId(user_id)},
        sort=[("created_at", -1)]
    )
    
    if existing and existing.get("items"):
        return existing["items"][:5]  # Return top 5
    
    # Generate basic recommendations
    if any("savings rate" in insight.lower() for insight in insights):
        recommendations.append({
            "title": "Increase Savings",
            "message": "Try to save at least 20% of your income for better financial security.",
            "action": "Review your expenses and identify areas to cut back."
        })
    
    if any("over budget" in insight.lower() for insight in insights):
        recommendations.append({
            "title": "Control Overspending",
            "message": "You're exceeding budgets in some categories.",
            "action": "Use the Budget Optimizer to adjust your limits."
        })
    
    if not recommendations:
        recommendations.append({
            "title": "Keep It Up!",
            "message": "Your spending looks healthy this period.",
            "action": "Continue tracking expenses and maintaining budgets."
        })
    
    return recommendations


async def get_reports(db: AsyncIOMotorDatabase, user_id: str, report_type: str | None = None) -> list[dict[str, Any]]:
    """Get all reports for a user, optionally filtered by type."""
    query = {"user_id": ObjectId(user_id)}
    if report_type:
        query["report_type"] = report_type
    
    cursor = db.financial_reports.find(query).sort("generated_at", -1)
    return [serialize_document(item) async for item in cursor]


async def get_report(db: AsyncIOMotorDatabase, user_id: str, report_id: str) -> dict[str, Any] | None:
    """Get a specific report."""
    if not ObjectId.is_valid(report_id):
        return None
    
    report = await db.financial_reports.find_one({
        "_id": ObjectId(report_id),
        "user_id": ObjectId(user_id)
    })
    return serialize_document(report) if report else None


async def mark_report_read(db: AsyncIOMotorDatabase, user_id: str, report_id: str) -> dict[str, Any] | None:
    """Mark a report as read."""
    if not ObjectId.is_valid(report_id):
        return None
    
    await db.financial_reports.update_one(
        {"_id": ObjectId(report_id), "user_id": ObjectId(user_id)},
        {"$set": {"is_read": True}}
    )
    
    report = await db.financial_reports.find_one({
        "_id": ObjectId(report_id),
        "user_id": ObjectId(user_id)
    })
    return serialize_document(report) if report else None


async def get_report_summary(db: AsyncIOMotorDatabase, user_id: str) -> ReportSummary:
    """Get summary of user's reports."""
    # Get all reports
    reports = await get_reports(db, user_id)
    
    # Calculate statistics
    total_reports = len(reports)
    unread_count = sum(1 for r in reports if not r.get("is_read", False))
    latest_report = reports[0] if reports else None
    
    # Calculate averages from monthly reports
    monthly_reports = [r for r in reports if r.get("report_type") == "monthly"]
    if monthly_reports:
        avg_spending = sum(r.get("total_spending", 0) for r in monthly_reports) / len(monthly_reports)
        avg_savings_rate = sum(r.get("savings_rate", 0) for r in monthly_reports) / len(monthly_reports)
        
        # Determine trend
        if len(monthly_reports) >= 2:
            recent_spending = monthly_reports[0].get("total_spending", 0)
            older_spending = monthly_reports[1].get("total_spending", 0)
            if recent_spending > older_spending * 1.1:
                trend = "increasing"
            elif recent_spending < older_spending * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
    else:
        avg_spending = 0
        avg_savings_rate = 0
        trend = "stable"
    
    return ReportSummary(
        total_reports=total_reports,
        latest_report=latest_report,
        unread_count=unread_count,
        average_monthly_spending=round(avg_spending, 2),
        average_savings_rate=round(avg_savings_rate, 2),
        spending_trend=trend
    )