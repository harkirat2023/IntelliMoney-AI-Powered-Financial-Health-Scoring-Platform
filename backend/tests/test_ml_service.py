from app.services.category_service import (
    is_valid_category,
    suggest_category,
    suggest_category_detailed,
)


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


def test_ml_detailed_categorization() -> None:
    details = suggest_category_detailed("Swiggy food order delivery")
    assert details["category"] == "Food"
    assert details["confidence"] > 0.4
    assert details["method"] == "ml"


def test_ml_diverse_categories() -> None:
    test_cases = [
        ("Uber cab to international airport", "Transport"),
        ("Monthly electricity BESCOM bill", "Bills"),
        ("Netflix family premium subscription", "Entertainment"),
        ("Apollo pharmacy purchase medicines", "Health"),
        ("Flight ticket booking to Goa", "Travel"),
        ("Apartment house rent payment", "Rent"),
        ("Amazon online shopping for clothes", "Shopping"),
    ]
    for desc, expected in test_cases:
        cat, conf = suggest_category(desc)
        assert cat == expected, f"Expected {expected} for '{desc}', got {cat}"
        assert conf > 0
