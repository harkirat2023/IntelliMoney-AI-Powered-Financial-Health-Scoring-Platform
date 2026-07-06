import asyncio
import random
from datetime import datetime, timedelta, timezone

from app.core.exceptions import BankConnectionException
from app.infrastructure.bank_integration.base import BankProviderAdapter
from app.infrastructure.bank_integration.dtos import (
    ConsentInitResponse,
    ConsentStatusResponse,
    ProviderAccount,
    ProviderTransaction,
)


MOCK_ACCOUNTS = [
    ProviderAccount(
        provider_account_id="mock-acc-sbi-001",
        bank_name="State Bank of India",
        masked_account_number="XXXXXX1234",
        account_type="savings",
        account_holder_name="Test User",
        ifsc_code="SBIN0001234",
    ),
    ProviderAccount(
        provider_account_id="mock-acc-hdfc-001",
        bank_name="HDFC Bank",
        masked_account_number="XXXXXX5678",
        account_type="current",
        account_holder_name="Test User",
        ifsc_code="HDFC0005678",
    ),
    ProviderAccount(
        provider_account_id="mock-acc-icici-001",
        bank_name="ICICI Bank",
        masked_account_number="XXXXXX9012",
        account_type="credit_card",
        account_holder_name="Test User",
        ifsc_code="ICIC0009012",
    ),
]

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment"]


class MockBankProvider(BankProviderAdapter):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def initiate_consent(self, user_id: str, consent_version: str, redirect_url: str) -> ConsentInitResponse:
        if random.random() < 0.05:
            raise BankConnectionException("Mock provider temporarily unavailable")
        consent_handle = f"mock-consent-{user_id[:8]}-{random.randint(1000, 9999)}"
        sep = "&" if "?" in redirect_url else "?"
        return ConsentInitResponse(
            consent_handle=consent_handle,
            consent_url=f"{redirect_url}{sep}consent_handle={consent_handle}",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    async def check_consent_status(self, consent_handle: str) -> ConsentStatusResponse:
        await asyncio.sleep(0.5)
        return ConsentStatusResponse(
            status="ACTIVE",
            consent_token=f"mock-token-{consent_handle[-8:]}",
        )

    async def fetch_accounts(self, consent_handle: str, consent_token: str) -> list[ProviderAccount]:
        return MOCK_ACCOUNTS

    async def fetch_transactions(self, consent_handle: str, consent_token: str, account_id: str, from_date: datetime, to_date: datetime) -> list[ProviderTransaction]:
        txs = []
        for i in range(10):
            txs.append(
                ProviderTransaction(
                    transaction_id=f"mock-txn-{account_id}-{i}",
                    description=f"Mock transaction {i}",
                    amount=round(random.uniform(100, 50000), 2),
                    transaction_type=random.choice(["DEBIT", "CREDIT"]),
                    transaction_date=from_date + timedelta(days=random.randint(0, (to_date - from_date).days)),
                    category=random.choice(CATEGORIES),
                )
            )
        return txs

    async def revoke_consent(self, consent_handle: str) -> bool:
        return True
