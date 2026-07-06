from datetime import datetime, timezone

from app.core.encryption import FieldEncryptor
from app.core.exceptions import ConsentDeniedException, ConsentExpiredException
from app.domain.bank_accounts.models import BankAccount
from app.domain.bank_accounts.repository import BankAccountRepository
from app.domain.consents.repository import ConsentRepository
from app.infrastructure.bank_integration import BankProviderAdapter
from app.infrastructure.bank_integration.dtos import ConsentInitResponse
from app.utils.date_utils import utc_now


class BankProviderRegistry:
    def __init__(self):
        self._adapters: dict[str, BankProviderAdapter] = {}

    def register(self, name: str, adapter: BankProviderAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> BankProviderAdapter:
        adapter = self._adapters.get(name)
        if not adapter:
            from app.core.exceptions import ProviderNotFoundException
            raise ProviderNotFoundException(name)
        return adapter

    def list_providers(self) -> list[str]:
        return list(self._adapters.keys())


class ConsentManager:
    def __init__(self, registry: BankProviderRegistry, repo: BankAccountRepository, consent_repo: ConsentRepository | None = None):
        self._registry = registry
        self._repo = repo
        self._consent_repo = consent_repo
        self._encryptor = FieldEncryptor()

    async def create_consent(self, user_id: str, provider: str, redirect_url: str) -> ConsentInitResponse:
        adapter = self._registry.get(provider)
        return await adapter.initiate_consent(user_id, "1.0", redirect_url)

    async def finalize_consent(
        self,
        user_id: str,
        provider: str,
        consent_handle: str,
        consent_token: str,
        account_ids: list[str],
        expires_at: datetime | None = None,
    ) -> list[BankAccount]:
        adapter = self._registry.get(provider)
        status = await adapter.check_consent_status(consent_handle)
        if status.status == "EXPIRED":
            raise ConsentExpiredException()
        if status.status != "ACTIVE":
            raise ConsentDeniedException()

        provider_accounts = await adapter.fetch_accounts(consent_handle, status.consent_token or consent_token)
        persisted = []
        now = utc_now()

        for acc in provider_accounts:
            if account_ids and acc.provider_account_id not in account_ids:
                continue
            encrypted_account_id = self._encryptor.encrypt(acc.provider_account_id)
            encrypted_token = self._encryptor.encrypt(status.consent_token or consent_token)

            bank_account = BankAccount(
                user_id=user_id,
                provider=provider,
                consent_handle=consent_handle,
                provider_account_id=encrypted_account_id,
                bank_name=acc.bank_name,
                masked_account_number=acc.masked_account_number,
                account_type=acc.account_type,
                account_holder_name=acc.account_holder_name,
                ifsc_code=acc.ifsc_code,
                connection_status="active",
                consent_status="active",
                consent_token=encrypted_token,
                consent_version="1.0",
                consent_expiry=expires_at or now.replace(year=now.year + 1),
                created_at=now,
                updated_at=now,
            )
            persisted.append(await self._repo.create(bank_account))
        return persisted

    async def revoke_consent(self, account_id: str) -> None:
        account = await self._repo.get_by_id(account_id)
        if not account:
            return
        adapter = self._registry.get(account.provider)
        await adapter.revoke_consent(account.consent_handle)
        await self._repo.update_consent_status(account_id, "revoked")
        if self._consent_repo:
            consent = await self._consent_repo.get_active_by_account(str(account.user_id), account_id)
            if consent and consent.consent_status == "granted":
                consent.revoke()
                await self._consent_repo.update_status(consent.id, "revoked", consent.revoked_at)

    async def get_active_accounts(self, user_id: str) -> list[BankAccount]:
        return await self._repo.get_active_by_user_id(user_id)

    async def check_expired_consents(self) -> int:
        accounts = await self._repo.get_all_active()
        now = utc_now()
        count = 0
        for acc in accounts:
            if acc.consent_expiry and acc.consent_expiry < now:
                await self._repo.update_consent_status(acc.id, "expired")
                count += 1
        return count
