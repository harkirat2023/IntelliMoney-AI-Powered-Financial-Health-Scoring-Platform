from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class CashFlowSummary(BaseModel):
    id: str | None = None
    user_id: str
    year: int
    month: int
    total_income: float = 0.0
    total_expenses: float = 0.0
    net_cash_flow: float = 0.0
    income_by_category: list[dict] = []
    expense_by_category: list[dict] = []
    updated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "CashFlowSummary":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            year=doc["year"],
            month=doc["month"],
            total_income=float(doc.get("total_income", 0)),
            total_expenses=float(doc.get("total_expenses", 0)),
            net_cash_flow=float(doc.get("net_cash_flow", 0)),
            income_by_category=list(doc.get("income_by_category", [])),
            expense_by_category=list(doc.get("expense_by_category", [])),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
