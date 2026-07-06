from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field

from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class ConsentGrant(BaseModel):
    id: str | None = None
    user_id: str
    bank_account_id: str
    consent_status: str = "granted"
    consent_version: str = "1.0"
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_active(self) -> bool:
        return (
            self.consent_status == "granted"
            and (self.expires_at is None or self.expires_at > utc_now())
        )

    def revoke(self) -> None:
        now = utc_now()
        self.consent_status = "revoked"
        self.revoked_at = now
        self.updated_at = now

    @classmethod
    def from_mongo(cls, doc: dict) -> "ConsentGrant":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            bank_account_id=str(doc["bank_account_id"]),
            consent_status=doc.get("consent_status", "granted"),
            consent_version=doc.get("consent_version", "1.0"),
            granted_at=doc.get("granted_at"),
            expires_at=doc.get("expires_at"),
            revoked_at=doc.get("revoked_at"),
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
