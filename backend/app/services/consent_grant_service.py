from datetime import timedelta

from app.core.exceptions import (
    BankAccountNotActiveException,
    ConsentAlreadyRevokedException,
    ConsentNotFoundException,
    ForbiddenException,
    NotFoundException,
)
from app.domain.bank_accounts.repository import BankAccountRepository
from app.domain.consents.models import ConsentGrant
from app.domain.consents.repository import ConsentRepository
from app.schemas.consent import (
    ConsentGrantRequest,
    ConsentGrantResponse,
    ConsentRevokeRequest,
    ConsentRevokeResponse,
    ConsentStatusResponse,
)
from app.utils.date_utils import utc_now


class ConsentGrantService:
    def __init__(self, consent_repo: ConsentRepository, bank_repo: BankAccountRepository):
        self._consent_repo = consent_repo
        self._bank_repo = bank_repo

    async def grant(self, user_id: str, req: ConsentGrantRequest) -> ConsentGrantResponse:
        account = await self._bank_repo.get_by_id(req.bank_account_id)
        if not account:
            raise NotFoundException("Bank account not found")
        if str(account.user_id) != user_id:
            raise ForbiddenException("You do not own this bank account")
        if account.connection_status != "active":
            raise BankAccountNotActiveException()
        if account.consent_status != "active":
            raise BankAccountNotActiveException()

        existing = await self._consent_repo.get_active_by_account(user_id, req.bank_account_id)
        if existing:
            return ConsentGrantResponse(
                id=existing.id,
                bank_account_id=existing.bank_account_id,
                consent_status="granted",
                granted_at=existing.granted_at,
                expires_at=existing.expires_at,
            )

        now = utc_now()
        consent = ConsentGrant(
            user_id=user_id,
            bank_account_id=req.bank_account_id,
            consent_version=req.consent_version,
            granted_at=now,
            expires_at=now + timedelta(days=req.consent_duration_days),
            created_at=now,
            updated_at=now,
        )
        created = await self._consent_repo.create(consent)
        return ConsentGrantResponse(
            id=created.id,
            bank_account_id=created.bank_account_id,
            consent_status="granted",
            granted_at=created.granted_at,
            expires_at=created.expires_at,
        )

    async def revoke(self, user_id: str, req: ConsentRevokeRequest) -> ConsentRevokeResponse:
        account = await self._bank_repo.get_by_id(req.bank_account_id)
        if not account:
            raise NotFoundException("Bank account not found")
        if str(account.user_id) != user_id:
            raise ForbiddenException("You do not own this bank account")

        consent = await self._consent_repo.get_by_account(user_id, req.bank_account_id)
        if not consent:
            raise ConsentNotFoundException()
        if consent.consent_status != "granted":
            raise ConsentAlreadyRevokedException()

        consent.revoke()
        updated = await self._consent_repo.update_status(consent.id, "revoked", consent.revoked_at)
        return ConsentRevokeResponse(
            id=updated.id,
            consent_status="revoked",
            revoked_at=consent.revoked_at,
        )

    async def get_status(self, user_id: str, bank_account_id: str) -> ConsentStatusResponse:
        consent = await self._consent_repo.get_by_account(user_id, bank_account_id)
        if not consent:
            return ConsentStatusResponse(
                bank_account_id=bank_account_id,
                consent_status="not_found",
            )

        if consent.consent_status == "granted":
            if consent.expires_at and consent.expires_at < utc_now():
                status = "expired"
            else:
                status = "granted"
        else:
            status = consent.consent_status

        return ConsentStatusResponse(
            id=consent.id,
            bank_account_id=consent.bank_account_id,
            consent_status=status,
            granted_at=consent.granted_at,
            expires_at=consent.expires_at,
            revoked_at=consent.revoked_at,
        )
