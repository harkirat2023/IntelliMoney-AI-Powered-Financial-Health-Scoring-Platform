from pydantic import BaseModel, Field

from app.schemas.common import PyObjectId


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    limit: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetUpdate(BaseModel):
    limit: float | None = Field(default=None, gt=0)


class BudgetPublic(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    category: str
    limit: float
    month: int
    year: int


class BudgetStatus(BaseModel):
    id: PyObjectId
    category: str
    limit: float
    spent: float
    remaining: float
    percentage_used: float
    state: str
