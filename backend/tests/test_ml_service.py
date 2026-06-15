from app.services.ml_service import categorizer


def test_fallback_predicts_known_category() -> None:
    category, confidence = categorizer.predict("uber ride to office")
    assert category == "Transport"
    assert confidence > 0


def test_empty_text_returns_other() -> None:
    category, confidence = categorizer.predict("   ")
    assert category == "Other"
    assert confidence == 0
