from pathlib import Path

import joblib

from app.core.config import get_settings
from app.core.constants import CATEGORIES, CATEGORY_KEYWORD_MAP


MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "expense_classifier.joblib"


class ExpenseCategorizer:
    def __init__(self) -> None:
        self._model = None

    def load(self) -> None:
        if not MODEL_PATH.exists():
            settings = get_settings()
            if settings.ml_allow_fallback:
                return
            raise RuntimeError(
                f"ML model not found at {MODEL_PATH}. "
                f"The model must be generated during build by running `python ml/train_model.py`. "
                f"Set ML_ALLOW_FALLBACK=true to use keyword-based fallback instead."
            )
        self._model = joblib.load(MODEL_PATH)

    def predict(self, description: str) -> tuple[str, float]:
        text = description.strip()
        if not text:
            return "Other", 0.0
        if self._model is None:
            self.load()
        if self._model is None:
            return self._fallback_predict(text), 0.45

        prediction = self._model.predict([text])[0]
        confidence = 0.75
        if hasattr(self._model, "predict_proba"):
            probabilities = self._model.predict_proba([text])[0]
            confidence = float(max(probabilities))
        category = str(prediction)
        return (category if category in CATEGORIES else "Other"), round(confidence, 3)

    def _fallback_predict(self, text: str) -> str:
        normalized = text.lower()
        for category, keywords in CATEGORY_KEYWORD_MAP.items():
            if any(keyword in normalized for keyword in keywords):
                return category
        return "Other"


categorizer = ExpenseCategorizer()
