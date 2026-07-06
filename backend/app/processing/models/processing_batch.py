from datetime import datetime
from typing import Literal

from bson import ObjectId
from pydantic import BaseModel


class ProcessingError(BaseModel):
    transaction_id: str
    stage: str
    message: str
    error_type: str = "general"


class ProcessingSummary(BaseModel):
    expenses_created: int = 0
    expenses_skipped: int = 0
    budget_usage_updated: int = 0
    dashboard_metrics_updated: int = 0
    financial_metrics_updated: int = 0
    cash_flow_updated: int = 0
    alerts_generated: int = 0


class ProcessingBatch(BaseModel):
    id: str | None = None
    batch_id: str
    user_id: str
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    total: int = 0
    processed: int = 0
    failed: int = 0
    errors: list[ProcessingError] = []
    summary: ProcessingSummary | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "ProcessingBatch":
        summary_data = doc.get("summary")
        summary = ProcessingSummary(**summary_data) if summary_data else None
        return cls(
            id=str(doc["_id"]),
            batch_id=str(doc["batch_id"]),
            user_id=str(doc["user_id"]),
            status=doc.get("status", "pending"),
            total=int(doc.get("total", 0)),
            processed=int(doc.get("processed", 0)),
            failed=int(doc.get("failed", 0)),
            errors=[ProcessingError(**e) for e in doc.get("errors", [])],
            summary=summary,
            created_at=doc.get("created_at"),
            completed_at=doc.get("completed_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "summary", "errors"})
        data["user_id"] = ObjectId(self.user_id)
        data["errors"] = [e.model_dump() for e in self.errors]
        if self.summary:
            data["summary"] = self.summary.model_dump()
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
