from app.core.constants import CATEGORIES
from app.core.exceptions import ValidationException


class ValidationService:
    def validate_bank_transaction(self, tx: dict | None) -> None:
        if not tx:
            raise ValidationException("Bank transaction not found")
        if not tx.get("description"):
            raise ValidationException("Bank transaction description is required")
        if not tx.get("amount"):
            raise ValidationException("Bank transaction amount is required")

    def validate_category(self, category: str) -> str:
        if category and category not in CATEGORIES:
            raise ValidationException(f"Invalid category '{category}'. Must be one of {CATEGORIES}")
        return category

    def validate_tags(self, tags: list[str]) -> list[str]:
        if not tags:
            return []
        for tag in tags:
            if tag and not tag.startswith("#"):
                raise ValidationException(f"Tag '{tag}' must start with #")
        return tags

    def validate_confidence_range(self, score: float) -> float:
        if score < 0.0 or score > 1.0:
            raise ValidationException(f"Confidence score {score} must be between 0.0 and 1.0")
        return round(score, 3)
