from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.import_preferences.models import ImportPreference
from app.domain.import_preferences.repository import ImportPreferenceRepository
from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class MongoImportPreferenceRepository(ImportPreferenceRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def upsert(self, pref: ImportPreference) -> ImportPreference:
        doc = pref.to_mongo()
        now = utc_now()
        doc["updated_at"] = now
        doc["created_at"] = now
        filter_doc = {
            "user_id": to_object_id(pref.user_id),
            "bank_account_id": to_object_id(pref.bank_account_id),
        }
        result = await self._db.import_preferences.update_one(
            filter_doc,
            {"$set": doc},
            upsert=True,
        )
        if result.upserted_id:
            pref.id = str(result.upserted_id)
        else:
            existing = await self._db.import_preferences.find_one(filter_doc)
            if existing:
                pref.id = str(existing["_id"])
        return pref

    async def get_by_account(self, user_id: str, bank_account_id: str) -> ImportPreference | None:
        doc = await self._db.import_preferences.find_one({
            "user_id": to_object_id(user_id),
            "bank_account_id": to_object_id(bank_account_id),
        })
        return ImportPreference.from_mongo(doc) if doc else None

    async def get_by_user(self, user_id: str) -> list[ImportPreference]:
        docs = self._db.import_preferences.find({"user_id": to_object_id(user_id)})
        return [ImportPreference.from_mongo(doc) async for doc in docs]
