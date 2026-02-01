# Transaction categorization logic is defined in this file
# Simple rule-based categorization is used

def categorize_transaction(merchant: str) -> str:
    # Merchant name is normalized to lowercase
    merchant_lower = merchant.lower()

    # Food and dining category is detected
    if "starbucks" in merchant_lower or "restaurant" in merchant_lower:
        return "Food & Dining"

    # Transportation category is detected
    if "uber" in merchant_lower or "lyft" in merchant_lower:
        return "Transportation"

    # Grocery category is detected
    if "walmart" in merchant_lower or "grocery" in merchant_lower:
        return "Groceries"

    # Default category is assigned when no rule matches
    return "Uncategorized"
