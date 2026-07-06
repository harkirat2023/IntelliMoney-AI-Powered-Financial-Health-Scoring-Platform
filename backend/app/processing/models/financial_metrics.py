from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class FinancialMetrics(BaseModel):
    id: str | None = None
    user_id: str
    period: str
    calculated_at: datetime | None = None
    score: int = 0
    risk_level: str = "Needs Attention"
    savings_rate: float = 0.0
    budget_adherence: float = 0.0
    expense_stability: float = 0.0
    discretionary_ratio: float = 0.0
    month_over_month_change: float = 0.0
    trend: str = "stable"

    @classmethod
    def from_mongo(cls, doc: dict) -> "FinancialMetrics":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            period=doc["period"],
            calculated_at=doc.get("calculated_at"),
            score=int(doc.get("score", 0)),
            risk_level=doc.get("risk_level", "Needs Attention"),
            savings_rate=float(doc.get("savings_rate", 0)),
            budget_adherence=float(doc.get("budget_adherence", 0)),
            expense_stability=float(doc.get("expense_stability", 0)),
            discretionary_ratio=float(doc.get("discretionary_ratio", 0)),
            month_over_month_change=float(doc.get("month_over_month_change", 0)),
            trend=doc.get("trend", "stable"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
