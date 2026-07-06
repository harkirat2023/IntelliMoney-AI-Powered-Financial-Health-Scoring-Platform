from datetime import datetime


RECEIPT_STATUSES = ["uploaded", "processing", "processed", "review_required", "completed", "failed"]
EXTRACTION_METHODS = ["ocr", "manual", "auto"]


class Receipt:
    def __init__(self, user_id: str, image_path: str, filename: str,
                 mime_type: str = "", file_size: int = 0,
                 merchant_name: str = "", total_amount: float = 0.0,
                 transaction_date: str = "", transaction_time: str = "",
                 currency: str = "INR",
                 tax_amount: float = 0.0, items: list[dict] | None = None,
                 predicted_category: str = "", confidence_score: float = 0.0,
                 status: str = "uploaded",
                 extraction_method: str = "ocr",
                 raw_ocr_text: str = "",
                 image_preview_url: str = "",
                 expense_id: str = "",
                 error_message: str = "",
                 ocr_attempts: int = 0,
                 metadata: dict | None = None,
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.image_path = image_path
        self.filename = filename
        self.mime_type = mime_type
        self.file_size = file_size
        self.merchant_name = merchant_name
        self.total_amount = total_amount
        self.transaction_date = transaction_date
        self.transaction_time = transaction_time
        self.currency = currency
        self.tax_amount = tax_amount
        self.items = items or []
        self.predicted_category = predicted_category
        self.confidence_score = confidence_score
        self.status = status
        self.extraction_method = extraction_method
        self.raw_ocr_text = raw_ocr_text
        self.image_preview_url = image_preview_url
        self.expense_id = expense_id
        self.error_message = error_message
        self.ocr_attempts = ocr_attempts
        self.metadata = metadata or {}
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "Receipt":
        return cls(id=str(doc.get("_id", "")), user_id=str(doc.get("user_id", "")),
                   image_path=doc.get("image_path", ""), filename=doc.get("filename", ""),
                   mime_type=doc.get("mime_type", ""), file_size=doc.get("file_size", 0),
                   merchant_name=doc.get("merchant_name", ""),
                   total_amount=doc.get("total_amount", 0.0),
                   transaction_date=doc.get("transaction_date", ""),
                   transaction_time=doc.get("transaction_time", ""),
                   currency=doc.get("currency", "INR"),
                   tax_amount=doc.get("tax_amount", 0.0),
                   items=doc.get("items", []),
                   predicted_category=doc.get("predicted_category", ""),
                   confidence_score=doc.get("confidence_score", 0.0),
                   status=doc.get("status", "uploaded"),
                   extraction_method=doc.get("extraction_method", "ocr"),
                   raw_ocr_text=doc.get("raw_ocr_text", ""),
                   image_preview_url=doc.get("image_preview_url", ""),
                   expense_id=doc.get("expense_id", ""),
                   error_message=doc.get("error_message", ""),
                   ocr_attempts=doc.get("ocr_attempts", 0),
                   metadata=doc.get("metadata", {}),
                   created_at=doc.get("created_at"), updated_at=doc.get("updated_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "image_path": self.image_path,
             "filename": self.filename, "mime_type": self.mime_type,
             "file_size": self.file_size, "merchant_name": self.merchant_name,
             "total_amount": self.total_amount,
             "transaction_date": self.transaction_date,
             "transaction_time": self.transaction_time,
             "currency": self.currency, "tax_amount": self.tax_amount,
             "items": self.items, "predicted_category": self.predicted_category,
             "confidence_score": self.confidence_score, "status": self.status,
             "extraction_method": self.extraction_method,
             "raw_ocr_text": self.raw_ocr_text,
             "image_preview_url": self.image_preview_url,
             "expense_id": self.expense_id, "error_message": self.error_message,
             "ocr_attempts": self.ocr_attempts, "metadata": self.metadata,
             "created_at": self.created_at, "updated_at": self.updated_at}
        if self.id:
            d["_id"] = self.id
        return d


class ReceiptProcessingLog:
    def __init__(self, receipt_id: str, user_id: str, action: str,
                 status: str, details: str = "",
                 duration_ms: int = 0,
                 created_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.receipt_id = receipt_id
        self.user_id = user_id
        self.action = action
        self.status = status
        self.details = details
        self.duration_ms = duration_ms
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "ReceiptProcessingLog":
        return cls(id=str(doc.get("_id", "")), receipt_id=str(doc.get("receipt_id", "")),
                   user_id=str(doc.get("user_id", "")), action=doc.get("action", ""),
                   status=doc.get("status", ""), details=doc.get("details", ""),
                   duration_ms=doc.get("duration_ms", 0),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"receipt_id": self.receipt_id, "user_id": self.user_id,
             "action": self.action, "status": self.status,
             "details": self.details, "duration_ms": self.duration_ms,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d
