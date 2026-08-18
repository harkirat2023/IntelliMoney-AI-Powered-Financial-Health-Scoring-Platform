"""Authentication/security helpers.

IntelliMoney uses Clerk as its ONLY authentication and identity provider.

There is intentionally no custom JWT generation, no password hashing and
no local login credential storage in this module or anywhere in the
application. ``hash_password`` / ``verify_password`` were removed with the
legacy password authentication system.
"""

from __future__ import annotations

from typing import Any

from app.core.clerk import ClerkError, verify_clerk_token
from app.core.logging import logger


async def validate_bearer_token(token: str) -> dict[str, Any] | None:
    """Verify a Clerk session token and return its claims.

    Returns ``None`` when the token is missing or cannot be verified so
    callers can raise the appropriate HTTP/websocket rejection.
    """
    if not token:
        return None
    try:
        return await verify_clerk_token(token)
    except ClerkError as exc:
        logger.warning("Clerk token verification failed: %s", exc)
        return None