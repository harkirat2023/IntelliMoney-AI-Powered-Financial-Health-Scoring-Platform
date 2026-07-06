from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import BulkWriteError

from app.domain.sync.models import BankTransaction, SyncLog
from app.domain.sync.repository import BankTransactionRepository, SyncLogRepository
from app.utils.date_utils import utc_now
from app.utils.object_id import to_object_id


class MongoBankTransactionRepository(BankTransactionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, tx: BankTransaction) -> BankTransaction:
        doc = tx.to_mongo()
        result = await self._db.bank_transactions.insert_one(doc)
        tx.id = str(result.inserted_id)
        return tx

    async def bulk_create(self, txs: list[BankTransaction]) -> int:
        if not txs:
            return 0
        docs = [tx.to_mongo() for tx in txs]
        try:
            result = await self._db.bank_transactions.insert_many(docs, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as bwe:
            return bwe.details["nInserted"]

    async def find_by_account(
        self, user_id: str, bank_account_id: str, limit: int = 50, offset: int = 0
    ) -> list[BankTransaction]:
        cursor = self._db.bank_transactions.find(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)}
        ).sort("transaction_date", -1).skip(offset).limit(limit)
        return [BankTransaction.from_mongo(doc) async for doc in cursor]

    async def find_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[BankTransaction]:
        cursor = self._db.bank_transactions.find(
            {"user_id": to_object_id(user_id)}
        ).sort("transaction_date", -1).skip(offset).limit(limit)
        return [BankTransaction.from_mongo(doc) async for doc in cursor]

    async def find_by_date_range(
        self, user_id: str, bank_account_id: str, from_date: datetime, to_date: datetime
    ) -> list[BankTransaction]:
        cursor = self._db.bank_transactions.find(
            {
                "user_id": to_object_id(user_id),
                "bank_account_id": to_object_id(bank_account_id),
                "transaction_date": {"$gte": from_date, "$lte": to_date},
            }
        ).sort("transaction_date", -1)
        return [BankTransaction.from_mongo(doc) async for doc in cursor]

    async def count_by_account(self, user_id: str, bank_account_id: str) -> int:
        return await self._db.bank_transactions.count_documents(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)},
        )

    async def exists_by_provider_id(self, provider_account_id: str, transaction_id: str) -> bool:
        doc = await self._db.bank_transactions.find_one(
            {"provider_account_id": provider_account_id, "transaction_id": transaction_id},
            {"_id": 1},
        )
        return doc is not None


class MongoSyncLogRepository(SyncLogRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, log: SyncLog) -> SyncLog:
        doc = log.to_mongo()
        result = await self._db.sync_logs.insert_one(doc)
        log.id = str(result.inserted_id)
        return log

    async def get_by_id(self, log_id: str) -> SyncLog | None:
        doc = await self._db.sync_logs.find_one({"_id": to_object_id(log_id)})
        return SyncLog.from_mongo(doc) if doc else None

    async def get_latest_by_account(self, user_id: str, bank_account_id: str) -> SyncLog | None:
        doc = await self._db.sync_logs.find_one(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)},
            sort=[("created_at", -1)],
        )
        return SyncLog.from_mongo(doc) if doc else None

    async def get_by_account(
        self, user_id: str, bank_account_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncLog]:
        cursor = self._db.sync_logs.find(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)}
        ).sort("created_at", -1).skip(offset).limit(limit)
        return [SyncLog.from_mongo(doc) async for doc in cursor]

    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncLog]:
        cursor = self._db.sync_logs.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).skip(offset).limit(limit)
        return [SyncLog.from_mongo(doc) async for doc in cursor]

    async def update_status(
        self, log_id: str, status: str, **kwargs
    ) -> SyncLog | None:
        update = {"status": status}
        update.update(kwargs)
        await self._db.sync_logs.update_one(
            {"_id": to_object_id(log_id)},
            {"$set": update},
        )
        return await self.get_by_id(log_id)

    async def count_by_account(self, user_id: str, bank_account_id: str) -> int:
        return await self._db.sync_logs.count_documents(
            {"user_id": to_object_id(user_id), "bank_account_id": to_object_id(bank_account_id)},
        )

    async def count_by_user(self, user_id: str) -> int:
        return await self._db.sync_logs.count_documents(
            {"user_id": to_object_id(user_id)},
        )
