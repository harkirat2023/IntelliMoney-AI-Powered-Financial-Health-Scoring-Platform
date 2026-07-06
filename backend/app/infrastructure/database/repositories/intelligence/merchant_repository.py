from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.object_id import to_object_id


class MongoMerchantRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def find_by_name(self, name: str) -> dict | None:
        return await self._db.merchant_dictionary.find_one({"merchant_name": name.lower()})

    async def find_all_active(self) -> list[dict]:
        cursor = self._db.merchant_dictionary.find({"is_active": True})
        return [doc async for doc in cursor]

    async def find_aliases_by_type(self, alias_type: str) -> list[dict]:
        cursor = self._db.merchant_aliases.find(
            {"alias_type": alias_type}
        ).sort("priority", -1)
        return [doc async for doc in cursor]

    async def find_all_aliases(self) -> list[dict]:
        cursor = self._db.merchant_aliases.find().sort("priority", -1)
        return [doc async for doc in cursor]
