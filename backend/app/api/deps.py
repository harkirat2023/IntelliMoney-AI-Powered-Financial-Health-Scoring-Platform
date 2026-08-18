from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.clerk import upsert_clerk_user
from app.core.security import validate_bearer_token
from app.db.mongodb import get_database

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Resolve the authenticated Clerk user.

    The frontend attaches the Clerk session token as a Bearer token. The
    token is verified against Clerk's JWKS and the matching local user
    profile (keyed by ``clerk_user_id``) is returned.

    Every financial resource is owned by this authenticated user; a
    client-provided user ID is never trusted for authorization.
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
    user, _ = await upsert_clerk_user(db, claims)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user