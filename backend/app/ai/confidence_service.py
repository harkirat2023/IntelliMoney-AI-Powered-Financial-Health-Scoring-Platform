from app.core.constants import (
    CONFIDENCE_THRESHOLDS,
    MERCHANT_CONFIDENCE_WEIGHTS,
    CATEGORIES,
)
from app.core.logging import logger


class ConfidenceService:
    def calculate(
        self,
        merchant_confidence: float = 0.0,
        merchant_category: str | None = None,
        ml_confidence: float = 0.0,
        ml_category: str | None = None,
        is_recurring: bool = False,
        keyword_confidence: float = 0.0,
        amount_normalcy: float = 0.5,
    ) -> dict:
        scores = {}

        has_merchant = merchant_confidence > 0
        merchant_is_known = merchant_category in CATEGORIES if merchant_category else False
        scores["merchant"] = merchant_confidence if (has_merchant and merchant_is_known) else 0.0

        scores["ml_probability"] = ml_confidence if (ml_category and ml_confidence > 0) else 0.0

        scores["recurring"] = 0.85 if is_recurring else 0.0

        scores["keyword"] = keyword_confidence

        scores["amount_normalcy"] = amount_normalcy

        total = sum(
            scores[k] * MERCHANT_CONFIDENCE_WEIGHTS.get(k, 0.0)
            for k in MERCHANT_CONFIDENCE_WEIGHTS
        )
        confidence_score = round(min(total, 1.0), 3)

        logger.info("Confidence score calculated", extra={
            "score": confidence_score, "breakdown": scores,
        })

        return {
            "score": confidence_score,
            "breakdown": scores,
        }

    def determine_review_status(self, confidence_score: float) -> str:
        if confidence_score >= CONFIDENCE_THRESHOLDS["auto_approved"]:
            return "auto_approved"
        elif confidence_score >= CONFIDENCE_THRESHOLDS["approved"]:
            return "approved"
        return "review_required"
