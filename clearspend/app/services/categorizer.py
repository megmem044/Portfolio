"""Assign a category by matching ordered keywords in a merchant name."""

from collections.abc import Iterable


DEFAULT_RULES = (
    ("starbucks", "Food & Dining"),
    ("restaurant", "Food & Dining"),
    ("uber", "Transportation"),
    ("lyft", "Transportation"),
    ("walmart", "Groceries"),
    ("grocery", "Groceries"),
)


def categorize_transaction(
    merchant: str,
    rules: Iterable[tuple[str, str]] | None = None,
) -> str:
    """Return the first category whose keyword appears in the merchant name."""
    normalized_merchant = merchant.casefold()
    active_rules = rules if rules is not None else DEFAULT_RULES

    for keyword, category in active_rules:
        if keyword.casefold() in normalized_merchant:
            return category

    return "Uncategorized"
