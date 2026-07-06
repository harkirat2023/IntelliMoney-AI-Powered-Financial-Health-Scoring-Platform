from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import PyObjectId


class BudgetAlertPublic(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    budget_id: PyObjectId
    percentage: float
    message: str
    created_at: datetime
    read: bool
