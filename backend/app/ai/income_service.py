from app.core.logging import logger


class IncomeDetectionService:
    REFUND_KEYWORDS = [
        "refund", "cashback", "reversal", "return", "cancellation",
    ]

    TRANSFER_KEYWORDS = [
        "transfer to", "transfer from", "neft", "imps", "rtgs",
        "self transfer", "own account",
    ]

    REVERSAL_KEYWORDS = [
        "reversal", "chargeback", "failed", "returned", "cancelled",
        "txn failed", "debited back",
    ]

    def classify(
        self,
        transaction_type: str,
        description: str,
    ) -> dict:
        desc_lower = description.lower()
        result = {
            "is_income": False,
            "is_refund": False,
            "is_transfer": False,
            "tags": [],
        }

        if transaction_type == "CREDIT":
            if any(kw in desc_lower for kw in self.REVERSAL_KEYWORDS):
                logger.info("CREDIT classified as reversal (not income)", extra={
                    "description": description,
                })
            elif any(kw in desc_lower for kw in self.REFUND_KEYWORDS):
                result["is_refund"] = True
                result["tags"].append("#refund")
                logger.info("CREDIT classified as refund", extra={"description": description})
            elif any(kw in desc_lower for kw in self.TRANSFER_KEYWORDS):
                result["is_transfer"] = True
                result["tags"].append("#transfer")
                logger.info("CREDIT classified as transfer", extra={"description": description})
            else:
                result["is_income"] = True
                if any(kw in desc_lower for kw in ["salary", "salary credit"]):
                    result["tags"].append("#salary")
                logger.info("CREDIT classified as income", extra={"description": description})

        return result
