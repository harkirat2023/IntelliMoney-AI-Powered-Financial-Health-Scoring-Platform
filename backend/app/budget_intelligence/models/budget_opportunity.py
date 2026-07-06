from datetime import datetime


class BudgetOpportunity:
    def __init__(
        self,
        user_id: str,
        opportunity_type: str,
        category: str,
        title: str,
        message: str,
        potential_savings: float = 0.0,
        confidence_score: float = 0.0,
        monthly_impact: float = 0.0,
        annual_impact: float = 0.0,
        reasoning: str = "",
        actionable_steps: list[str] | None = None,
        dismissed: bool = False,
        created_at: datetime | None = None,
        id: str | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.opportunity_type = opportunity_type
        self.category = category
        self.title = title
        self.message = message
        self.potential_savings = potential_savings
        self.confidence_score = confidence_score
        self.monthly_impact = monthly_impact
        self.annual_impact = annual_impact
        self.reasoning = reasoning
        self.actionable_steps = actionable_steps or []
        self.dismissed = dismissed
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetOpportunity":
        return cls(
            id=str(doc.get("_id", "")),
            user_id=str(doc.get("user_id", "")),
            opportunity_type=doc.get("opportunity_type", ""),
            category=doc.get("category", ""),
            title=doc.get("title", ""),
            message=doc.get("message", ""),
            potential_savings=doc.get("potential_savings", 0.0),
            confidence_score=doc.get("confidence_score", 0.0),
            monthly_impact=doc.get("monthly_impact", 0.0),
            annual_impact=doc.get("annual_impact", 0.0),
            reasoning=doc.get("reasoning", ""),
            actionable_steps=doc.get("actionable_steps", []),
            dismissed=doc.get("dismissed", False),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "opportunity_type": self.opportunity_type,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "potential_savings": self.potential_savings,
            "confidence_score": self.confidence_score,
            "monthly_impact": self.monthly_impact,
            "annual_impact": self.annual_impact,
            "reasoning": self.reasoning,
            "actionable_steps": self.actionable_steps,
            "dismissed": self.dismissed,
            "created_at": self.created_at,
        }
        if self.id:
            doc["_id"] = self.id
        return doc
