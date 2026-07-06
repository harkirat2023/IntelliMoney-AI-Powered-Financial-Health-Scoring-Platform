from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


ALLOWED_PROVIDERS = {"mock", "setu", "finvu", "onemoney", "perfios"}


class BankConnectRequest(BaseModel):
    provider: str
    consent_version: str = "1.0"

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v not in ALLOWED_PROVIDERS:
            raise ValueError(f"Invalid provider '{v}'. Allowed: {', '.join(sorted(ALLOWED_PROVIDERS))}")
        return v


class ConsentSubmitRequest(BaseModel):
    provider: str
    consent_handle: str
    consent_token: str
    account_ids: list[str] = []
    consent_expiry: datetime | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v not in ALLOWED_PROVIDERS:
            raise ValueError(f"Invalid provider '{v}'. Allowed: {', '.join(sorted(ALLOWED_PROVIDERS))}")
        return v


class BankAccountPublic(BaseModel):
    id: str
    provider: str
    bank_name: str
    masked_account_number: str
    account_type: str
    connection_status: Literal["active", "expired", "revoked", "error"]
    consent_status: Literal["pending", "active", "expired", "revoked", "denied"]
    consent_expiry: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConnectInitResponse(BaseModel):
    consent_url: str
    consent_handle: str
    expires_at: datetime


class BankStatusResponse(BaseModel):
    total_accounts: int
    active_accounts: int
    providers_connected: list[str]
    last_sync: datetime | None = None
