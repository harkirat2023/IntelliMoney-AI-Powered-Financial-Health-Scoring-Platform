from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.financial_transactions.models import FinancialTransaction


class FinancialTransactionRepository(ABC):
    @abstractmethod
    async def create(self, tx: FinancialTransaction) -> FinancialTransaction: ...

    @abstractmethod
    async def bulk_create(self, txs: list[FinancialTransaction]) -> int: ...

    @abstractmethod
    async def get_by_id(self, tx_id: str) -> FinancialTransaction | None: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[FinancialTransaction]: ...

    @abstractmethod
    async def find_by_user_and_category(
        self, user_id: str, category: str, limit: int = 50, offset: int = 0
    ) -> list[FinancialTransaction]: ...

    @abstractmethod
    async def find_by_review_status(
        self, user_id: str, status: str, limit: int = 20, offset: int = 0
    ) -> list[FinancialTransaction]: ...

    @abstractmethod
    async def find_by_date_range(
        self, user_id: str, from_date: datetime, to_date: datetime
    ) -> list[FinancialTransaction]: ...

    @abstractmethod
    async def find_unprocessed_bank_tx_ids(
        self, user_id: str, bank_tx_ids: list[str]
    ) -> list[str]: ...

    @abstractmethod
    async def update_fields(
        self, tx_id: str, update_data: dict,
    ) -> FinancialTransaction | None: ...

    @abstractmethod
    async def atomic_claim(self, tx_id: str) -> FinancialTransaction | None:
        """Atomically claim a tx for processing. Returns None if already claimed."""

    @abstractmethod
    async def atomic_review_update(
        self, tx_id: str, expected_review_status: str,
        review_status: str, reviewed_by: str, reviewed_at: datetime,
        review_note: str | None = None,
        assigned_category: str | None = None,
    ) -> FinancialTransaction | None: ...

    @abstractmethod
    async def find_unprocessed(
        self, user_id: str, limit: int = 100,
    ) -> list[FinancialTransaction]: ...

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int: ...

    @abstractmethod
    async def count_by_review_status(self, user_id: str, status: str) -> int: ...
