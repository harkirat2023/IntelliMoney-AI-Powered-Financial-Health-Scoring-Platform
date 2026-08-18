"""Clerk authentication for IntelliMoney.

Clerk is the ONLY authentication and identity provider.

Session tokens issued by Clerk are signed JSON Web Tokens. Their public
signing keys are published at:

    https://<CLERK_FRONTEND_API>/.well-known/jwks.json

This module verifies a Clerk session token, extracts the authenticated
Clerk user identity, and keeps a lightweight local user profile in
MongoDB that references the Clerk identity (``clerk_user_id``).

There is intentionally no custom JWT generation, no password hashing and
no local login credential storage anywhere in IntelliMoney.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import get_settings
from app.core.logging import logger

_JWKS_TTL_SECONDS = 3600


class ClerkError(Exception):
    """Raised when a Clerk session token cannot be verified."""


class ClerkVerifier:
    """Verifies Clerk session tokens using Clerk's published JWKS."""

    def __init__(self) -> None:
        settings = get_settings()
        self._frontend_api = (settings.clerk_frontend_api or "").strip().rstrip("/")
        self._publishable_key = (settings.clerk_publishable_key or "").strip()
        self._jwks: list[dict[str, Any]] | None = None
        self._jwks_fetched_at: float = 0.0

    @property
    def configured(self) -> bool:
        return bool(self._frontend_api)

    @property
    def app_id(self) -> str | None:
        """Derive the Clerk application ID from the publishable key.

        Publishable keys look like ``pk_test_<application_id>`` or
        ``pk_live_<application_id>``. The token's ``azp`` claim must match
        this value when it is available.
        """
        if not self._publishable_key:
            return None
        for prefix in ("pk_test_", "pk_live_"):
            if self._publishable_key.startswith(prefix):
                return self._publishable_key[len(prefix):]
        return None

    async def _load_jwks(self) -> None:
        if not self.configured:
            raise ClerkError("Clerk is not configured (CLERK_FRONTEND_API is empty)")
        now = time.time()
        if self._jwks and (now - self._jwks_fetched_at) < _JWKS_TTL_SECONDS:
            return
        url = f"https://{self._frontend_api}/.well-known/jwks.json"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # noqa: BLE001 - any network failure means no auth
            raise ClerkError(f"Failed to fetch Clerk JWKS: {exc}") from exc
        self._jwks = payload.get("keys", [])
        self._jwks_fetched_at = now
        if not self._jwks:
            raise ClerkError("Clerk JWKS response contained no signing keys")

    async def verify(self, token: str) -> dict[str, Any]:
        """Verify a Clerk session token and return its claims.

        Raises ``ClerkError`` when the token is invalid, expired or signed
        by an unexpected application.
        """
        if not token:
            raise ClerkError("Missing token")
        if not self.configured:
            raise ClerkError("Clerk is not configured (CLERK_FRONTEND_API is empty)")

        await self._load_jwks()

        try:
            unverified_headers = jwt.get_unverified_headers(token)
            kid = unverified_headers.get("kid")
            key = next((k for k in (self._jwks or []) if k.get("kid") == kid), None)
            if key is None:
                raise ClerkError("Clerk token signed with an unknown key")

            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={
                    "verify_aud": False,
                    "verify_sub": True,
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )
        except JWTError as exc:
            raise ClerkError(f"Invalid Clerk token: {exc}") from exc

        subject = claims.get("sub")
        if not subject:
            raise ClerkError("Clerk token has no subject")

        app_id = self.app_id
        if app_id and claims.get("azp") and claims.get("azp") != app_id:
            raise ClerkError("Clerk token issued for a different application")

        if not claims.get("sid"):
            raise ClerkError("Clerk token has no session id")

        return claims


_verifier = ClerkVerifier()


def get_verifier() -> ClerkVerifier:
    return _verifier


async def verify_clerk_token(token: str) -> dict[str, Any]:
    """Verify a Clerk session token and return its claims."""
    return await _verifier.verify(token)


async def upsert_clerk_user(db, claims: dict[str, Any]) -> dict[str, Any]:
    """Find or create the local user profile for an authenticated Clerk user.

    The user's ``clerk_user_id`` references the Clerk identity. The
    ``_id`` remains a Mongo ``ObjectId`` so that every existing
    user-owned financial record keeps working unchanged.
    """
    from bson import ObjectId

    from app.utils.date_utils import utc_now

    clerk_sub = claims["sub"]
    user = await db.users.find_one({"clerk_user_id": clerk_sub})
    if user:
        return user

    email = ""
    for ident in claims.get("claims", {}).get("email_addresses", []):
        email = ident.get("email_address", "")
        break
    if not email:
        email = claims.get("email") or ""

    first_name = claims.get("first_name") or ""
    last_name = claims.get("last_name") or ""
    name = " ".join(p for p in (first_name, last_name) if p).strip() or claims.get("name") or email or clerk_sub

    document = {
        "_id": ObjectId(),
        "clerk_user_id": clerk_sub,
        "name": name,
        "email": (email or "").lower(),
        "monthly_income": 0.0,
        "is_verified": True,
        "is_onboarded": False,
        "created_at": utc_now(),
        "auth_provider": "clerk",
    }
    try:
        result = await db.users.insert_one(document)
    except Exception:
        existing = await db.users.find_one({"clerk_user_id": clerk_sub})
        if existing:
            return existing
        raise
    document["_id"] = result.inserted_id
    logger.info("Created local user profile for Clerk user", extra={"clerk_user_id": clerk_sub})
    return document