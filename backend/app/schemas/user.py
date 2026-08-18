from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import PyObjectId


class UserPublic(BaseModel):
    id: PyObjectId
    name: str
    email: EmailStr | None = None
    monthly_income: float
    is_verified: bool = False
    is_onboarded: bool = False
    is_new_user: bool = False
    clerk_user_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("email", mode="before")
    @classmethod
    def _empty_or_invalid_email_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if "@" not in value:
                return None
        return value or None


class ClerkSyncRequest(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=254)
    monthly_income: float | None = Field(default=None, ge=0)