from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, field_validator


class ConsentGrantRequest(BaseModel):
    bank_account_id: str
    consent_version: str = "1.0"
    consent_duration_days: int = 365

    @field_validator("consent_duration_days")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("consent_duration_days must be greater than 0")
        if v > 3650:
            raise ValueError("consent_duration_days must not exceed 3650 (10 years)")
        return v


class ConsentGrantResponse(BaseModel):
    id: str
    bank_account_id: str
    consent_status: Literal["granted"]
    granted_at: datetime
    expires_at: datetime | None = None


class ConsentRevokeRequest(BaseModel):
    bank_account_id: str


class ConsentRevokeResponse(BaseModel):
    id: str
    consent_status: Literal["revoked"]
    revoked_at: datetime


class ConsentStatusResponse(BaseModel):
    id: str = ""
    bank_account_id: str
    consent_status: Literal["granted", "revoked", "expired", "not_found"]
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
