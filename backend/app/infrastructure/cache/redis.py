from typing import Any

from app.core.config import get_settings


class CacheClient:
    def __init__(self) -> None:
        self._client = None

    async def connect(self) -> None:
        settings = get_settings()
        if hasattr(settings, "redis_url") and settings.redis_url:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.from_url(
                    settings.redis_url, decode_responses=True
                )
            except ImportError:
                pass

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        value = await self._client.get(key)
        if value is not None and hasattr(value, "decode"):
            value = value.decode("utf-8")
        return value

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        if not self._client:
            return
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        if not self._client:
            return
        await self._client.delete(key)

    async def increment(self, key: str) -> None:
        if not self._client:
            return
        await self._client.incr(key)


cache_client = CacheClient()
