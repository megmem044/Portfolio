CATEGORY_RULES = {
    "Food & Dining": ("starbucks", "restaurant"),
    "Transportation": ("uber", "lyft"),
    "Groceries": ("walmart", "grocery"),
}


def categorize_transaction(merchant: str) -> str:
    """Return the first category whose keyword appears in the merchant name."""
    normalized_merchant = merchant.casefold()

    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in normalized_merchant for keyword in keywords):
            return category

    return "Uncategorized"
