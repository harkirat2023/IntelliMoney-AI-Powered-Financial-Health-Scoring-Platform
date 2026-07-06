import re
from datetime import datetime, timedelta

from app.infrastructure.bank_integration.merchant.merchant_data import (
    AliasEntry,
    MerchantEntry,
    get_all_merchants,
)


class MerchantResult:
    def __init__(
        self,
        cleaned_merchant: str = "",
        normalized_merchant: str = "",
        merchant_id: str | None = None,
        category: str | None = None,
        confidence: float = 0.0,
    ):
        self.cleaned_merchant = cleaned_merchant
        self.normalized_merchant = normalized_merchant
        self.merchant_id = merchant_id
        self.category = category
        self.confidence = confidence


class MerchantNormalizer:
    def __init__(self):
        self._merchants: dict[str, MerchantEntry] = {}
        self._aliases: list[tuple[str, AliasEntry, str, str]] = []
        self._last_refresh: datetime | None = None
        self._ttl_seconds = 300

    def _load_merchants(self) -> None:
        now = datetime.now()
        if self._last_refresh and (now - self._last_refresh).total_seconds() < self._ttl_seconds:
            return
        self._merchants = {}
        self._aliases = []
        for key, entry in get_all_merchants().items():
            self._merchants[key] = entry
            for alias in entry.aliases:
                self._aliases.append((key, alias, entry.display_name, entry.category))
        self._aliases.sort(key=lambda x: x[1].priority, reverse=True)
        self._last_refresh = now

    def _clean_description(self, description: str) -> str:
        text = description.strip()
        text = re.sub(r'/[A-Z]+$', '', text)
        upi_match = re.search(r'\*([a-z]+)\*', text, re.IGNORECASE)
        if upi_match:
            text = upi_match.group(1)
        city_match = re.search(r'^([A-Za-z\s]+?)\s+[A-Z]{2,3}\s+IN', text)
        if city_match:
            text = city_match.group(1).strip()
        text = re.sub(r'[^a-zA-Z0-9\s\.]', '', text)
        return text.lower().strip()

    def normalize(self, description: str) -> MerchantResult:
        self._load_merchants()
        cleaned = self._clean_description(description)
        if not cleaned:
            return MerchantResult(confidence=0.0)

        for key, alias, display_name, category in self._aliases:
            if alias.alias_type == "exact" and cleaned == alias.pattern:
                return MerchantResult(cleaned, display_name, key, category, 1.0)
            if alias.alias_type == "contains" and alias.pattern in cleaned:
                return MerchantResult(cleaned, display_name, key, category, 0.85)
            if alias.alias_type == "regex":
                try:
                    if re.search(alias.pattern, cleaned):
                        return MerchantResult(cleaned, display_name, key, category, 0.85)
                except re.error:
                    pass

        return MerchantResult(cleaned, cleaned, None, None, 0.0)
