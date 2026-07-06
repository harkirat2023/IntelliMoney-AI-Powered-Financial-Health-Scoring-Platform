from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.bank_accounts.models import BankAccount
from app.domain.bank_accounts.repository import BankAccountRepository
from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class MongoBankAccountRepository(BankAccountRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, account: BankAccount) -> BankAccount:
        doc = account.to_mongo()
        result = await self._db.bank_accounts.insert_one(doc)
        account.id = str(result.inserted_id)
        return account

    async def get_by_user_id(self, user_id: str) -> list[BankAccount]:
        docs = self._db.bank_accounts.find({"user_id": to_object_id(user_id)}).sort("created_at", -1)
        return [BankAccount.from_mongo(doc) async for doc in docs]

    async def get_active_by_user_id(self, user_id: str) -> list[BankAccount]:
        docs = self._db.bank_accounts.find(
            {"user_id": to_object_id(user_id), "connection_status": "active"}
        ).sort("created_at", -1)
        return [BankAccount.from_mongo(doc) async for doc in docs]

    async def get_all_active(self) -> list[BankAccount]:
        docs = self._db.bank_accounts.find({"connection_status": "active"}).sort("created_at", -1)
        return [BankAccount.from_mongo(doc) async for doc in docs]

    async def get_by_id(self, account_id: str) -> BankAccount | None:
        doc = await self._db.bank_accounts.find_one({"_id": to_object_id(account_id)})
        return BankAccount.from_mongo(doc) if doc else None

    async def get_by_consent_handle(self, consent_handle: str) -> BankAccount | None:
        doc = await self._db.bank_accounts.find_one({"consent_handle": consent_handle})
        return BankAccount.from_mongo(doc) if doc else None

    async def update_connection_status(self, account_id: str, status: str) -> BankAccount | None:
        await self._db.bank_accounts.update_one(
            {"_id": to_object_id(account_id)},
            {"$set": {"connection_status": status, "updated_at": utc_now()}},
        )
        return await self.get_by_id(account_id)

    async def update_consent_status(self, account_id: str, status: str, expiry: datetime | None = None) -> BankAccount | None:
        update = {"consent_status": status, "updated_at": utc_now()}
        if expiry:
            update["consent_expiry"] = expiry
        await self._db.bank_accounts.update_one(
            {"_id": to_object_id(account_id)},
            {"$set": update},
        )
        return await self.get_by_id(account_id)

    async def delete(self, account_id: str) -> bool:
        result = await self._db.bank_accounts.delete_one({"_id": to_object_id(account_id)})
        return result.deleted_count > 0

    async def count_active_by_user_id(self, user_id: str) -> int:
        return await self._db.bank_accounts.count_documents(
            {"user_id": to_object_id(user_id), "connection_status": "active"},
        )

    async def update_last_synced(self, account_id: str, synced_at: datetime) -> BankAccount | None:
        await self._db.bank_accounts.update_one(
            {"_id": to_object_id(account_id)},
            {"$set": {"last_synced_at": synced_at, "updated_at": utc_now()}},
        )
        return await self.get_by_id(account_id)
