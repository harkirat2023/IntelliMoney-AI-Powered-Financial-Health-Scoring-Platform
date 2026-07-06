from app.core.constants import CATEGORIES, CATEGORY_KEYWORD_MAP
from app.core.logging import logger
from app.services.ml_service import categorizer


class CategoryPredictionService:
    def predict(self, description: str, merchant_category: str | None = None) -> tuple[str, float]:
        if merchant_category and merchant_category in CATEGORIES:
            logger.info("Category from merchant override", extra={
                "description": description, "merchant_category": merchant_category,
            })
            return merchant_category, 0.90
        category, confidence = categorizer.predict(description)
        logger.info("Category from ML prediction", extra={
            "description": description, "category": category, "confidence": confidence,
        })
        return category, confidence

    def get_keyword_confidence(self, description: str, assigned_category: str) -> float:
        if not description:
            return 0.0
        normalized = description.lower()
        keywords = CATEGORY_KEYWORD_MAP.get(assigned_category)
        if not keywords:
            return 0.0
        matched = sum(1 for kw in keywords if kw in normalized)
        return round(matched / len(keywords), 3)
