from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.receipt_ocr.models.receipt_models import Receipt, ReceiptProcessingLog


class ReceiptRepository(ABC):
    @abstractmethod
    async def create(self, receipt: Receipt) -> Receipt: ...
    @abstractmethod
    async def get_by_id(self, receipt_id: str) -> Receipt | None: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, status: str | None = None,
                          limit: int = 50) -> list[Receipt]: ...
    @abstractmethod
    async def update(self, receipt_id: str, data: dict) -> bool: ...
    @abstractmethod
    async def delete(self, receipt_id: str) -> bool: ...
    @abstractmethod
    async def get_by_user_and_filename(self, user_id: str, filename: str) -> Receipt | None: ...


class ReceiptProcessingLogRepository(ABC):
    @abstractmethod
    async def create(self, log: ReceiptProcessingLog) -> ReceiptProcessingLog: ...
    @abstractmethod
    async def get_by_receipt(self, receipt_id: str) -> list[ReceiptProcessingLog]: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[ReceiptProcessingLog]: ...
    @abstractmethod
    async def delete_by_receipt(self, receipt_id: str) -> int: ...


class MongoReceiptRepository(ReceiptRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.receipts

    async def create(self, receipt: Receipt) -> Receipt:
        doc = receipt.to_mongo()
        doc["created_at"] = doc["updated_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        receipt.id = str(r.inserted_id)
        return receipt

    async def get_by_id(self, receipt_id: str) -> Receipt | None:
        d = await self._collection.find_one({"_id": receipt_id})
        return Receipt.from_mongo(d) if d else None

    async def get_by_user(self, user_id: str, status: str | None = None,
                          limit: int = 50) -> list[Receipt]:
        q = {"user_id": user_id}
        if status:
            q["status"] = status
        cursor = self._collection.find(q).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [Receipt.from_mongo(d) for d in docs]

    async def update(self, receipt_id: str, data: dict) -> bool:
        data["updated_at"] = datetime.utcnow()
        r = await self._collection.update_one({"_id": receipt_id}, {"$set": data})
        return r.modified_count > 0

    async def delete(self, receipt_id: str) -> bool:
        r = await self._collection.delete_one({"_id": receipt_id})
        return r.deleted_count > 0

    async def get_by_user_and_filename(self, user_id: str, filename: str) -> Receipt | None:
        d = await self._collection.find_one({"user_id": user_id, "filename": filename})
        return Receipt.from_mongo(d) if d else None


class MongoReceiptProcessingLogRepository(ReceiptProcessingLogRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.receipt_processing_logs

    async def create(self, log: ReceiptProcessingLog) -> ReceiptProcessingLog:
        doc = log.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        log.id = str(r.inserted_id)
        return log

    async def get_by_receipt(self, receipt_id: str) -> list[ReceiptProcessingLog]:
        cursor = self._collection.find({"receipt_id": receipt_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [ReceiptProcessingLog.from_mongo(d) for d in docs]

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[ReceiptProcessingLog]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [ReceiptProcessingLog.from_mongo(d) for d in docs]

    async def delete_by_receipt(self, receipt_id: str) -> int:
        r = await self._collection.delete_many({"receipt_id": receipt_id})
        return r.deleted_count
