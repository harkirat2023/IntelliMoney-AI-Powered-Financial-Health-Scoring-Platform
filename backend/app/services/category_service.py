"""Deterministic expense categorization.

The previous TF-IDF / Logistic Regression classifier has been removed.
Categorization is now a plain keyword/rule based business-logic function
(no ML, no training artifacts, no scikit-learn). It is used by the
expense routes, the receipt/OCR flow, the import pipeline and the agent's
categorization tool.

The AI agent may additionally explain or refine categories using natural
language, but the deterministic suggestion below remains the source of
truth for default category assignment.
"""

from app.core.constants import CATEGORIES, CATEGORY_KEYWORD_MAP


def suggest_category(description: str) -> tuple[str, float]:
    """Return a (category, confidence) tuple for a transaction description.

    Matching is deterministic: a description is compared against a keyword
    map. When nothing matches, ``Other`` is returned with a low confidence.
    Confidence reflects how specific the match is, never model probability.
    """
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


def is_valid_category(category: str) -> bool:
    return category in CATEGORIES