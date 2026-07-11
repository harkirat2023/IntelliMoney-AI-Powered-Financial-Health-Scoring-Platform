import io
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, path: str, data: bytes) -> str:
        ...

    @abstractmethod
    async def read(self, path: str) -> bytes | None:
        ...

    @abstractmethod
    async def delete(self, path: str) -> bool:
        ...

    @abstractmethod
    async def exists(self, path: str) -> bool:
        ...

    @abstractmethod
    def get_url(self, path: str) -> str:
        ...


def get_storage_backend() -> StorageBackend:
    from app.core.config import get_settings
    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_key:
        from app.infrastructure.storage.supabase import SupabaseStorage
        return SupabaseStorage(settings.supabase_url, settings.supabase_service_key, "receipts")
    from app.infrastructure.storage.local import LocalStorage
    return LocalStorage(settings.upload_dir)
