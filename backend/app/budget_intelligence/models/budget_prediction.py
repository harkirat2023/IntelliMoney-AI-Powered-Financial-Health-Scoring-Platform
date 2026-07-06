from datetime import datetime


class BudgetPrediction:
    def __init__(
        self,
        user_id: str,
        period: str,
        category: str,
        predicted_spending: float = 0.0,
        predicted_utilization: float = 0.0,
        confidence_upper: float = 0.0,
        confidence_lower: float = 0.0,
        trend_direction: str = "stable",
        months_analyzed: int = 0,
        calculated_at: datetime | None = None,
        id: str | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.period = period
        self.category = category
        self.predicted_spending = predicted_spending
        self.predicted_utilization = predicted_utilization
        self.confidence_upper = confidence_upper
        self.confidence_lower = confidence_lower
        self.trend_direction = trend_direction
        self.months_analyzed = months_analyzed
        self.calculated_at = calculated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetPrediction":
        return cls(
            id=str(doc.get("_id", "")),
            user_id=str(doc.get("user_id", "")),
            period=doc.get("period", ""),
            category=doc.get("category", ""),
            predicted_spending=doc.get("predicted_spending", 0.0),
            predicted_utilization=doc.get("predicted_utilization", 0.0),
            confidence_upper=doc.get("confidence_upper", 0.0),
            confidence_lower=doc.get("confidence_lower", 0.0),
            trend_direction=doc.get("trend_direction", "stable"),
            months_analyzed=doc.get("months_analyzed", 0),
            calculated_at=doc.get("calculated_at"),
        )

    def to_mongo(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "period": self.period,
            "category": self.category,
            "predicted_spending": self.predicted_spending,
            "predicted_utilization": self.predicted_utilization,
            "confidence_upper": self.confidence_upper,
            "confidence_lower": self.confidence_lower,
            "trend_direction": self.trend_direction,
            "months_analyzed": self.months_analyzed,
            "calculated_at": self.calculated_at,
        }
        if self.id:
            doc["_id"] = self.id
        return doc
