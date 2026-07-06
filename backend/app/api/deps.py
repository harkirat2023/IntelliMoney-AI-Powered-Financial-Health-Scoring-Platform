from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_access_token
from app.db.mongodb import get_database
from app.services.serializers import to_object_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    object_id = to_object_id(user_id)
    user = await db.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
