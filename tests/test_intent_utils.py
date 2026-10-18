from app.intent_utils import normalize_intent


def test_normalizes_sales():
    assert normalize_intent("Sales") == "sales"


def test_removes_surrounding_whitespace():
    assert normalize_intent("  sales  ") == "sales"


def test_normalizes_personal_loan():
    assert normalize_intent("PERSONAL_LOAN") == "personal_loan"


def test_handles_empty_string():
    assert normalize_intent("") == ""