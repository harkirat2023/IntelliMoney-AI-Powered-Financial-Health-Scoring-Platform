from abc import ABC, abstractmethod
from datetime import datetime

from app.infrastructure.bank_integration.dtos import (
    ConsentInitResponse,
    ConsentStatusResponse,
    ProviderAccount,
    ProviderTransaction,
)


class BankProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def initiate_consent(self, user_id: str, consent_version: str, redirect_url: str) -> ConsentInitResponse: ...

    @abstractmethod
    async def check_consent_status(self, consent_handle: str) -> ConsentStatusResponse: ...

    @abstractmethod
    async def fetch_accounts(self, consent_handle: str, consent_token: str) -> list[ProviderAccount]: ...

    @abstractmethod
    async def fetch_transactions(self, consent_handle: str, consent_token: str, account_id: str, from_date: datetime, to_date: datetime) -> list[ProviderTransaction]: ...

    @abstractmethod
    async def revoke_consent(self, consent_handle: str) -> bool: ...
