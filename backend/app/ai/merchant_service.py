from app.infrastructure.bank_integration.merchant.merchant_normalizer import (
    MerchantNormalizer,
    MerchantResult,
)


class MerchantNormalizationService:
    def __init__(self):
        self._normalizer = MerchantNormalizer()

    def normalize(self, description: str) -> MerchantResult:
        return self._normalizer.normalize(description)
