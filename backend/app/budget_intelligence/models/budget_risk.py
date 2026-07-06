from datetime import datetime


class BudgetRisk:
    def __init__(
        self,
        user_id: str,
        period: str,
        overall_risk_level: str = "low",
        overall_risk_score: float = 0.0,
        overspending_categories: list[dict] | None = None,
        recurring_risk: list[dict] | None = None,
        volatility_score: float = 0.0,
        trend_direction: str = "stable",
        high_risk_count: int = 0,
        medium_risk_count: int = 0,
        low_risk_count: int = 0,
        calculated_at: datetime | None = None,
        id: str | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.period = period
        self.overall_risk_level = overall_risk_level
        self.overall_risk_score = overall_risk_score
        self.overspending_categories = overspending_categories or []
        self.recurring_risk = recurring_risk or []
        self.volatility_score = volatility_score
        self.trend_direction = trend_direction
        self.high_risk_count = high_risk_count
        self.medium_risk_count = medium_risk_count
        self.low_risk_count = low_risk_count
        self.calculated_at = calculated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetRisk":
        return cls(
            id=str(doc.get("_id", "")),
            user_id=str(doc.get("user_id", "")),
            period=doc.get("period", ""),
            overall_risk_level=doc.get("overall_risk_level", "low"),
            overall_risk_score=doc.get("overall_risk_score", 0.0),
            overspending_categories=doc.get("overspending_categories", []),
            recurring_risk=doc.get("recurring_risk", []),
            volatility_score=doc.get("volatility_score", 0.0),
            trend_direction=doc.get("trend_direction", "stable"),
            high_risk_count=doc.get("high_risk_count", 0),
            medium_risk_count=doc.get("medium_risk_count", 0),
            low_risk_count=doc.get("low_risk_count", 0),
            calculated_at=doc.get("calculated_at"),
        )

    def to_mongo(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "period": self.period,
            "overall_risk_level": self.overall_risk_level,
            "overall_risk_score": self.overall_risk_score,
            "overspending_categories": self.overspending_categories,
            "recurring_risk": self.recurring_risk,
            "volatility_score": self.volatility_score,
            "trend_direction": self.trend_direction,
            "high_risk_count": self.high_risk_count,
            "medium_risk_count": self.medium_risk_count,
            "low_risk_count": self.low_risk_count,
            "calculated_at": self.calculated_at,
        }
        if self.id:
            doc["_id"] = self.id
        return doc
