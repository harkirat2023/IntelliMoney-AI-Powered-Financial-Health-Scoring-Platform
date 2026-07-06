from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class HealthRecommendation(BaseModel):
    id: str | None = None
    user_id: str
    category: str
    priority: str = "medium"
    title: str
    message: str
    metric: str = ""
    current_value: float = 0.0
    target_value: float = 0.0
    impact: str = "low"
    action: str = ""
    dismissed: bool = False
    created_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "HealthRecommendation":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            category=doc["category"],
            priority=doc.get("priority", "medium"),
            title=doc["title"],
            message=doc.get("message", ""),
            metric=doc.get("metric", ""),
            current_value=float(doc.get("current_value", 0)),
            target_value=float(doc.get("target_value", 0)),
            impact=doc.get("impact", "low"),
            action=doc.get("action", ""),
            dismissed=doc.get("dismissed", False),
            created_at=doc.get("created_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
