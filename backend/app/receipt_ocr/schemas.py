from datetime import datetime

from pydantic import BaseModel, Field


class ReceiptResponse(BaseModel):
    id: str
    filename: str
    mime_type: str = ""
    file_size: int = 0
    merchant_name: str = ""
    total_amount: float = 0.0
    transaction_date: str = ""
    transaction_time: str = ""
    currency: str = "INR"
    tax_amount: float = 0.0
    items: list[dict] = []
    predicted_category: str = ""
    confidence_score: float = 0.0
    status: str = "uploaded"
    extraction_method: str = "ocr"
    raw_ocr_text: str = ""
    image_preview_url: str = ""
    expense_id: str = ""
    error_message: str = ""
    ocr_attempts: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReceiptUpdateRequest(BaseModel):
    merchant_name: str | None = None
    total_amount: float | None = None
    transaction_date: str | None = None
    transaction_time: str | None = None
    currency: str | None = None
    tax_amount: float | None = None
    items: list[dict] | None = None
    predicted_category: str | None = None


class ReceiptUploadResponse(BaseModel):
    receipt: ReceiptResponse
    message: str = "Receipt uploaded successfully"


class ReceiptProcessResponse(BaseModel):
    receipt: ReceiptResponse
    expense_id: str = ""
    message: str = ""


class ReceiptProcessingLogResponse(BaseModel):
    id: str
    receipt_id: str
    action: str
    status: str
    details: str = ""
    duration_ms: int = 0
    created_at: datetime | None = None


class ReceiptListResponse(BaseModel):
    receipts: list[ReceiptResponse] = []
    total: int = 0
