from app.services.category_service import is_valid_category, suggest_category


def test_suggests_known_category() -> None:
    category, confidence = suggest_category("uber ride to office")
    assert category == "Transport"
    assert confidence > 0
    assert is_valid_category(category)


def test_empty_text_returns_other() -> None:
    category, confidence = suggest_category("   ")
    assert category == "Other"
    assert confidence == 0


def test_unknown_text_returns_other() -> None:
    category, confidence = suggest_category("random unknown text")
    assert category == "Other"
    assert confidence > 0


def test_multiple_keywords_increase_confidence() -> None:
    single = suggest_category("coffee")
    multi = suggest_category("coffee restaurant dinner")
    assert single[1] < multi[1]