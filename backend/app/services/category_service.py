"""Expense categorization with ML model and keyword fallback.

Uses a TF-IDF + Logistic Regression model when available, otherwise falls
back to deterministic keyword matching. The ML model is loaded lazily on
first use and cached for subsequent calls.
"""

import logging
from pathlib import Path
from typing import Optional

import joblib
from app.core.config import get_settings
from app.core.constants import CATEGORIES, CATEGORY_KEYWORD_MAP

logger = logging.getLogger(__name__)

_MODEL: Optional[object] = None
_MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "expense_classifier.joblib"


def _load_model():
    """Load the ML model if available, return None if not."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not _MODEL_PATH.exists():
        logger.warning("ML model not found at %s, using keyword fallback", _MODEL_PATH)
        return None
    try:
        _MODEL = joblib.load(_MODEL_PATH)
        logger.info("Loaded ML expense classifier from %s", _MODEL_PATH)
    except Exception as exc:
        logger.error("Failed to load ML model: %s", exc)
        _MODEL = None
    return _MODEL


def _keyword_fallback(description: str) -> tuple[str, float]:
    """Deterministic keyword-based categorization."""
    text = (description or "").strip()
    if not text:
        return "Other", 0.0

    normalized = text.lower()
    best_category = "Other"
    best_score = 0
    best_keywords = 0

    for category, keywords in CATEGORY_KEYWORD_MAP.items():
        matched = [kw for kw in keywords if kw in normalized]
        if not matched:
            continue
        score = len(matched)
        if score > best_score or (score == best_score and len(matched) > best_keywords):
            best_category = category
            best_score = score
            best_keywords = len(matched)

    if best_score == 0:
        return "Other", 0.1

    confidence = min(0.95, 0.55 + 0.12 * best_score)
    return best_category, round(confidence, 3)


def suggest_category(description: str) -> tuple[str, float]:
    """Return a (category, confidence) tuple for a transaction description.

    First tries the ML model if available and enabled. Falls back to
    deterministic keyword matching if ML is unavailable or disabled.
    """
    cfg = get_settings()
    if cfg.ml_allow_fallback:
        model = _load_model()
        if model is not None:
            try:
                pred = model.predict([description])[0]
                prob = model.predict_proba([description])[0].max()
                category = str(pred)
                confidence = round(float(prob), 3)
                if category in CATEGORIES:
                    return category, confidence
            except Exception as exc:
                logger.warning("ML prediction failed, falling back to keywords: %s", exc)

    return _keyword_fallback(description)


def is_valid_category(category: str) -> bool:
    return category in CATEGORIES