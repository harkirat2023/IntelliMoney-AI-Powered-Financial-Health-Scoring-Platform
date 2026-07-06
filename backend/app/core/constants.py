PAYMENT_METHODS = ["Cash", "Card", "UPI", "Bank Transfer", "Wallet", "Other"]

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Travel",
    "Rent",
    "Other",
]

SUBSCRIPTION_CATEGORIES = [
    "Entertainment", "Software", "Utilities", "Health", "Education", "Shopping", "Other",
]

FREQUENCIES = ["weekly", "biweekly", "monthly", "yearly"]

SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

RISK_LEVELS = ["Excellent", "Good", "Moderate", "Needs Attention"]

ANOMALY_THRESHOLDS = {
    "low": 50,
    "medium": 100,
    "high": 200,
    "critical": 300,
}

REPORT_TYPES = ["weekly", "monthly"]

BUDGET_STATES = ["safe", "warning", "over"]

CONFIDENCE_THRESHOLDS = {
    "auto_approved": 0.95,
    "approved": 0.70,
    "review_required": 0.00,
}

REVIEW_STATUSES = ["auto_approved", "approved", "review_required"]

TRANSACTION_TAGS = [
    "#subscription", "#utility", "#rent", "#salary",
    "#refund", "#transfer", "#tax-deductible", "#business",
    "#reimbursement", "#one-time",
]

CATEGORY_KEYWORD_MAP = {
    "Food": ["coffee", "restaurant", "pizza", "burger", "grocery", "lunch", "dinner"],
    "Transport": ["uber", "ola", "metro", "fuel", "bus", "taxi", "train"],
    "Shopping": ["amazon", "flipkart", "clothes", "mall", "shoes"],
    "Bills": ["electricity", "internet", "phone", "water", "bill", "recharge"],
    "Entertainment": ["movie", "netflix", "spotify", "game", "concert"],
    "Health": ["doctor", "pharmacy", "medicine", "hospital", "clinic"],
    "Education": ["course", "book", "tuition", "exam", "college"],
    "Travel": ["flight", "hotel", "trip", "airbnb", "booking"],
    "Rent": ["rent", "landlord", "apartment"],
}

MERCHANT_CONFIDENCE_WEIGHTS = {
    "merchant": 0.40,
    "ml_probability": 0.35,
    "recurring": 0.10,
    "keyword": 0.10,
    "amount_normalcy": 0.05,
}
