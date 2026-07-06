from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.domain.bank_accounts.repository import BankAccountRepository
from app.infrastructure.bank_integration.consent_manager import ConsentManager
from app.infrastructure.bank_integration.dtos import ConsentInitResponse
from app.schemas.bank import BankAccountPublic, BankStatusResponse, ConsentSubmitRequest


def _to_public(account) -> BankAccountPublic:
    return BankAccountPublic(
        id=account.id,
        provider=account.provider,
        bank_name=account.bank_name,
        masked_account_number=account.masked_account_number,
        account_type=account.account_type,
        connection_status=account.connection_status,
        consent_status=account.consent_status,
        consent_expiry=account.consent_expiry,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


class BankService:
    def __init__(self, consent_manager: ConsentManager, repo: BankAccountRepository):
        self._consent_manager = consent_manager
        self._repo = repo

    async def initiate_connection(self, user_id: str, provider: str) -> ConsentInitResponse:
        settings = get_settings()
        redirect_url = f"{settings.bank_consent_redirect_base}?provider={provider}&state={user_id}"
        return await self._consent_manager.create_consent(user_id, provider, redirect_url)

    async def complete_consent(self, user_id: str, req: ConsentSubmitRequest) -> list[BankAccountPublic]:
        accounts = await self._consent_manager.finalize_consent(
            user_id=user_id,
            provider=req.provider,
            consent_handle=req.consent_handle,
            consent_token=req.consent_token,
            account_ids=req.account_ids,
            expires_at=req.consent_expiry,
        )
        return [_to_public(a) for a in accounts]

    async def list_accounts(self, user_id: str) -> list[BankAccountPublic]:
        accounts = await self._repo.get_by_user_id(user_id)
        return [_to_public(a) for a in accounts]

    async def get_status(self, user_id: str) -> BankStatusResponse:
        all_accounts = await self._repo.get_by_user_id(user_id)
        active_accounts = [a for a in all_accounts if a.connection_status == "active"]
        providers = list({a.provider for a in active_accounts})
        last_sync = max((a.last_synced_at for a in all_accounts if a.last_synced_at), default=None)
        return BankStatusResponse(
            total_accounts=len(all_accounts),
            active_accounts=len(active_accounts),
            providers_connected=providers,
            last_sync=last_sync,
        )

    async def disconnect(self, user_id: str, account_id: str) -> None:
        account = await self._repo.get_by_id(account_id)
        if not account:
            raise NotFoundException("Bank account not found")
        if str(account.user_id) != user_id:
            raise ForbiddenException("You do not own this bank account")
        await self._consent_manager.revoke_consent(account_id)
