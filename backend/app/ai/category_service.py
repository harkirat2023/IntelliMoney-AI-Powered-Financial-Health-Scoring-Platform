from app.core.constants import CATEGORIES, CATEGORY_KEYWORD_MAP
from app.core.logging import logger
from app.services.category_service import suggest_category


class CategoryPredictionService:
    """Assigns categories to imported transactions using deterministic rules.

    The old TF-IDF / Logistic Regression categorizer was removed. This
    service uses the keyword/rule based ``suggest_category`` business
    logic and records the outcome for the processing pipeline.
    """

    def predict(self, description: str, merchant_category: str | None = None) -> tuple[str, float]:
        if merchant_category and merchant_category in CATEGORIES:
            logger.info("Category from merchant override", extra={
                "description": description, "merchant_category": merchant_category,
            })
            return merchant_category, 0.90
        category, confidence = suggest_category(description)
        logger.info("Category from deterministic suggestion", extra={
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