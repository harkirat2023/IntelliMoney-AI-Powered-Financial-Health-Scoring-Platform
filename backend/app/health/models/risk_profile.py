from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class RiskProfile(BaseModel):
    id: str | None = None
    user_id: str
    period: str
    overall_risk_level: str = "Moderate"
    overall_risk_score: int = 50
    savings_risk: str = "moderate"
    budget_risk: str = "moderate"
    expense_risk: str = "moderate"
    cash_flow_risk: str = "moderate"
    income_risk: str = "moderate"
    emergency_risk: str = "moderate"
    recurring_risk: str = "moderate"
    calculated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "RiskProfile":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            period=doc["period"],
            overall_risk_level=doc.get("overall_risk_level", "Moderate"),
            overall_risk_score=int(doc.get("overall_risk_score", 50)),
            savings_risk=doc.get("savings_risk", "moderate"),
            budget_risk=doc.get("budget_risk", "moderate"),
            expense_risk=doc.get("expense_risk", "moderate"),
            cash_flow_risk=doc.get("cash_flow_risk", "moderate"),
            income_risk=doc.get("income_risk", "moderate"),
            emergency_risk=doc.get("emergency_risk", "moderate"),
            recurring_risk=doc.get("recurring_risk", "moderate"),
            calculated_at=doc.get("calculated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
