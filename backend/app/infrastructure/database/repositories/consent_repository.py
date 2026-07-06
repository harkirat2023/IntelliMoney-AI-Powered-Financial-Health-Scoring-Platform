from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.consents.models import ConsentGrant
from app.domain.consents.repository import ConsentRepository
from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class MongoConsentRepository(ConsentRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, consent: ConsentGrant) -> ConsentGrant:
        doc = consent.to_mongo()
        result = await self._db.consents.insert_one(doc)
        consent.id = str(result.inserted_id)
        return consent

    async def get_by_id(self, consent_id: str) -> ConsentGrant | None:
        doc = await self._db.consents.find_one({"_id": to_object_id(consent_id)})
        return ConsentGrant.from_mongo(doc) if doc else None

    async def get_active_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None:
        doc = await self._db.consents.find_one({
            "user_id": to_object_id(user_id),
            "bank_account_id": to_object_id(bank_account_id),
            "consent_status": "granted",
            "$or": [
                {"expires_at": {"$exists": False}},
                {"expires_at": None},
                {"expires_at": {"$gt": utc_now()}},
            ],
        })
        return ConsentGrant.from_mongo(doc) if doc else None

    async def get_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None:
        doc = await self._db.consents.find_one(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)},
            sort=[("created_at", -1)],
        )
        return ConsentGrant.from_mongo(doc) if doc else None

    async def update_status(self, consent_id: str, status: str, revoked_at: datetime | None = None) -> ConsentGrant | None:
        update = {"consent_status": status, "updated_at": utc_now()}
        if revoked_at:
            update["revoked_at"] = revoked_at
        await self._db.consents.update_one(
            {"_id": to_object_id(consent_id)},
            {"$set": update},
        )
        return await self.get_by_id(consent_id)

    async def get_all_expired(self) -> list[ConsentGrant]:
        docs = self._db.consents.find({
            "consent_status": "granted",
            "expires_at": {"$lt": utc_now()},
        })
        return [ConsentGrant.from_mongo(doc) async for doc in docs]
