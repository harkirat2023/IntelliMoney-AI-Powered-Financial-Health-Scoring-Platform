from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.models.processing_batch import ProcessingBatch, ProcessingSummary
from app.utils.object_id import to_object_id
from app.utils.date_utils import utc_now


class ProcessingBatchRepository(ABC):
    @abstractmethod
    async def create(self, batch: ProcessingBatch) -> ProcessingBatch:
        ...

    @abstractmethod
    async def get_by_batch_id(self, batch_id: str) -> ProcessingBatch | None:
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0,
    ) -> list[ProcessingBatch]:
        ...

    @abstractmethod
    async def update_status(
        self, batch_id: str, status: str,
        processed: int, failed: int,
        errors: list[dict], summary: ProcessingSummary | None = None,
    ) -> None:
        ...


class MongoProcessingBatchRepository(ProcessingBatchRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def create(self, batch: ProcessingBatch) -> ProcessingBatch:
        doc = batch.to_mongo()
        result = await self._db.processing_batches.insert_one(doc)
        batch.id = str(result.inserted_id)
        return batch

    async def get_by_batch_id(self, batch_id: str) -> ProcessingBatch | None:
        doc = await self._db.processing_batches.find_one({"batch_id": batch_id})
        return ProcessingBatch.from_mongo(doc) if doc else None

    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0,
    ) -> list[ProcessingBatch]:
        cursor = self._db.processing_batches.find(
            {"user_id": to_object_id(user_id)}
        ).sort("created_at", -1).skip(offset).limit(limit)
        return [ProcessingBatch.from_mongo(doc) async for doc in cursor]

    async def update_status(
        self, batch_id: str, status: str,
        processed: int, failed: int,
        errors: list[dict], summary: ProcessingSummary | None = None,
    ) -> None:
        update = {
            "status": status,
            "processed": processed,
            "failed": failed,
            "errors": errors,
        }
        if summary:
            update["summary"] = summary.model_dump()
        if status in ("completed", "failed"):
            update["completed_at"] = utc_now()
        await self._db.processing_batches.update_one(
            {"batch_id": batch_id},
            {"$set": update},
        )
