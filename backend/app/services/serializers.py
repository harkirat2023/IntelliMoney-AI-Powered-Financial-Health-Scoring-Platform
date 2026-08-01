from datetime import date, datetime
from typing import Any
from bson import ObjectId

from app.utils.date_utils import date_to_datetime, month_bounds, utc_now
from app.utils.object_id import to_object_id


def serialize_document(doc: dict[str, Any] | None) -> dict[str, Any]:
    if not doc:
        return {}
    res = dict(doc)
    if "_id" in res:
        res["id"] = str(res["_id"])
        del res["_id"]
    for k, v in res.items():
        if isinstance(v, ObjectId):
            res[k] = str(v)
        elif isinstance(v, (datetime, date)):
            res[k] = v.isoformat()
    return res


__all__ = ["serialize_document", "utc_now", "month_bounds", "date_to_datetime", "to_object_id"]

