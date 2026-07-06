from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, field_validator


class ImportPreferenceRequest(BaseModel):
    bank_account_id: str
    import_type: Literal["import_all", "start_fresh", "from_date"]
    import_start_date: datetime | None = None

    @field_validator("import_start_date")
    @classmethod
    def validate_start_date(cls, v: datetime | None, info) -> datetime | None:
        if info.data.get("import_type") == "from_date" and v is None:
            raise ValueError("import_start_date is required when import_type is 'from_date'")
        if v is not None and v > datetime.now(timezone.utc):
            raise ValueError("import_start_date must not be in the future")
        return v


class ImportPreferenceResponse(BaseModel):
    id: str
    bank_account_id: str
    import_type: str
    import_start_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
