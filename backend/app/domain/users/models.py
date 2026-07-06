from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str | None = None
    email: str
    name: str
    hashed_password: str
    monthly_income: float = 0.0
    created_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "User":
        return cls(
            id=str(doc["_id"]),
            email=doc["email"],
            name=doc["name"],
            hashed_password=doc["hashed_password"],
            monthly_income=float(doc.get("monthly_income", 0)),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id"})
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
