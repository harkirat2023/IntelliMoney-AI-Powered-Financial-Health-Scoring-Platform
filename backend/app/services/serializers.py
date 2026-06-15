from datetime import date, datetime
from typing import Any

from bson import ObjectId


def serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    item = dict(document)
    item["id"] = str(item.pop("_id"))
    if "user_id" in item:
        item["user_id"] = str(item["user_id"])
    return item


def utc_now() -> datetime:
    return datetime.utcnow()


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def date_to_datetime(value: date) -> datetime:
    return datetime.combine(value, datetime.min.time())


def to_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return ObjectId(value)
