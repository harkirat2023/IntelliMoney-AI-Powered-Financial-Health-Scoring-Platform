from datetime import date as Date
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class Expense(BaseModel):
    id: str | None = None
    user_id: str
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=240)
    category: str = "Other"
    payment_method: str = "Other"
    date: Date
    created_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "Expense":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            amount=float(doc["amount"]),
            description=doc["description"],
            category=doc.get("category", "Other"),
            payment_method=doc.get("payment_method", "Other"),
            date=doc["date"],
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
