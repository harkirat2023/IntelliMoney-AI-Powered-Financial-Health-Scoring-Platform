from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongodb import get_database
from app.schemas.user import Token, UserCreate, UserLogin, UserPublic
from app.services.serializers import serialize_document


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)) -> Token:
    document = {
        "name": payload.name,
        "email": payload.email.lower(),
        "hashed_password": hash_password(payload.password),
        "monthly_income": payload.monthly_income,
        "created_at": datetime.utcnow(),
    }
    try:
        result = await db.users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    document["_id"] = result.inserted_id
    user = UserPublic(**serialize_document(document))
    return Token(access_token=create_access_token(str(result.inserted_id)), user=user)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)) -> Token:
    user_doc = await db.users.find_one({"email": payload.email.lower()})
    if not user_doc or not verify_password(payload.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = UserPublic(**serialize_document(user_doc))
    return Token(access_token=create_access_token(str(user_doc["_id"])), user=user)


@router.get("/me", response_model=UserPublic)
async def me(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**serialize_document(current_user))
