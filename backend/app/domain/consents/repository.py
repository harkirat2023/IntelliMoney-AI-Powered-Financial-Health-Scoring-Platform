from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.consents.models import ConsentGrant


class ConsentRepository(ABC):
    @abstractmethod
    async def create(self, consent: ConsentGrant) -> ConsentGrant: ...

    @abstractmethod
    async def get_by_id(self, consent_id: str) -> ConsentGrant | None: ...

    @abstractmethod
    async def get_active_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None: ...

    @abstractmethod
    async def get_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None: ...

    @abstractmethod
    async def update_status(self, consent_id: str, status: str, revoked_at: datetime | None = None) -> ConsentGrant | None: ...

    @abstractmethod
    async def get_all_expired(self) -> list[ConsentGrant]: ...
