from abc import ABC, abstractmethod

from app.domain.import_preferences.models import ImportPreference


class ImportPreferenceRepository(ABC):
    @abstractmethod
    async def upsert(self, pref: ImportPreference) -> ImportPreference: ...

    @abstractmethod
    async def get_by_account(self, user_id: str, bank_account_id: str) -> ImportPreference | None: ...

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[ImportPreference]: ...
