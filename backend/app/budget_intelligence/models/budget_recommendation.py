from datetime import datetime


class BudgetRecommendation:
    def __init__(
        self,
        user_id: str,
        category: str,
        recommendation_type: str,
        title: str,
        message: str,
        current_value: float = 0.0,
        target_value: float = 0.0,
        potential_savings: float = 0.0,
        confidence_score: float = 0.0,
        priority: str = "medium",
        reasoning: str = "",
        affected_categories: list[str] | None = None,
        estimated_impact: str = "",
        actionable_steps: list[str] | None = None,
        dismissed: bool = False,
        created_at: datetime | None = None,
        id: str | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.category = category
        self.recommendation_type = recommendation_type
        self.title = title
        self.message = message
        self.current_value = current_value
        self.target_value = target_value
        self.potential_savings = potential_savings
        self.confidence_score = confidence_score
        self.priority = priority
        self.reasoning = reasoning
        self.affected_categories = affected_categories or []
        self.estimated_impact = estimated_impact
        self.actionable_steps = actionable_steps or []
        self.dismissed = dismissed
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetRecommendation":
        return cls(
            id=str(doc.get("_id", "")),
            user_id=str(doc.get("user_id", "")),
            category=doc.get("category", ""),
            recommendation_type=doc.get("recommendation_type", ""),
            title=doc.get("title", ""),
            message=doc.get("message", ""),
            current_value=doc.get("current_value", 0.0),
            target_value=doc.get("target_value", 0.0),
            potential_savings=doc.get("potential_savings", 0.0),
            confidence_score=doc.get("confidence_score", 0.0),
            priority=doc.get("priority", "medium"),
            reasoning=doc.get("reasoning", ""),
            affected_categories=doc.get("affected_categories", []),
            estimated_impact=doc.get("estimated_impact", ""),
            actionable_steps=doc.get("actionable_steps", []),
            dismissed=doc.get("dismissed", False),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "category": self.category,
            "recommendation_type": self.recommendation_type,
            "title": self.title,
            "message": self.message,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "potential_savings": self.potential_savings,
            "confidence_score": self.confidence_score,
            "priority": self.priority,
            "reasoning": self.reasoning,
            "affected_categories": self.affected_categories,
            "estimated_impact": self.estimated_impact,
            "actionable_steps": self.actionable_steps,
            "dismissed": self.dismissed,
            "created_at": self.created_at,
        }
        if self.id:
            doc["_id"] = self.id
        return doc
