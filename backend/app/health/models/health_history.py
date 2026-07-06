from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class HealthHistory(BaseModel):
    id: str | None = None
    user_id: str
    period: str
    score: int
    risk_level: str
    savings_rate: float = 0.0
    budget_adherence: float = 0.0
    expense_stability: float = 0.0
    cash_flow_stability: float = 0.0
    income_consistency: float = 0.0
    emergency_fund_score: float = 0.0
    recurring_expense_ratio: float = 0.0
    essential_spending_ratio: float = 0.0
    calculated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "HealthHistory":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            period=doc["period"],
            score=int(doc.get("score", 0)),
            risk_level=doc.get("risk_level", "Needs Attention"),
            savings_rate=float(doc.get("savings_rate", 0)),
            budget_adherence=float(doc.get("budget_adherence", 0)),
            expense_stability=float(doc.get("expense_stability", 0)),
            cash_flow_stability=float(doc.get("cash_flow_stability", 0)),
            income_consistency=float(doc.get("income_consistency", 0)),
            emergency_fund_score=float(doc.get("emergency_fund_score", 0)),
            recurring_expense_ratio=float(doc.get("recurring_expense_ratio", 0)),
            essential_spending_ratio=float(doc.get("essential_spending_ratio", 0)),
            calculated_at=doc.get("calculated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
