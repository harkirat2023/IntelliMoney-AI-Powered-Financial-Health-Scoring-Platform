import logging
import time
import uuid
from datetime import datetime
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.infrastructure.messaging.event_bus import event_bus as global_event_bus
from app.infrastructure.messaging.events import Event
from app.infrastructure.storage import get_storage_backend
from app.receipt_ocr.models.receipt_models import Receipt, ReceiptProcessingLog
from app.receipt_ocr.repositories.receipt_repositories import (
    MongoReceiptProcessingLogRepository, MongoReceiptRepository,
)
from app.receipt_ocr.services.image_processing_service import ImageProcessingService
from app.receipt_ocr.services.ocr_service import OCRService
from app.receipt_ocr.services.receipt_validation_service import (
    ReceiptValidationService,
)
from app.services.ml_service import ExpenseCategorizer

logger = logging.getLogger(__name__)


class ReceiptService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._receipt_repo = MongoReceiptRepository(db)
        self._log_repo = MongoReceiptProcessingLogRepository(db)
        self._image_processor = ImageProcessingService()
        self._ocr = OCRService()
        self._validator = ReceiptValidationService()
        self._categorizer = ExpenseCategorizer()
        self._storage = get_storage_backend()

    async def upload(self, user_id: str, file_bytes: bytes, filename: str,
                     content_type: str) -> dict:
        errors = self._validator.validate_image(filename, content_type, len(file_bytes))
        if errors:
            return {"receipt": None, "errors": errors, "message": "; ".join(errors)}

        existing = await self._receipt_repo.get_by_user_and_filename(user_id, filename)
        if existing:
            return {"receipt": None, "errors": ["Duplicate receipt filename. A receipt with this name already exists."],
                    "message": "Duplicate receipt"}

        file_id = uuid.uuid4().hex[:12]
        safe_name = f"{file_id}_{filename}"
        image_path = await self._storage.save(safe_name, file_bytes)

        receipt = Receipt(
            user_id=user_id, image_path=image_path, filename=filename,
            mime_type=content_type, file_size=len(file_bytes),
            image_preview_url=self._storage.get_url(safe_name),
            status="uploaded",
            metadata={"original_filename": filename, "file_id": file_id},
        )
        receipt = await self._receipt_repo.create(receipt)
        image_url = self._storage.get_url(safe_name)
        await self._receipt_repo.update(receipt.id, {"image_preview_url": image_url})
        receipt.image_preview_url = image_url

        await self._log(receipt.id, user_id, "upload", "success",
                        f"Receipt uploaded: {filename} ({len(file_bytes)} bytes)")

        await self._publish_event("receipt.uploaded", user_id, {
            "receipt_id": receipt.id, "filename": filename,
        })

        return {"receipt": receipt, "errors": [], "message": "Receipt uploaded"}

    async def _resolve_image_path(self, image_path: str) -> str:
        if image_path.startswith("http"):
            data = await self._storage.read(image_path)
            if data is None:
                raise FileNotFoundError(f"Image not found in storage: {image_path}")
            tmp = Path(f"/tmp/{uuid.uuid4().hex}.jpg")
            tmp.write_bytes(data)
            return str(tmp)
        return image_path

    async def process(self, receipt_id: str, user_id: str) -> dict:
        receipt = await self._receipt_repo.get_by_id(receipt_id)
        if not receipt or receipt.user_id != user_id:
            return {"receipt": None, "expense_id": "",
                    "errors": ["Receipt not found"], "message": "Receipt not found"}

        if receipt.status == "completed":
            return {"receipt": receipt, "expense_id": receipt.expense_id,
                    "errors": [], "message": "Already processed"}

        start = time.time()
        try:
            await self._receipt_repo.update(receipt_id, {
                "status": "processing", "ocr_attempts": receipt.ocr_attempts + 1,
            })

            local_path = await self._resolve_image_path(receipt.image_path)
            processed_bytes = self._image_processor.preprocess(local_path)
            if not processed_bytes:
                raise RuntimeError("Image preprocessing failed")

            ocr_data = self._ocr.extract(processed_bytes)
            ocr_duration = int((time.time() - start) * 1000)

            receipt.raw_ocr_text = ocr_data.get("raw_text", "")
            receipt.merchant_name = ocr_data.get("merchant_name", "")
            receipt.total_amount = ocr_data.get("total_amount", 0.0)
            receipt.transaction_date = ocr_data.get("transaction_date", "")
            receipt.transaction_time = ocr_data.get("transaction_time", "")
            receipt.currency = ocr_data.get("currency", "INR")
            receipt.tax_amount = ocr_data.get("tax_amount", 0.0)
            receipt.items = ocr_data.get("items", [])

            validation_errors = self._validator.validate_extracted_data({
                "merchant_name": receipt.merchant_name,
                "total_amount": receipt.total_amount,
                "transaction_date": receipt.transaction_date,
            })
            if validation_errors:
                receipt.status = "review_required"
                receipt.error_message = "; ".join(validation_errors)
            else:
                category, confidence = self._categorizer.predict(
                    receipt.merchant_name or receipt.filename)
                receipt.predicted_category = category
                receipt.confidence_score = confidence
                receipt.status = "processed"

            await self._receipt_repo.update(receipt_id, {
                "merchant_name": receipt.merchant_name,
                "total_amount": receipt.total_amount,
                "transaction_date": receipt.transaction_date,
                "transaction_time": receipt.transaction_time,
                "currency": receipt.currency,
                "tax_amount": receipt.tax_amount,
                "items": receipt.items,
                "raw_ocr_text": receipt.raw_ocr_text,
                "predicted_category": receipt.predicted_category,
                "confidence_score": receipt.confidence_score,
                "status": receipt.status,
                "error_message": receipt.error_message,
                "ocr_attempts": receipt.ocr_attempts,
            })

            await self._log(receipt.id, user_id, "ocr_process",
                            "success" if receipt.status != "review_required" else "partial",
                            f"OCR completed: merchant={receipt.merchant_name}, "
                            f"amount={receipt.total_amount}, category={receipt.predicted_category}",
                            duration_ms=ocr_duration)

            await self._publish_event("receipt.processed", user_id, {
                "receipt_id": receipt.id,
                "status": receipt.status,
                "merchant": receipt.merchant_name,
                "amount": receipt.total_amount,
            })

            if receipt.status == "processed":
                expense_id = await self._create_expense(user_id, receipt)
                if expense_id:
                    receipt.expense_id = expense_id
                    await self._receipt_repo.update(receipt.id, {"expense_id": expense_id})

            return {"receipt": receipt, "expense_id": receipt.expense_id,
                    "errors": validation_errors if validation_errors else [],
                    "message": "Processed" if receipt.status != "review_required" else "Review required"}

        except Exception as e:
            logger.error(f"Receipt processing failed: {e}")
            await self._receipt_repo.update(receipt_id, {
                "status": "failed", "error_message": str(e),
            })
            await self._log(receipt_id, user_id, "ocr_process", "failed",
                            f"Error: {e}", duration_ms=int((time.time() - start) * 1000))
            return {"receipt": None, "expense_id": "",
                    "errors": [str(e)], "message": "Processing failed"}

    async def confirm_and_finalize(self, receipt_id: str, user_id: str) -> dict:
        receipt = await self._receipt_repo.get_by_id(receipt_id)
        if not receipt or receipt.user_id != user_id:
            return {"receipt": None, "expense_id": "", "errors": ["Receipt not found"],
                    "message": "Receipt not found"}

        if receipt.status == "completed":
            return {"receipt": receipt, "expense_id": receipt.expense_id,
                    "errors": [], "message": "Already completed"}

        if not receipt.predicted_category:
            category, confidence = self._categorizer.predict(
                receipt.merchant_name or receipt.filename)
            receipt.predicted_category = category
            receipt.confidence_score = confidence

        expense_id = await self._create_expense(user_id, receipt)
        await self._receipt_repo.update(receipt_id, {
            "status": "completed", "expense_id": expense_id,
            "predicted_category": receipt.predicted_category,
            "confidence_score": receipt.confidence_score,
        })
        receipt.expense_id = expense_id
        receipt.status = "completed"

        await self._log(receipt_id, user_id, "confirm", "success",
                        f"Expense created: {expense_id}")

        await self._publish_event("receipt.completed", user_id, {
            "receipt_id": receipt.id, "expense_id": expense_id,
        })

        return {"receipt": receipt, "expense_id": expense_id,
                "errors": [], "message": "Expense created"}

    async def update_receipt(self, receipt_id: str, user_id: str,
                             data: dict) -> Receipt | None:
        receipt = await self._receipt_repo.get_by_id(receipt_id)
        if not receipt or receipt.user_id != user_id:
            return None

        upd = {}
        for field in ("merchant_name", "total_amount", "transaction_date",
                       "transaction_time", "currency", "tax_amount", "items",
                       "predicted_category"):
            if field in data:
                upd[field] = data[field]
        if "total_amount" in upd:
            upd["total_amount"] = float(upd["total_amount"])
        if "items" in upd and isinstance(upd["items"], list):
            upd["items"] = [dict(i) if not isinstance(i, dict) else i for i in upd["items"]]

        if not upd:
            return receipt

        if "predicted_category" in upd:
            receipt.predicted_category = upd["predicted_category"]
        else:
            category, confidence = self._categorizer.predict(
                upd.get("merchant_name", receipt.merchant_name) or receipt.filename)
            upd["predicted_category"] = category
            upd["confidence_score"] = confidence

        await self._receipt_repo.update(receipt_id, upd)
        await self._log(receipt_id, user_id, "update", "success",
                        f"Fields updated: {', '.join(upd.keys())}")

        return await self._receipt_repo.get_by_id(receipt_id)

    async def delete_receipt(self, receipt_id: str, user_id: str) -> bool:
        receipt = await self._receipt_repo.get_by_id(receipt_id)
        if not receipt or receipt.user_id != user_id:
            return False

        try:
            await self._storage.delete(receipt.image_path)
        except Exception as e:
            logger.warning(f"Failed to delete receipt image: {e}")

        await self._receipt_repo.delete(receipt_id)
        await self._log(receipt_id, user_id, "delete", "success", "Receipt deleted")
        return True

    async def get_receipt(self, receipt_id: str, user_id: str) -> Receipt | None:
        receipt = await self._receipt_repo.get_by_id(receipt_id)
        if not receipt or receipt.user_id != user_id:
            return None
        return receipt

    async def get_receipts(self, user_id: str, status: str | None = None) -> list[Receipt]:
        return await self._receipt_repo.get_by_user(user_id, status)

    def _receipt_to_dict(self, receipt: Receipt) -> dict:
        return {k: v for k, v in receipt.__dict__.items() if not k.startswith("_")}

    async def _create_expense(self, user_id: str, receipt: Receipt) -> str | None:
        try:
            tx_date = datetime.utcnow()
            if receipt.transaction_date:
                try:
                    tx_date = datetime.strptime(receipt.transaction_date, "%Y-%m-%d")
                except ValueError:
                    pass
            from datetime import date as date_type
            expense_doc = {
                "user_id": user_id,
                "amount": receipt.total_amount,
                "description": f"{receipt.merchant_name or receipt.filename} (via Receipt OCR)",
                "category": receipt.predicted_category or "Other",
                "payment_method": "Receipt OCR",
                "date": date_type(tx_date.year, tx_date.month, tx_date.day),
                "created_at": datetime.utcnow(),
            }
            result = await self._db.expenses.insert_one(expense_doc)
            expense_id = str(result.inserted_id)

            await self._publish_event("expense.created", user_id, {
                "expense_id": expense_id, "amount": receipt.total_amount,
                "category": receipt.predicted_category, "source": "receipt_ocr",
            })
            return expense_id
        except Exception as e:
            logger.error(f"Expense creation failed: {e}")
            return None

    async def _log(self, receipt_id: str, user_id: str, action: str,
                   status: str, details: str = "", duration_ms: int = 0):
        log_entry = ReceiptProcessingLog(
            receipt_id=receipt_id, user_id=user_id, action=action,
            status=status, details=details[:500], duration_ms=duration_ms,
        )
        await self._log_repo.create(log_entry)

    async def _publish_event(self, event_type: str, user_id: str, payload: dict):
        event = Event(event_type=event_type, user_id=user_id, payload=payload)
        await global_event_bus.publish(event)
