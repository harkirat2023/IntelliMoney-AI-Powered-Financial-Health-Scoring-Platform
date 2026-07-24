from typing import Any

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.infrastructure.database.repositories.bank_repository import MongoBankAccountRepository
from app.infrastructure.database.repositories.import_preference_repository import MongoImportPreferenceRepository
from app.schemas.import_preference import ImportPreferenceRequest, ImportPreferenceResponse
from app.services.import_preference_service import ImportPreferenceService


router = APIRouter(prefix="/import-preference", tags=["import_preference"])


def _get_pref_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ImportPreferenceService:
    pref_repo = MongoImportPreferenceRepository(db)
    bank_repo = MongoBankAccountRepository(db)
    return ImportPreferenceService(pref_repo, bank_repo)


@router.post("/", response_model=ImportPreferenceResponse)
async def save_import_preference(
    req: ImportPreferenceRequest,
    user: dict = Depends(get_current_user),
    service: ImportPreferenceService = Depends(_get_pref_service),
) -> Any:
    return await service.save(str(user["_id"]), req)


@router.get("/", response_model=ImportPreferenceResponse)
async def get_import_preference(
    bank_account_id: str = Query(...),
    user: dict = Depends(get_current_user),
    service: ImportPreferenceService = Depends(_get_pref_service),
) -> Any:
    return await service.get(str(user["_id"]), bank_account_id)
