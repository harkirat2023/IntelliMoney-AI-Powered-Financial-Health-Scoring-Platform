from typing import Any

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.infrastructure.bank_integration import MockBankProvider
from app.infrastructure.bank_integration.consent_manager import BankProviderRegistry
from app.infrastructure.database.repositories.bank_repository import MongoBankAccountRepository
from app.infrastructure.database.repositories.consent_repository import MongoConsentRepository
from app.infrastructure.database.repositories.import_preference_repository import MongoImportPreferenceRepository
from app.infrastructure.database.repositories.sync_repository import (
    MongoBankTransactionRepository,
    MongoSyncLogRepository,
)
from app.schemas.sync import (
    SyncHistoryResponse,
    SyncManualResponse,
    SyncRetryRequest,
    SyncRetryResponse,
    SyncStartRequest,
    SyncStartResponse,
    SyncStatusResponse,
)
from app.services.sync_service import SyncService


router = APIRouter(prefix="/sync", tags=["sync"])


def _get_sync_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> SyncService:
    registry = BankProviderRegistry()
    registry.register("mock", MockBankProvider())
    bank_repo = MongoBankAccountRepository(db)
    consent_repo = MongoConsentRepository(db)
    pref_repo = MongoImportPreferenceRepository(db)
    tx_repo = MongoBankTransactionRepository(db)
    sync_log_repo = MongoSyncLogRepository(db)
    return SyncService(bank_repo, consent_repo, pref_repo, tx_repo, sync_log_repo, registry)


@router.post("/start", response_model=SyncStartResponse)
async def start_sync(
    req: SyncStartRequest,
    user: dict = Depends(get_current_user),
    service: SyncService = Depends(_get_sync_service),
) -> Any:
    return await service.start_sync(str(user["_id"]), req.bank_account_id)


@router.post("/manual", response_model=SyncManualResponse)
async def manual_sync(
    user: dict = Depends(get_current_user),
    service: SyncService = Depends(_get_sync_service),
) -> Any:
    return await service.manual_sync_all(str(user["_id"]))


@router.get("/status", response_model=list[SyncStatusResponse])
async def sync_status(
    bank_account_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    service: SyncService = Depends(_get_sync_service),
) -> Any:
    return await service.get_status(str(user["_id"]), bank_account_id)


@router.get("/history", response_model=SyncHistoryResponse)
async def sync_history(
    bank_account_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    service: SyncService = Depends(_get_sync_service),
) -> Any:
    return await service.get_history(str(user["_id"]), bank_account_id, limit, offset)


@router.post("/retry", response_model=SyncRetryResponse)
async def retry_sync(
    req: SyncRetryRequest,
    user: dict = Depends(get_current_user),
    service: SyncService = Depends(_get_sync_service),
) -> Any:
    return await service.retry_sync(str(user["_id"]), req.sync_log_id)
