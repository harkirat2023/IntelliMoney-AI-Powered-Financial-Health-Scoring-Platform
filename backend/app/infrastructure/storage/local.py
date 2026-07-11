import os
from pathlib import Path

from app.infrastructure.storage import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    async def save(self, path: str, data: bytes) -> str:
        full = self._base / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)
        return str(full)

    async def read(self, path: str) -> bytes | None:
        full = self._base / path
        if not full.exists():
            return None
        return full.read_bytes()

    async def delete(self, path: str) -> bool:
        full = self._base / path
        if not full.exists():
            return False
        full.unlink()
        return True

    async def exists(self, path: str) -> bool:
        return (self._base / path).exists()

    def get_url(self, path: str) -> str:
        return f"/api/v1/receipts/{Path(path).stem}/image"
