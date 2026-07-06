from app.core.exceptions import ForbiddenException, ImportPreferenceNotFoundException, NotFoundException
from app.domain.bank_accounts.repository import BankAccountRepository
from app.domain.import_preferences.models import ImportPreference
from app.domain.import_preferences.repository import ImportPreferenceRepository
from app.schemas.import_preference import ImportPreferenceRequest, ImportPreferenceResponse
from app.utils.date_utils import utc_now


class ImportPreferenceService:
    def __init__(self, pref_repo: ImportPreferenceRepository, bank_repo: BankAccountRepository | None = None):
        self._pref_repo = pref_repo
        self._bank_repo = bank_repo

    async def save(self, user_id: str, req: ImportPreferenceRequest) -> ImportPreferenceResponse:
        if self._bank_repo:
            account = await self._bank_repo.get_by_id(req.bank_account_id)
            if not account:
                raise NotFoundException("Bank account not found")
            if str(account.user_id) != user_id:
                raise ForbiddenException("You do not own this bank account")
        now = utc_now()
        pref = ImportPreference(
            user_id=user_id,
            bank_account_id=req.bank_account_id,
            import_type=req.import_type,
            import_start_date=req.import_start_date,
            created_at=now,
            updated_at=now,
        )
        saved = await self._pref_repo.upsert(pref)
        return ImportPreferenceResponse(
            id=saved.id,
            bank_account_id=saved.bank_account_id,
            import_type=saved.import_type,
            import_start_date=saved.import_start_date,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def get(self, user_id: str, bank_account_id: str) -> ImportPreferenceResponse:
        pref = await self._pref_repo.get_by_account(user_id, bank_account_id)
        if not pref:
            raise ImportPreferenceNotFoundException()
        return ImportPreferenceResponse(
            id=pref.id,
            bank_account_id=pref.bank_account_id,
            import_type=pref.import_type,
            import_start_date=pref.import_start_date,
            created_at=pref.created_at,
            updated_at=pref.updated_at,
        )
