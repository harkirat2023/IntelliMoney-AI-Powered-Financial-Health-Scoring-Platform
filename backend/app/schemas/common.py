from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator


def object_id_to_str(value: object) -> str:
    return str(value)


PyObjectId = Annotated[str, BeforeValidator(object_id_to_str)]


class TimestampMixin:
    created_at: datetime
