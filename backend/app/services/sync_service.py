from asyncio import wait_for
from datetime import datetime, timedelta

from app.core.encryption import FieldEncryptor
from app.core.exceptions import (
    BankConnectionException,
    ConsentNotGrantedException,
    ForbiddenException,
    NotFoundException,
    SyncInProgressException,
    SyncRetryLimitExceededException,
)
from app.core.logging import logger
from app.domain.bank_accounts.repository import BankAccountRepository
from app.domain.consents.repository import ConsentRepository
from app.domain.import_preferences.repository import ImportPreferenceRepository
from app.domain.sync.models import BankTransaction, SyncLog
from app.domain.sync.repository import BankTransactionRepository, SyncLogRepository
from app.infrastructure.bank_integration.consent_manager import BankProviderRegistry
from app.schemas.sync import (
    SyncHistoryResponse,
    SyncLogDetail,
    SyncLogSummary,
    SyncManualResponse,
    SyncRetryResponse,
    SyncStartResponse,
    SyncStatusResponse,
)
from app.utils.date_utils import utc_now

FETCH_TRANSACTIONS_TIMEOUT = 120


class SyncService:
    def __init__(
        self,
        bank_repo: BankAccountRepository,
        consent_repo: ConsentRepository,
        pref_repo: ImportPreferenceRepository,
        tx_repo: BankTransactionRepository,
        sync_log_repo: SyncLogRepository,
        adapter_registry: BankProviderRegistry,
    ):
        self._bank_repo = bank_repo
        self._consent_repo = consent_repo
        self._pref_repo = pref_repo
        self._tx_repo = tx_repo
        self._sync_log_repo = sync_log_repo
        self._adapter_registry = adapter_registry
        self._encryptor = FieldEncryptor()

    async def start_sync(self, user_id: str, bank_account_id: str) -> SyncStartResponse:
        account = await self._bank_repo.get_by_id(bank_account_id)
        if not account:
            raise NotFoundException("Bank account not found")
        if str(account.user_id) != user_id:
            raise ForbiddenException("You do not own this bank account")

        latest = await self._sync_log_repo.get_latest_by_account(user_id, bank_account_id)
        if latest and latest.status == "running":
            raise SyncInProgressException()

        sync_log = SyncLog(
            user_id=user_id,
            bank_account_id=bank_account_id,
            sync_type="manual",
            created_at=utc_now(),
        )
        created = await self._sync_log_repo.create(sync_log)
        logger.info("Sync started", extra={"sync_log_id": created.id, "bank_account_id": bank_account_id, "user_id": user_id})

        await self._execute_sync(created.id, user_id, bank_account_id)

        return SyncStartResponse(
            sync_log_id=created.id,
            status="completed",
            message="Sync completed successfully",
        )

    async def manual_sync_all(self, user_id: str) -> SyncManualResponse:
        accounts = await self._bank_repo.get_active_by_user_id(user_id)
        logger.info("Manual sync all triggered", extra={"user_id": user_id, "account_count": len(accounts)})
        results = []
        for acc in accounts:
            try:
                result = await self.start_sync(user_id, acc.id)
                results.append(result)
            except SyncInProgressException:
                results.append(SyncStartResponse(
                    sync_log_id="",
                    status="skipped",
                    message="Sync already in progress",
                ))
            except Exception as e:
                results.append(SyncStartResponse(
                    sync_log_id="",
                    status="failed",
                    message=str(e),
                ))
        return SyncManualResponse(results=results)

    async def get_status(self, user_id: str, bank_account_id: str | None = None) -> list[SyncStatusResponse]:
        if bank_account_id:
            accounts = [await self._bank_repo.get_by_id(bank_account_id)]
            if not accounts[0] or str(accounts[0].user_id) != user_id:
                raise NotFoundException("Bank account not found")
        else:
            accounts = await self._bank_repo.get_active_by_user_id(user_id)

        result = []
        for acc in accounts:
            latest = await self._sync_log_repo.get_latest_by_account(user_id, acc.id)
            sync_status = "never"
            latest_summary = None
            if latest:
                sync_status = latest.status
                latest_summary = SyncLogSummary(
                    id=latest.id,
                    status=latest.status,
                    sync_type=latest.sync_type,
                    transactions_imported=latest.transactions_imported,
                    started_at=latest.started_at,
                    completed_at=latest.completed_at,
                    error_message=latest.error_message,
                )

            result.append(SyncStatusResponse(
                bank_account_id=acc.id,
                bank_name=acc.bank_name,
                masked_account_number=acc.masked_account_number,
                last_synced_at=acc.last_synced_at,
                sync_status=sync_status,
                latest_sync=latest_summary,
            ))
        return result

    async def get_history(
        self, user_id: str, bank_account_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> SyncHistoryResponse:
        if bank_account_id:
            logs = await self._sync_log_repo.get_by_account(user_id, bank_account_id, limit, offset)
            total = await self._sync_log_repo.count_by_account(user_id, bank_account_id)
        else:
            logs = await self._sync_log_repo.get_by_user(user_id, limit, offset)
            total = await self._sync_log_repo.count_by_user(user_id)

        items = [
            SyncLogDetail(
                id=log.id,
                bank_account_id=log.bank_account_id,
                sync_type=log.sync_type,
                status=log.status,
                started_at=log.started_at,
                completed_at=log.completed_at,
                transactions_fetched=log.transactions_fetched,
                transactions_imported=log.transactions_imported,
                transactions_skipped=log.transactions_skipped,
                error_message=log.error_message,
                error_category=log.error_category,
                retry_count=log.retry_count,
                created_at=log.created_at,
            )
            for log in logs
        ]

        return SyncHistoryResponse(items=items, total=total, limit=limit, offset=offset)

    async def retry_sync(self, user_id: str, sync_log_id: str) -> SyncRetryResponse:
        existing = await self._sync_log_repo.get_by_id(sync_log_id)
        if not existing:
            raise NotFoundException("Sync log not found")
        if str(existing.user_id) != user_id:
            raise ForbiddenException("You do not own this sync log")
        if not existing.can_retry():
            raise SyncRetryLimitExceededException()

        remaining_retries = existing.max_retries - existing.retry_count - 1
        if remaining_retries < 0:
            raise SyncRetryLimitExceededException()

        sync_log = SyncLog(
            user_id=user_id,
            bank_account_id=existing.bank_account_id,
            sync_type="retry",
            retry_count=existing.retry_count + 1,
            max_retries=existing.max_retries,
            created_at=utc_now(),
        )
        created = await self._sync_log_repo.create(sync_log)
        logger.info("Sync retry started", extra={
            "sync_log_id": created.id, "original_id": sync_log_id,
            "retry_count": sync_log.retry_count, "bank_account_id": existing.bank_account_id,
        })

        await self._execute_sync(created.id, user_id, existing.bank_account_id)

        return SyncRetryResponse(
            sync_log_id=created.id,
            status="completed",
            message="Retry sync completed successfully",
        )

    async def _execute_sync(self, sync_log_id: str, user_id: str, bank_account_id: str) -> None:
        log = await self._sync_log_repo.get_by_id(sync_log_id)
        if not log:
            logger.warning("Sync log not found for execution", extra={"sync_log_id": sync_log_id})
            return

        running = await self._sync_log_repo.get_latest_by_account(user_id, bank_account_id)
        if running and running.id != sync_log_id and running.status == "running":
            logger.warning("Concurrent sync detected, aborting", extra={
                "sync_log_id": sync_log_id, "running_id": running.id,
            })
            log.mark_failed("Another sync is already running", "network_error")
            await self._sync_log_repo.update_status(
                log.id, "failed",
                completed_at=log.completed_at,
                error_message=log.error_message,
                error_category=log.error_category,
            )
            return

        try:
            log.mark_running()
            await self._sync_log_repo.update_status(
                log.id, "running",
                started_at=log.started_at,
            )

            account = await self._bank_repo.get_by_id(bank_account_id)
            if not account:
                raise NotFoundException("Bank account not found during sync")

            consent = await self._consent_repo.get_active_by_account(
                str(account.user_id), bank_account_id
            )
            if not consent or not consent.is_active():
                logger.warning("Consent not active for sync", extra={
                    "sync_log_id": sync_log_id, "bank_account_id": bank_account_id,
                })
                raise ConsentNotGrantedException()

            pref = await self._pref_repo.get_by_account(user_id, bank_account_id)
            from_date, to_date = pref.get_sync_range() if pref else (None, utc_now())
            if from_date is None:
                from_date = utc_now() - timedelta(days=730)

            adapter = self._adapter_registry.get(account.provider)

            decrypted_token = self._encryptor.decrypt(account.consent_token)
            decrypted_account_id = self._encryptor.decrypt(account.provider_account_id)

            logger.info("Fetching transactions from provider", extra={
                "sync_log_id": sync_log_id, "provider": account.provider,
                "from_date": from_date.isoformat(), "to_date": to_date.isoformat(),
            })

            provider_txs = await wait_for(
                adapter.fetch_transactions(
                    consent_handle=account.consent_handle,
                    consent_token=decrypted_token,
                    account_id=decrypted_account_id,
                    from_date=from_date,
                    to_date=to_date,
                ),
                timeout=FETCH_TRANSACTIONS_TIMEOUT,
            )

            bank_txs = [
                BankTransaction(
                    user_id=user_id,
                    bank_account_id=bank_account_id,
                    sync_log_id=sync_log_id,
                    provider_account_id=account.provider_account_id,
                    transaction_id=ptx.transaction_id,
                    description=ptx.description,
                    amount=ptx.amount,
                    transaction_type=ptx.transaction_type,
                    transaction_date=ptx.transaction_date,
                    category=ptx.category,
                    reference=ptx.reference,
                    created_at=utc_now(),
                )
                for ptx in provider_txs
            ]

            imported = await self._tx_repo.bulk_create(bank_txs)
            fetched = len(provider_txs)
            skipped = fetched - imported

            await self._bank_repo.update_last_synced(bank_account_id, utc_now())

            log.mark_completed(fetched, imported, skipped)
            await self._sync_log_repo.update_status(
                log.id, "completed",
                completed_at=log.completed_at,
                transactions_fetched=fetched,
                transactions_imported=imported,
                transactions_skipped=skipped,
            )
            logger.info("Sync completed", extra={
                "sync_log_id": sync_log_id, "fetched": fetched,
                "imported": imported, "skipped": skipped,
            })

        except ConsentNotGrantedException:
            log.mark_failed("Active consent not found for this account", "consent_expired")
            await self._sync_log_repo.update_status(
                log.id, "failed",
                completed_at=log.completed_at,
                error_message=log.error_message,
                error_category=log.error_category,
            )
            logger.warning("Sync failed: consent not granted", extra={"sync_log_id": sync_log_id})
        except BankConnectionException as e:
            log.mark_failed(str(e), "provider_error")
            await self._sync_log_repo.update_status(
                log.id, "failed",
                completed_at=log.completed_at,
                error_message=log.error_message,
                error_category=log.error_category,
            )
            logger.warning("Sync failed: provider error", extra={"sync_log_id": sync_log_id, "error": str(e)})
        except Exception as e:
            log.mark_failed(str(e), "network_error")
            await self._sync_log_repo.update_status(
                log.id, "failed",
                completed_at=log.completed_at,
                error_message=log.error_message,
                error_category=log.error_category,
            )
            logger.error("Sync failed", extra={"sync_log_id": sync_log_id, "error": str(e)})
