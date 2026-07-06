from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.sync.models import BankTransaction, SyncLog


class BankTransactionRepository(ABC):
    @abstractmethod
    async def create(self, tx: BankTransaction) -> BankTransaction: ...

    @abstractmethod
    async def bulk_create(self, txs: list[BankTransaction]) -> int: ...

    @abstractmethod
    async def find_by_account(
        self, user_id: str, bank_account_id: str, limit: int = 50, offset: int = 0
    ) -> list[BankTransaction]: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[BankTransaction]: ...

    @abstractmethod
    async def find_by_date_range(
        self, user_id: str, bank_account_id: str, from_date: datetime, to_date: datetime
    ) -> list[BankTransaction]: ...

    @abstractmethod
    async def count_by_account(self, user_id: str, bank_account_id: str) -> int: ...

    @abstractmethod
    async def exists_by_provider_id(self, provider_account_id: str, transaction_id: str) -> bool: ...


class SyncLogRepository(ABC):
    @abstractmethod
    async def create(self, log: SyncLog) -> SyncLog: ...

    @abstractmethod
    async def get_by_id(self, log_id: str) -> SyncLog | None: ...

    @abstractmethod
    async def get_latest_by_account(self, user_id: str, bank_account_id: str) -> SyncLog | None: ...

    @abstractmethod
    async def get_by_account(
        self, user_id: str, bank_account_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncLog]: ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncLog]: ...

    @abstractmethod
    async def update_status(
        self, log_id: str, status: str, **kwargs
    ) -> SyncLog | None: ...

    @abstractmethod
    async def count_by_account(self, user_id: str, bank_account_id: str) -> int: ...

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int: ...
