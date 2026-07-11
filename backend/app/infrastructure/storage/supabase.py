import hashlib

from supabase import create_client

from app.infrastructure.storage import StorageBackend


class SupabaseStorage(StorageBackend):
    def __init__(self, supabase_url: str, service_key: str, bucket: str) -> None:
        self._client = create_client(supabase_url, service_key)
        self._bucket = bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        buckets = [b.name for b in self._client.storage.list_buckets()]
        if self._bucket not in buckets:
            self._client.storage.create_bucket(self._bucket, public=True)

    async def save(self, path: str, data: bytes) -> str:
        content_type = "image/jpeg"
        if path.lower().endswith(".png"):
            content_type = "image/png"
        elif path.lower().endswith(".webp"):
            content_type = "image/webp"
        self._client.storage.from_(self._bucket).upload(
            path, data, {"content-type": content_type}
        )
        public_url = self._client.storage.from_(self._bucket).get_public_url(path)
        return public_url

    async def read(self, path: str) -> bytes | None:
        try:
            resp = self._client.storage.from_(self._bucket).download(path)
            return resp
        except Exception:
            return None

    async def delete(self, path: str) -> bool:
        try:
            self._client.storage.from_(self._bucket).remove([path])
            return True
        except Exception:
            return False

    async def exists(self, path: str) -> bool:
        try:
            resp = self._client.storage.from_(self._bucket).download(path)
            return resp is not None
        except Exception:
            return False

    def get_url(self, path: str) -> str:
        return self._client.storage.from_(self._bucket).get_public_url(path)
