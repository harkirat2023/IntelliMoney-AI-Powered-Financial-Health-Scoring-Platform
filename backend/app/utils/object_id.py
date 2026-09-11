from typing import Any
from bson import ObjectId

from app.core.exceptions import ValidationException


def to_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValidationException(f"Invalid ID format: {value}")
    return ObjectId(value)


def user_id_query(user_id: Any) -> Any:
    """Build a MongoDB query filter for user_id matching both ObjectId and string formats safely."""
    if not user_id:
        return user_id
    if isinstance(user_id, ObjectId):
        return {"$in": [user_id, str(user_id)]}
    user_str = str(user_id)
    if ObjectId.is_valid(user_str):
        return {"$in": [ObjectId(user_str), user_str]}
    return user_str


def to_user_id(user_id: Any) -> Any:
    """Convert a user_id to ObjectId if valid 24-hex string, otherwise return string."""
    if not user_id:
        return user_id
    if isinstance(user_id, ObjectId):
        return user_id
    user_str = str(user_id)
    if ObjectId.is_valid(user_str):
        return ObjectId(user_str)
    return user_str

