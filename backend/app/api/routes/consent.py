from typing import Any

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.domain.bank_accounts.repository import BankAccountRepository
from app.infrastructure.database.repositories.bank_repository import MongoBankAccountRepository
from app.infrastructure.database.repositories.consent_repository import MongoConsentRepository
from app.schemas.consent import (
    ConsentGrantRequest,
    ConsentGrantResponse,
    ConsentRevokeRequest,
    ConsentRevokeResponse,
    ConsentStatusResponse,
)
from app.services.consent_grant_service import ConsentGrantService


router = APIRouter(prefix="/consent", tags=["consent"])


def _get_consent_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ConsentGrantService:
    consent_repo = MongoConsentRepository(db)
    bank_repo: BankAccountRepository = MongoBankAccountRepository(db)
    return ConsentGrantService(consent_repo, bank_repo)


@router.post("/grant", response_model=ConsentGrantResponse)
async def grant_consent(
    req: ConsentGrantRequest,
    user: dict = Depends(get_current_user),
    service: ConsentGrantService = Depends(_get_consent_service),
) -> Any:
    return await service.grant(str(user["_id"]), req)


@router.post("/revoke", response_model=ConsentRevokeResponse)
async def revoke_consent(
    req: ConsentRevokeRequest,
    user: dict = Depends(get_current_user),
    service: ConsentGrantService = Depends(_get_consent_service),
) -> Any:
    return await service.revoke(str(user["_id"]), req)


@router.get("/status", response_model=ConsentStatusResponse)
async def consent_status(
    bank_account_id: str = Query(...),
    user: dict = Depends(get_current_user),
    service: ConsentGrantService = Depends(_get_consent_service),
) -> Any:
    return await service.get_status(str(user["_id"]), bank_account_id)
