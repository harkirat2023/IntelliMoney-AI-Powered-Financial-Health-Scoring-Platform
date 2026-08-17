from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import PyObjectId


class UserPublic(BaseModel):
    id: PyObjectId
    name: str
    email: EmailStr
    monthly_income: float
    is_verified: bool = False
    is_onboarded: bool = False
    clerk_user_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ClerkSyncRequest(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    monthly_income: float | None = Field(default=None, ge=0)