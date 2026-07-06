from datetime import datetime


class BudgetIntelligence:
    def __init__(
        self,
        user_id: str,
        period: str,
        budget_score: float = 0.0,
        total_budget: float = 0.0,
        total_spent: float = 0.0,
        total_suggested: float = 0.0,
        potential_savings: float = 0.0,
        category_count: int = 0,
        on_track_count: int = 0,
        warning_count: int = 0,
        over_count: int = 0,
        categories: list[dict] | None = None,
        calculated_at: datetime | None = None,
        id: str | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.period = period
        self.budget_score = budget_score
        self.total_budget = total_budget
        self.total_spent = total_spent
        self.total_suggested = total_suggested
        self.potential_savings = potential_savings
        self.category_count = category_count
        self.on_track_count = on_track_count
        self.warning_count = warning_count
        self.over_count = over_count
        self.categories = categories or []
        self.calculated_at = calculated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetIntelligence":
        return cls(
            id=str(doc.get("_id", "")),
            user_id=str(doc.get("user_id", "")),
            period=doc.get("period", ""),
            budget_score=doc.get("budget_score", 0.0),
            total_budget=doc.get("total_budget", 0.0),
            total_spent=doc.get("total_spent", 0.0),
            total_suggested=doc.get("total_suggested", 0.0),
            potential_savings=doc.get("potential_savings", 0.0),
            category_count=doc.get("category_count", 0),
            on_track_count=doc.get("on_track_count", 0),
            warning_count=doc.get("warning_count", 0),
            over_count=doc.get("over_count", 0),
            categories=doc.get("categories", []),
            calculated_at=doc.get("calculated_at"),
        )

    def to_mongo(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "period": self.period,
            "budget_score": self.budget_score,
            "total_budget": self.total_budget,
            "total_spent": self.total_spent,
            "total_suggested": self.total_suggested,
            "potential_savings": self.potential_savings,
            "category_count": self.category_count,
            "on_track_count": self.on_track_count,
            "warning_count": self.warning_count,
            "over_count": self.over_count,
            "categories": self.categories,
            "calculated_at": self.calculated_at,
        }
        if self.id:
            doc["_id"] = self.id
        return doc
