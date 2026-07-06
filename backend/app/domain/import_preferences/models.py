from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel

from app.utils.date_utils import utc_now


class ImportPreference(BaseModel):
    id: str | None = None
    user_id: str
    bank_account_id: str
    import_type: str
    import_start_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def get_sync_range(self) -> tuple[datetime | None, datetime]:
        now = utc_now()
        if self.import_type == "import_all":
            return (None, now)
        elif self.import_type == "start_fresh":
            return (now, now)
        else:
            return (self.import_start_date, now)

    @classmethod
    def from_mongo(cls, doc: dict) -> "ImportPreference":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            bank_account_id=str(doc["bank_account_id"]),
            import_type=doc["import_type"],
            import_start_date=doc.get("import_start_date"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id", "bank_account_id"})
        data["user_id"] = ObjectId(self.user_id)
        data["bank_account_id"] = ObjectId(self.bank_account_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
