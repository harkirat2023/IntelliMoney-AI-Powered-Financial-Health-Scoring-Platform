from typing import Any


def serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    item = dict(document)
    item["id"] = str(item.pop("_id"))
    if "user_id" in item:
        item["user_id"] = str(item["user_id"])
    return item
