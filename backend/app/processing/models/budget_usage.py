from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class BudgetUsage(BaseModel):
    id: str | None = None
    user_id: str
    budget_id: str
    category: str
    month: int
    year: int
    limit: float
    spent: float
    remaining: float
    percentage_used: float
    state: str = "safe"
    updated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "BudgetUsage":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            budget_id=str(doc["budget_id"]),
            category=doc["category"],
            month=doc["month"],
            year=doc["year"],
            limit=float(doc["limit"]),
            spent=float(doc["spent"]),
            remaining=float(doc["remaining"]),
            percentage_used=float(doc["percentage_used"]),
            state=doc.get("state", "safe"),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "budget_id"})
        data["user_id"] = ObjectId(self.user_id)
        data["budget_id"] = ObjectId(self.budget_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
