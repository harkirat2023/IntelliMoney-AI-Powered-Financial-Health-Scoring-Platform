from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class MonthlySummary(BaseModel):
    id: str | None = None
    user_id: str
    period: str
    total_income: float = 0.0
    total_expenses: float = 0.0
    net_savings: float = 0.0
    savings_rate: float = 0.0
    expense_count: int = 0
    by_category: list[dict] = []
    top_merchants: list[dict] = []
    updated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "MonthlySummary":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            period=doc["period"],
            total_income=float(doc.get("total_income", 0)),
            total_expenses=float(doc.get("total_expenses", 0)),
            net_savings=float(doc.get("net_savings", 0)),
            savings_rate=float(doc.get("savings_rate", 0)),
            expense_count=int(doc.get("expense_count", 0)),
            by_category=list(doc.get("by_category", [])),
            top_merchants=list(doc.get("top_merchants", [])),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
