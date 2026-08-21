"""Check that merchant keywords produce the expected categories."""

import pytest

from app.services.categorizer import categorize_transaction


@pytest.mark.parametrize(
    ("merchant", "expected"),
    [
        ("Starbucks", "Food & Dining"),
        ("LOCAL RESTAURANT", "Food & Dining"),
        ("Uber Trip", "Transportation"),
        ("Lyft", "Transportation"),
        ("Walmart", "Groceries"),
        ("Neighbourhood Grocery", "Groceries"),
        ("Unknown Shop", "Uncategorized"),
    ],
)
def test_categorize_transaction(merchant, expected):
    assert categorize_transaction(merchant) == expected
