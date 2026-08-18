from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.core.clerk import upsert_clerk_user
from app.core.security import validate_bearer_token
from app.db.mongodb import get_database
from app.schemas.user import ClerkSyncRequest, UserPublic
from app.services.serializers import serialize_document

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/clerk-sync", response_model=UserPublic)
async def clerk_sync(
    payload: ClerkSyncRequest | None = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """Create or refresh the local user profile for an authenticated Clerk user.

    The Clerk session token is read from the ``Authorization: Bearer``
    header, verified against Clerk's JWKS, and the local profile is
    upserted keyed by the Clerk user ID. Optional profile fields (name,
    monthly income) may be supplied and are applied on top of the data
    Clerk already provides.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = await validate_bearer_token(credentials.credentials)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user, is_new_user = await upsert_clerk_user(db, claims)
    update: dict[str, Any] = {}
    if payload and payload.name:
        update["name"] = payload.name
    if payload and payload.email:
        update["email"] = payload.email.strip().lower()
    if payload and payload.monthly_income is not None:
        update["monthly_income"] = payload.monthly_income
    if update:
        from app.utils.date_utils import utc_now

        update["updated_at"] = utc_now()
        await db.users.update_one({"_id": user["_id"]}, {"$set": update})
        user = await db.users.find_one({"_id": user["_id"]})
    return UserPublic(**serialize_document(user), is_new_user=is_new_user)


@router.post("/onboarding/complete", response_model=UserPublic)
async def complete_onboarding(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserPublic:
    from app.utils.date_utils import utc_now

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"is_onboarded": True, "updated_at": utc_now()}},
    )
    current_user["is_onboarded"] = True
    return UserPublic(**serialize_document(current_user))


@router.get("/me", response_model=UserPublic)
async def me(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**serialize_document(current_user))