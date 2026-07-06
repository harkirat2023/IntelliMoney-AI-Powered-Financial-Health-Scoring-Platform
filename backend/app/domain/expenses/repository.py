from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.expenses.models import Expense


class ExpenseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, expense_id: str) -> Expense | None:
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, category: str | None = None,
        payment_method: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Expense]:
        ...

    @abstractmethod
    async def create(self, expense: Expense) -> Expense:
        ...

    @abstractmethod
    async def update(self, expense_id: str, data: dict) -> Expense | None:
        ...

    @abstractmethod
    async def delete(self, expense_id: str) -> bool:
        ...
