from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    id: str | None = None
    user_id: str
    provider: str
    consent_handle: str
    provider_account_id: str
    bank_name: str
    masked_account_number: str
    account_type: str
    account_holder_name: str
    ifsc_code: str
    connection_status: str = "active"
    consent_status: str = "active"
    consent_token: str = ""
    consent_version: str = "1.0"
    consent_expiry: datetime | None = None
    last_synced_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "BankAccount":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            provider=doc["provider"],
            consent_handle=doc["consent_handle"],
            provider_account_id=doc["provider_account_id"],
            bank_name=doc["bank_name"],
            masked_account_number=doc["masked_account_number"],
            account_type=doc["account_type"],
            account_holder_name=doc["account_holder_name"],
            ifsc_code=doc["ifsc_code"],
            connection_status=doc.get("connection_status", "active"),
            consent_status=doc.get("consent_status", "active"),
            consent_token=doc.get("consent_token", ""),
            consent_version=doc.get("consent_version", "1.0"),
            consent_expiry=doc.get("consent_expiry"),
            last_synced_at=doc.get("last_synced_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude={"id", "user_id"})
        data["user_id"] = ObjectId(self.user_id)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
