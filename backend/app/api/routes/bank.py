from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.infrastructure.bank_integration import MockBankProvider
from app.infrastructure.bank_integration.consent_manager import BankProviderRegistry, ConsentManager
from app.infrastructure.bank_integration.setu_sandbox import setu_sandbox_provider
from app.infrastructure.database.repositories.bank_repository import MongoBankAccountRepository
from app.infrastructure.database.repositories.consent_repository import MongoConsentRepository
from app.infrastructure.database.repositories.import_preference_repository import MongoImportPreferenceRepository
from app.infrastructure.database.repositories.sync_repository import (
    MongoBankTransactionRepository,
    MongoSyncLogRepository,
)
from app.schemas.bank import BankAccountPublic, BankConnectRequest, BankImportRequest, BankImportResponse, BankStatusResponse, ConnectInitResponse, ConsentSubmitRequest
from app.services.auto_processing_service import AutoProcessingService
from app.services.bank_service import BankService
from app.services.consent_grant_service import ConsentGrantService
from app.services.sync_service import SyncService
from app.schemas.consent import ConsentGrantRequest


router = APIRouter(prefix="/bank", tags=["bank"])


def _get_bank_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> BankService:
    registry = BankProviderRegistry()
    registry.register("setu", setu_sandbox_provider)
    registry.register("mock", MockBankProvider())
    repo = MongoBankAccountRepository(db)
    consent_repo = MongoConsentRepository(db)
    consent_manager = ConsentManager(registry, repo, consent_repo)
    return BankService(consent_manager, repo)


def _get_sync_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> SyncService:
    registry = BankProviderRegistry()
    registry.register("setu", setu_sandbox_provider)
    registry.register("mock", MockBankProvider())
    return SyncService(
        bank_repo=MongoBankAccountRepository(db),
        consent_repo=MongoConsentRepository(db),
        pref_repo=MongoImportPreferenceRepository(db),
        tx_repo=MongoBankTransactionRepository(db),
        sync_log_repo=MongoSyncLogRepository(db),
        adapter_registry=registry,
    )


@router.post("/connect", response_model=ConnectInitResponse)
async def connect_bank(
    req: BankConnectRequest,
    user: dict = Depends(get_current_user),
    service: BankService = Depends(_get_bank_service),
) -> Any:
    return await service.initiate_connection(str(user["_id"]), req.provider)


@router.post("/consent", response_model=list[BankAccountPublic])
async def submit_consent(
    req: ConsentSubmitRequest,
    user: dict = Depends(get_current_user),
    service: BankService = Depends(_get_bank_service),
) -> Any:
    return await service.complete_consent(str(user["_id"]), req)


@router.get("/accounts", response_model=list[BankAccountPublic])
async def list_accounts(
    user: dict = Depends(get_current_user),
    service: BankService = Depends(_get_bank_service),
) -> Any:
    return await service.list_accounts(str(user["_id"]))


@router.get("/status", response_model=BankStatusResponse)
async def connection_status(
    user: dict = Depends(get_current_user),
    service: BankService = Depends(_get_bank_service),
) -> Any:
    return await service.get_status(str(user["_id"]))


@router.delete("/disconnect/{account_id}")
async def disconnect_account(
    account_id: str,
    user: dict = Depends(get_current_user),
    service: BankService = Depends(_get_bank_service),
) -> dict[str, str]:
    await service.disconnect(str(user["_id"]), account_id)
    return {"message": "Account disconnected"}


@router.post("/import", response_model=BankImportResponse)
async def import_bank_account(
    req: BankImportRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> BankImportResponse:
    user_id = str(user["_id"])
    bank_repo = MongoBankAccountRepository(db)

    account = await bank_repo.get_by_id(req.bank_account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    if str(account.user_id) != user_id:
        raise HTTPException(status_code=403, detail="You do not own this bank account")

    consent_svc = ConsentGrantService(MongoConsentRepository(db), bank_repo)
    await consent_svc.grant(user_id, ConsentGrantRequest(
        bank_account_id=req.bank_account_id,
        consent_version="1.0",
        consent_duration_days=req.consent_duration_days,
    ))

    sync_svc = _get_sync_service(db)
    sync_result = await sync_svc.start_sync(user_id, req.bank_account_id)
    if sync_result.status != "completed":
        raise HTTPException(status_code=502, detail=sync_result.message or "Transaction import failed")

    processed = await AutoProcessingService(db).process_synced(user_id, req.bank_account_id)

    await db.users.update_one({"_id": user["_id"]}, {"$set": {"is_onboarded": True}})

    return BankImportResponse(
        sync_log_id=sync_result.sync_log_id,
        status="completed",
        transactions_imported=0,
        transactions_categorized=processed.get("categorized", 0),
        financial_transactions_processed=processed.get("processed", 0),
        health_recalculated=processed.get("health_recalculated", False),
        onboarded=True,
        message="Bank account imported successfully",
    )
