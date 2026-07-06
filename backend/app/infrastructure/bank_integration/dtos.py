from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ConsentInitResponse(BaseModel):
    consent_handle: str
    consent_url: str
    expires_at: datetime


class ConsentStatusResponse(BaseModel):
    status: Literal["ACTIVE", "EXPIRED", "REVOKED", "DENIED", "PENDING"]
    consent_token: str | None = None


class ProviderAccount(BaseModel):
    provider_account_id: str
    bank_name: str
    masked_account_number: str
    account_type: str
    account_holder_name: str
    ifsc_code: str


class ProviderTransaction(BaseModel):
    transaction_id: str
    description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    category: str | None = None
    reference: str | None = None
