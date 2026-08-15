import hashlib
import secrets
import time
from collections import defaultdict
from datetime import timedelta

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr
from pymongo.errors import DuplicateKeyError

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import (
    create_access_token, create_refresh_token, decode_refresh_token,
    hash_password, verify_password,
)
from app.db.mongodb import get_database
from app.schemas.user import Token, UserCreate, UserLogin, UserPublic
from app.services.email_service import render_otp_email, send_email
from app.services.serializers import serialize_document, utc_now


router = APIRouter(prefix="/auth", tags=["auth"])

_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def _hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


async def _issue_otp_for_user(user_doc: dict, db) -> str:
    otp = _generate_otp()
    now = utc_now()
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {
            "otp_hash": _hash_otp(otp),
            "otp_expires_at": now + timedelta(minutes=get_settings().otp_expire_minutes),
        }},
    )
    await send_email(
        to=user_doc["email"],
        subject="Your IntelliMoney verification code",
        html=render_otp_email(otp, user_doc["name"]),
    )
    return otp


def _check_rate_limit(key: str) -> None:
    settings = get_settings()
    if not settings.rate_limit_auth_enabled or settings.environment in ("testing", "test"):
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
    db: AsyncIOMotorDatabase = Depends(get_database),
    request: Request = None,
) -> Token:
    client_ip = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    _check_rate_limit(f"register:{client_ip}")
    document = {
        "name": payload.name,
        "email": payload.email.lower(),
        "hashed_password": hash_password(payload.password),
        "monthly_income": payload.monthly_income,
        "is_verified": False,
        "is_onboarded": False,
        "created_at": utc_now(),
    }
    try:
        result = await db.users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    document["_id"] = result.inserted_id
    await _issue_otp_for_user(document, db)
    user = UserPublic(**serialize_document(document))
    user_id = str(result.inserted_id)
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        user=user,
    )


class SendOtpRequest(BaseModel):
    email: EmailStr


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(
    payload: SendOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    request: Request = None,
) -> dict:
    client_ip = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    _check_rate_limit(f"otp:{client_ip}")
    user_doc = await db.users.find_one({"email": payload.email.lower()})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Account not found")
    await _issue_otp_for_user(user_doc, db)
    return {"message": "Verification code sent"}


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str


@router.post("/verify-otp", response_model=UserPublic)
async def verify_otp(
    payload: VerifyOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    request: Request = None,
) -> UserPublic:
    client_ip = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    _check_rate_limit(f"otp-verify:{client_ip}")
    user_doc = await db.users.find_one({"email": payload.email.lower()})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Account not found")
    if user_doc.get("is_verified"):
        return UserPublic(**serialize_document(user_doc))
    stored_hash = user_doc.get("otp_hash")
    expires_at = user_doc.get("otp_expires_at")
    if not stored_hash or not expires_at:
        raise HTTPException(status_code=400, detail="No verification code pending. Request a new one.")
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=__import__("datetime").timezone.utc)
    if utc_now() > expires_at:
        raise HTTPException(status_code=400, detail="Verification code expired. Request a new one.")
    if _hash_otp(payload.code.strip()) != stored_hash:
        raise HTTPException(status_code=400, detail="Invalid verification code.")
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"otp_hash": "", "otp_expires_at": ""}},
    )
    user_doc["is_verified"] = True
    user_doc.pop("otp_hash", None)
    user_doc.pop("otp_expires_at", None)
    return UserPublic(**serialize_document(user_doc))


class OnboardCompleteRequest(BaseModel):
    pass


@router.post("/onboarding/complete", response_model=UserPublic)
async def complete_onboarding(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserPublic:
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"is_onboarded": True}},
    )
    current_user["is_onboarded"] = True
    return UserPublic(**serialize_document(current_user))


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database),
    request: Request = None,
) -> Token:
    client_ip = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    _check_rate_limit(f"login:{client_ip}")
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
