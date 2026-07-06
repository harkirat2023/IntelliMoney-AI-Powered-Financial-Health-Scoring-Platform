from bson import ObjectId

from app.core.exceptions import ValidationException


def to_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValidationException(f"Invalid ID format: {value}")
    return ObjectId(value)
