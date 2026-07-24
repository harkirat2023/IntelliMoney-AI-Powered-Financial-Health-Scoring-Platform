from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.infrastructure.bank_integration import MockBankProvider
from app.infrastructure.bank_integration.consent_manager import BankProviderRegistry, ConsentManager
from app.infrastructure.database.repositories.bank_repository import MongoBankAccountRepository
from app.infrastructure.database.repositories.consent_repository import MongoConsentRepository
from app.schemas.bank import BankAccountPublic, BankConnectRequest, BankStatusResponse, ConnectInitResponse, ConsentSubmitRequest
from app.services.bank_service import BankService


router = APIRouter(prefix="/bank", tags=["bank"])


def _get_bank_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> BankService:
    registry = BankProviderRegistry()
    registry.register("mock", MockBankProvider())
    repo = MongoBankAccountRepository(db)
    consent_repo = MongoConsentRepository(db)
    consent_manager = ConsentManager(registry, repo, consent_repo)
    return BankService(consent_manager, repo)


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
