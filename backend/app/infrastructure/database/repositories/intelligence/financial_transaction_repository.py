from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import BulkWriteError

from app.domain.financial_transactions.models import FinancialTransaction
from app.domain.financial_transactions.repository import FinancialTransactionRepository
from app.utils.object_id import to_object_id


class MongoFinancialTransactionRepository(FinancialTransactionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, tx: FinancialTransaction) -> FinancialTransaction:
        doc = tx.to_mongo()
        result = await self._db.financial_transactions.insert_one(doc)
        tx.id = str(result.inserted_id)
        return tx

    async def bulk_create(self, txs: list[FinancialTransaction]) -> int:
        if not txs:
            return 0
        docs = [tx.to_mongo() for tx in txs]
        try:
            result = await self._db.financial_transactions.insert_many(docs, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as bwe:
            return bwe.details["nInserted"]

    async def get_by_id(self, tx_id: str) -> FinancialTransaction | None:
        doc = await self._db.financial_transactions.find_one({"_id": to_object_id(tx_id)})
        return FinancialTransaction.from_mongo(doc) if doc else None

    async def find_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[FinancialTransaction]:
        cursor = self._db.financial_transactions.find(
            {"user_id": to_object_id(user_id)}
        ).sort("transaction_date", -1).skip(offset).limit(limit)
        return [FinancialTransaction.from_mongo(doc) async for doc in cursor]

    async def find_by_user_and_category(
        self, user_id: str, category: str, limit: int = 50, offset: int = 0
    ) -> list[FinancialTransaction]:
        cursor = self._db.financial_transactions.find(
            {"user_id": to_object_id(user_id), "assigned_category": category}
        ).sort("transaction_date", -1).skip(offset).limit(limit)
        return [FinancialTransaction.from_mongo(doc) async for doc in cursor]

    async def find_by_review_status(
        self, user_id: str, status: str, limit: int = 20, offset: int = 0
    ) -> list[FinancialTransaction]:
        cursor = self._db.financial_transactions.find(
            {"user_id": to_object_id(user_id), "review_status": status}
        ).sort("transaction_date", -1).skip(offset).limit(limit)
        return [FinancialTransaction.from_mongo(doc) async for doc in cursor]

    async def find_by_date_range(
        self, user_id: str, from_date: datetime, to_date: datetime
    ) -> list[FinancialTransaction]:
        cursor = self._db.financial_transactions.find(
            {
                "user_id": to_object_id(user_id),
                "transaction_date": {"$gte": from_date, "$lte": to_date},
            }
        ).sort("transaction_date", -1)
        return [FinancialTransaction.from_mongo(doc) async for doc in cursor]

    async def find_unprocessed_bank_tx_ids(
        self, user_id: str, bank_tx_ids: list[str]
    ) -> list[str]:
        if not bank_tx_ids:
            return []
        obj_ids = [to_object_id(bid) for bid in bank_tx_ids]
        cursor = self._db.financial_transactions.find(
            {"user_id": to_object_id(user_id), "bank_transaction_id": {"$in": obj_ids}},
            {"bank_transaction_id": 1},
        )
        processed_ids = set()
        async for doc in cursor:
            processed_ids.add(str(doc["bank_transaction_id"]))
        return [bid for bid in bank_tx_ids if bid not in processed_ids]

    async def atomic_claim(self, tx_id: str) -> FinancialTransaction | None:
        from app.utils.date_utils import utc_now
        doc = await self._db.financial_transactions.find_one_and_update(
            {"_id": to_object_id(tx_id), "processed_at": None},
            {"$set": {"processed_at": utc_now()}},
            return_document=True,
        )
        return FinancialTransaction.from_mongo(doc) if doc else None

    async def atomic_review_update(
        self, tx_id: str, expected_review_status: str,
        review_status: str, reviewed_by: str, reviewed_at: datetime,
        review_note: str | None = None,
        assigned_category: str | None = None,
    ) -> FinancialTransaction | None:
        update = {
            "review_status": review_status,
            "reviewed_by": to_object_id(reviewed_by),
            "reviewed_at": reviewed_at,
        }
        if review_note is not None:
            update["review_note"] = review_note
        if assigned_category is not None:
            update["assigned_category"] = assigned_category
        doc = await self._db.financial_transactions.find_one_and_update(
            {"_id": to_object_id(tx_id), "review_status": expected_review_status},
            {"$set": update},
            return_document=True,
        )
        return FinancialTransaction.from_mongo(doc) if doc else None

    async def update_fields(
        self, tx_id: str, update_data: dict,
    ) -> FinancialTransaction | None:
        doc = await self._db.financial_transactions.find_one_and_update(
            {"_id": to_object_id(tx_id)},
            {"$set": update_data},
            return_document=True,
        )
        return FinancialTransaction.from_mongo(doc) if doc else None

    async def find_unprocessed(self, user_id: str, limit: int = 100) -> list[FinancialTransaction]:
        cursor = self._db.financial_transactions.find(
            {"user_id": to_object_id(user_id), "processed_at": None}
        ).sort("created_at", 1).limit(limit)
        return [FinancialTransaction.from_mongo(doc) async for doc in cursor]

    async def count_by_user(self, user_id: str) -> int:
        return await self._db.financial_transactions.count_documents(
            {"user_id": to_object_id(user_id)},
        )

    async def count_by_review_status(self, user_id: str, status: str) -> int:
        return await self._db.financial_transactions.count_documents(
            {"user_id": to_object_id(user_id), "review_status": status},
        )
