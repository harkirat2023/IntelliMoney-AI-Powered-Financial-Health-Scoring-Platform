import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class ReceiptValidationService:
    def validate_image(self, filename: str, content_type: str, file_size: int) -> list[str]:
        errors = []
        ext = Path(filename).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"):
            errors.append(f"Unsupported file format: {ext}. Use JPG, PNG, BMP, TIFF, or WebP.")
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            errors.append(f"Unsupported MIME type: {content_type}")
        if file_size > MAX_FILE_SIZE:
            errors.append(f"File too large ({file_size / 1024 / 1024:.1f} MB). Max 10 MB.")
        if file_size == 0:
            errors.append("File is empty.")
        return errors

    def validate_extracted_data(self, data: dict) -> list[str]:
        errors = []
        if not data.get("merchant_name"):
            errors.append("Merchant name could not be extracted.")
        if not data.get("total_amount") or data["total_amount"] <= 0:
            errors.append("Total amount could not be extracted or is zero.")
        if not data.get("transaction_date"):
            errors.append("Transaction date could not be extracted.")
        return errors

    def validate_update_data(self, data: dict) -> list[str]:
        errors = []
        if "total_amount" in data and data["total_amount"] is not None:
            if data["total_amount"] <= 0:
                errors.append("Total amount must be greater than zero.")
            if data["total_amount"] > 99999999:
                errors.append("Total amount seems unrealistically high.")
        if "merchant_name" in data and data["merchant_name"] is not None:
            if len(data["merchant_name"].strip()) < 2:
                errors.append("Merchant name is too short.")
        return errors
