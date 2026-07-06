from app.core.logging import logger


class RecurringDetectionService:
    KNOWN_SUBSCRIPTIONS: dict[str, list[float]] = {
        "Netflix": [649.0, 199.0, 499.0, 799.0],
        "Spotify": [119.0, 59.0],
        "Google One": [130.0, 65.0],
        "Amazon Prime": [1499.0, 299.0, 599.0],
        "Disney+ Hotstar": [1499.0, 899.0, 299.0],
        "Apple": [99.0, 249.0],
        "ZEE5": [999.0, 299.0],
        "Sony LIV": [999.0, 499.0],
    }

    UTILITY_KEYWORDS = [
        "electricity", "water bill", "internet", "broadband",
        "mobile recharge", "dth", "gas", "insurance",
    ]

    RENT_KEYWORDS = ["rent", "landlord"]

    def detect(
        self,
        normalized_merchant: str,
        amount: float,
        description: str,
    ) -> tuple[bool, list[str]]:
        is_recurring = False
        tags = []
        merchant_lower = normalized_merchant.lower()
        desc_lower = description.lower()

        for sub_name, amounts in self.KNOWN_SUBSCRIPTIONS.items():
            if sub_name.lower() in merchant_lower:
                for sub_amount in amounts:
                    positive_amount = abs(amount)
                    if sub_amount > 0 and abs(positive_amount - sub_amount) / sub_amount <= 0.05:
                        is_recurring = True
                        tags.append("#subscription")
                        break

        for kw in self.UTILITY_KEYWORDS:
            if kw in desc_lower:
                is_recurring = True
                tags.append("#utility")
                break

        for kw in self.RENT_KEYWORDS:
            if kw in desc_lower:
                is_recurring = True
                tags.append("#rent")
                break

        if is_recurring:
            logger.info("Recurring transaction detected", extra={
                "merchant": normalized_merchant, "amount": amount, "tags": tags,
            })

        return is_recurring, tags
