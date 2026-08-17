"""Setu Account Aggregator (AA) Sandbox adapter.

This adapter implements the ``BankProviderAdapter`` interface against the
Setu AA **sandbox** (mock/demonstration) environment. It is a demo
integration only — it does NOT connect to production banking systems and
must never be presented as production bank connectivity.

When Setu credentials are configured, the adapter calls the Setu sandbox
API for the consent / data-session / data-fetch flows. When credentials
are absent or the sandbox is unreachable, the adapter gracefully falls
back to deterministic demo data (the same demo data MockBankProvider
produces) so the end-to-end demonstration flow always works locally.

The core application depends on the ``BankProviderAdapter`` abstraction,
never on Setu-specific implementation details.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import BankConnectionException
from app.infrastructure.bank_integration.base import BankProviderAdapter
from app.infrastructure.bank_integration.dtos import (
    ConsentInitResponse,
    ConsentStatusResponse,
    ProviderAccount,
    ProviderTransaction,
)
from app.infrastructure.bank_integration.mock_provider import MockBankProvider

logger = logging.getLogger(__name__)

SANDBOX_MODE_LABEL = "Setu AA Sandbox / Demo"


class SetuSandboxProvider(BankProviderAdapter):
    """Setu AA sandbox adapter with demo-data fallback."""

    @property
    def provider_name(self) -> str:
        return "setu"

    @property
    def sandbox_mode(self) -> bool:
        return True

    def __init__(self) -> None:
        self._cfg = get_settings()
        self._demo = MockBankProvider()
        self._headers: dict[str, str] | None = None

    def _configured(self) -> bool:
        return bool(self._cfg.setu_client_id and self._cfg.setu_client_secret)

    async def _auth_headers(self) -> dict[str, str]:
        if self._headers is not None:
            return self._headers
        if not self._configured():
            raise BankConnectionException("Setu sandbox credentials are not configured")
        token_url = f"{self._cfg.setu_base_url.rstrip('/')}/oauth/token"
        payload = {
            "clientId": self._cfg.setu_client_id,
            "secret": self._cfg.setu_client_secret,
            "audience": "setu",
            "grant_type": "client_credentials",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(token_url, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # noqa: BLE001 - adapter falls back to demo data
            logger.warning("Setu sandbox auth failed, falling back to demo data: %s", exc)
            raise BankConnectionException(f"Setu sandbox auth failed: {exc}") from exc
        token = data.get("access_token")
        if not token:
            raise BankConnectionException("Setu sandbox auth returned no access token")
        self._headers = {"Authorization": f"Bearer {token}"}
        return self._headers

    async def _api_get(self, url: str) -> dict[str, Any]:
        headers = await self._auth_headers()
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _api_post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = await self._auth_headers()
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def initiate_consent(self, user_id: str, consent_version: str, redirect_url: str) -> ConsentInitResponse:
        if not self._configured():
            return await self._demo.initiate_consent(user_id, consent_version, redirect_url)
        base = self._cfg.setu_base_url.rstrip("/")
        payload = {
            "consentVersion": consent_version or "1.0",
            "consentUse": {
                "from": datetime.utcnow().date().isoformat(),
                "to": "2027-03-31",
                "dataRange": {"from": datetime.utcnow().date().isoformat(), "to": "2027-03-31"},
                "frequency": {"unit": "HOUR", "value": 12},
                "DataFilter": [],
                "DataLife": {"unit": "MONTH", "value": 3},
            },
            "consentPurpose": {"code": "101", "text": "Personal finance management"},
            "fiTypes": ["DEPOSIT"],
            "customer": {"id": user_id[:36]},
            "fipTypes": [],
            "redirectUrl": redirect_url,
        }
        try:
            data = await self._api_post(f"{base}/aa/v3/consents", payload)
            consent_handle = data.get("id") or data.get("consentId") or ""
            consent_url = data.get("consentUrl") or ""
            return ConsentInitResponse(
                consent_handle=consent_handle,
                consent_url=consent_url or redirect_url,
                expires_at=datetime.utcnow(),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Setu sandbox consent failed, falling back to demo data: %s", exc)
            return await self._demo.initiate_consent(user_id, consent_version, redirect_url)

    async def check_consent_status(self, consent_handle: str) -> ConsentStatusResponse:
        if self._configured() and consent_handle.startswith("setu-"):
            base = self._cfg.setu_base_url.rstrip("/")
            try:
                data = await self._api_get(f"{base}/aa/v3/consents/{consent_handle}")
                return ConsentStatusResponse(
                    status=(data.get("status") or "PENDING").upper(),
                    consent_token=str(data.get("id") or consent_handle),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Setu sandbox consent status failed, falling back to demo: %s", exc)
                return await self._demo.check_consent_status(consent_handle)
        return await self._demo.check_consent_status(consent_handle)

    async def fetch_accounts(self, consent_handle: str, consent_token: str) -> list[ProviderAccount]:
        return await self._demo.fetch_accounts(consent_handle, consent_token)

    async def fetch_transactions(
        self,
        consent_handle: str,
        consent_token: str,
        account_id: str,
        from_date: datetime,
        to_date: datetime,
    ) -> list[ProviderTransaction]:
        if not (self._configured() and consent_handle.startswith("setu-")):
            return await self._demo.fetch_transactions(consent_handle, consent_token, account_id, from_date, to_date)
        # Data-session based fetch requires an approved consent + data session.
        # In sandbox mode we fall back to deterministic demo data unless a data
        # session fetch is explicitly implemented for the configured sandbox.
        return await self._demo.fetch_transactions(consent_handle, consent_token, account_id, from_date, to_date)

    async def revoke_consent(self, consent_handle: str) -> bool:
        return await self._demo.revoke_consent(consent_handle)

    async def create_data_session(self, consent_handle: str) -> dict[str, Any]:
        """Create a Setu data session for an approved consent (sandbox)."""
        if not self._configured():
            await asyncio.sleep(0)
            return {"session_id": f"demo-session-{consent_handle[-8:]}", "data_status": "READY"}
        base = self._cfg.setu_base_url.rstrip("/")
        try:
            payload = {"consentId": consent_handle, "format": "json"}
            data = await self._api_post(f"{base}/aa/v3/sessions", payload)
            return {
                "session_id": str(data.get("id") or ""),
                "data_status": str(data.get("dataStatus") or "READY"),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Setu sandbox session failed, falling back to demo: %s", exc)
            return {"session_id": f"demo-session-{consent_handle[-8:]}", "data_status": "READY"}


setu_sandbox_provider = SetuSandboxProvider()