from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.bank_accounts.models import BankAccount


class BankAccountRepository(ABC):
    @abstractmethod
    async def create(self, account: BankAccount) -> BankAccount: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[BankAccount]: ...

    @abstractmethod
    async def get_active_by_user_id(self, user_id: str) -> list[BankAccount]: ...

    @abstractmethod
    async def get_all_active(self) -> list[BankAccount]: ...

    @abstractmethod
    async def get_by_id(self, account_id: str) -> BankAccount | None: ...

    @abstractmethod
    async def get_by_consent_handle(self, consent_handle: str) -> BankAccount | None: ...

    @abstractmethod
    async def update_connection_status(self, account_id: str, status: str) -> BankAccount | None: ...

    @abstractmethod
    async def update_consent_status(self, account_id: str, status: str, expiry: datetime | None = None) -> BankAccount | None: ...

    @abstractmethod
    async def delete(self, account_id: str) -> bool: ...

    @abstractmethod
    async def count_active_by_user_id(self, user_id: str) -> int: ...

    @abstractmethod
    async def update_last_synced(self, account_id: str, synced_at: datetime) -> BankAccount | None: ...
