import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import (
    create_access_token, create_refresh_token, decode_refresh_token,
    hash_password, verify_password,
)
from app.db.mongodb import get_database
from app.schemas.user import Token, UserCreate, UserLogin, UserPublic
from app.services.serializers import serialize_document, utc_now


router = APIRouter(prefix="/auth", tags=["auth"])

_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(key: str) -> None:
    settings = get_settings()
    if not settings.rate_limit_auth_enabled:
        return
    now = time.time()
    window = settings.rate_limit_auth_window_seconds
    max_req = settings.rate_limit_auth_max_requests
    timestamps = _rate_limit_store[key]
    cutoff = now - window
    _rate_limit_store[key] = [t for t in timestamps if t > cutoff]
    if len(_rate_limit_store[key]) >= max_req:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    _rate_limit_store[key].append(now)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Token:
    _check_rate_limit(f"register:{request.client.host}")
    document = {
        "name": payload.name,
        "email": payload.email.lower(),
        "hashed_password": hash_password(payload.password),
        "monthly_income": payload.monthly_income,
        "created_at": utc_now(),
    }
    try:
        result = await db.users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    document["_id"] = result.inserted_id
    user = UserPublic(**serialize_document(document))
    user_id = str(result.inserted_id)
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        user=user,
    )


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Token:
    _check_rate_limit(f"login:{request.client.host}")
    user_doc = await db.users.find_one({"email": payload.email.lower()})
    if not user_doc or not verify_password(payload.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = UserPublic(**serialize_document(user_doc))
    user_id = str(user_doc["_id"])
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        user=user,
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    body: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Token:
    user_id = decode_refresh_token(body.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    object_id = None
    try:
        from bson import ObjectId
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    user_doc = await db.users.find_one({"_id": object_id})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    user = UserPublic(**serialize_document(user_doc))
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        user=user,
    )


@router.get("/me", response_model=UserPublic)
async def me(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**serialize_document(current_user))
