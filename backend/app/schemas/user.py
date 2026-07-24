from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import PyObjectId


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    monthly_income: float = Field(default=0, ge=0)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: PyObjectId
    name: str
    email: EmailStr
    monthly_income: float
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic
