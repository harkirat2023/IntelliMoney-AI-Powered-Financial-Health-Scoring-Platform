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
    from app.infrastructure.storage.local import LocalStorage
    return LocalStorage(settings.upload_dir)
