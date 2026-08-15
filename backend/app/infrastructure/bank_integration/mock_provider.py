import asyncio
import hashlib
import random
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.exceptions import BankConnectionException
from app.infrastructure.bank_integration.base import BankProviderAdapter
from app.infrastructure.bank_integration.dtos import (
    ConsentInitResponse,
    ConsentStatusResponse,
    ProviderAccount,
    ProviderTransaction,
)

IST = ZoneInfo("Asia/Kolkata")

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

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Education", "Travel", "Rent", "Other"]

# Fixed monthly entries: (day_of_month, description, category, base_amount, variance, direction)
FIXED_MONTHLY = {
    "mock-acc-sbi-001": [
        (1, "ACME CORP SALARY", "Income", 85000, 0, "CREDIT"),
        (1, "RENT PAYMENT - SUNRISE APARTMENTS", "Rent", 22000, 0, "DEBIT"),
        (5, "NETFLIX SUBSCRIPTION", "Entertainment", 649, 0, "DEBIT"),
        (8, "SPOTIFY PREMIUM", "Entertainment", 119, 0, "DEBIT"),
        (10, "RELIANCE JIO POSTPAID", "Bills", 899, 0, "DEBIT"),
        (12, "TATA POWER ELECTRICITY", "Bills", 1500, 600, "DEBIT"),
        (15, "AIRTEL BROADBAND", "Bills", 1099, 0, "DEBIT"),
        (20, "AMAZON PRIME MEMBERSHIP", "Entertainment", 149, 0, "DEBIT"),
        (25, "LIC PREMIUM PAYMENT", "Investment", 2500, 0, "DEBIT"),
    ],
    "mock-acc-hdfc-001": [
        (2, "CLIENT PAYMENT - BLUEPRINT TECH", "Income", 45000, 20000, "CREDIT"),
        (16, "CLIENT PAYMENT - NOVA SOLUTIONS", "Income", 35000, 15000, "CREDIT"),
        (5, "OFFICE RENT - COWORK SPACE", "Rent", 18000, 0, "DEBIT"),
        (10, "OFFICE SUPPLIES - STATIONERY", "Shopping", 1200, 800, "DEBIT"),
        (25, "GST FILING CHARGES", "Other", 750, 250, "DEBIT"),
    ],
    "mock-acc-icici-001": [
        (3, "CREDIT CARD BILL PAYMENT", "Bills", 42000, 12000, "CREDIT"),
    ],
}

# Variable transaction templates: (description, category, min_amount, max_amount, direction, frequency_per_week)
VARIABLE_TEMPLATES = {
    "mock-acc-sbi-001": [
        ("SWIGGY ORDER", "Food", 150, 450, "DEBIT", 2),
        ("ZOMATO ORDER", "Food", 200, 500, "DEBIT", 2),
        ("DOMINOS PIZZA", "Food", 250, 550, "DEBIT", 1),
        ("BIGBASKET GROCERIES", "Food", 800, 1800, "DEBIT", 1),
        ("DMART GROCERY", "Food", 600, 1400, "DEBIT", 1),
        ("CAFE COFFEE DAY", "Food", 150, 350, "DEBIT", 1),
        ("UBER INDIA", "Transport", 120, 350, "DEBIT", 1),
        ("RAPIDO BIKE", "Transport", 40, 140, "DEBIT", 2),
        ("INDIAN OIL PETROL", "Transport", 800, 1500, "DEBIT", 1),
        ("NHAI FASTAG RECHARGE", "Transport", 400, 700, "DEBIT", 1),
        ("AMAZON PAY", "Shopping", 300, 2500, "DEBIT", 1),
        ("FLIPKART", "Shopping", 400, 2200, "DEBIT", 1),
        ("MYNTRA FASHION", "Shopping", 500, 2500, "DEBIT", 1),
        ("APOLLO PHARMACY", "Health", 200, 700, "DEBIT", 1),
        ("PVR CINEMAS", "Entertainment", 250, 700, "DEBIT", 1),
        ("BOOK MY SHOW", "Entertainment", 300, 900, "DEBIT", 1),
    ],
    "mock-acc-hdfc-001": [
        ("VENDOR PAYMENT - SUPPLY CO", "Shopping", 8000, 25000, "DEBIT", 1),
        ("HARDWARE STORE PURCHASE", "Shopping", 1500, 8000, "DEBIT", 1),
        ("FUEL - HP PETROL", "Transport", 1000, 2000, "DEBIT", 1),
        ("CLIENT LUNCH MEETING", "Food", 500, 1500, "DEBIT", 1),
        ("TECH SUPPORT SERVICES", "Other", 1000, 5000, "DEBIT", 1),
    ],
    "mock-acc-icici-001": [
        ("SWIGGY ORDER", "Food", 200, 600, "DEBIT", 2),
        ("ZOMATO ORDER", "Food", 250, 650, "DEBIT", 1),
        ("AMAZON PRIME DAY", "Shopping", 500, 3000, "DEBIT", 2),
        ("FLIPKART BIG BILLION", "Shopping", 600, 4000, "DEBIT", 1),
        ("MYNTRA FASHION", "Shopping", 700, 3000, "DEBIT", 1),
        ("AIR INDIA BOOKING", "Travel", 4000, 18000, "DEBIT", 1),
        ("OYO HOTELS", "Travel", 1500, 5000, "DEBIT", 1),
        ("MAKEMYTRIP", "Travel", 3000, 12000, "DEBIT", 1),
        ("PVR CINEMAS", "Entertainment", 300, 800, "DEBIT", 1),
        ("CULVERTS NIGHTCLUB", "Entertainment", 500, 1500, "DEBIT", 1),
        ("NIIT COURSE FEE", "Education", 2000, 6000, "DEBIT", 1),
    ],
}

_DEFAULT_FIXED = [
    (5, "NETFLIX SUBSCRIPTION", "Entertainment", 649, 0, "DEBIT"),
    (15, "AIRTEL POSTPAID", "Bills", 549, 0, "DEBIT"),
]

_DEFAULT_VARIABLE = [
    ("SWIGGY ORDER", "Food", 150, 450, "DEBIT", 2),
    ("ZOMATO ORDER", "Food", 200, 500, "DEBIT", 1),
    ("UBER INDIA", "Transport", 120, 350, "DEBIT", 1),
    ("AMAZON PAY", "Shopping", 300, 2500, "DEBIT", 1),
    ("APOLLO PHARMACY", "Health", 200, 700, "DEBIT", 1),
]


def _seed_for(account_id: str, from_date: datetime) -> int:
    key = f"{account_id}:{from_date.date().isoformat()}"
    return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16)


def _iter_months(from_date: datetime, to_date: datetime):
    current = datetime(from_date.year, from_date.month, 1, tzinfo=IST)
    end = datetime(to_date.year, to_date.month, 1, tzinfo=IST)
    while current <= end:
        yield current
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1, tzinfo=IST)
        else:
            current = datetime(current.year, current.month + 1, 1, tzinfo=IST)


class MockBankProvider(BankProviderAdapter):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def initiate_consent(self, user_id: str, consent_version: str, redirect_url: str) -> ConsentInitResponse:
        rng = random.Random(_seed_for(f"consent-{user_id}", datetime.now(timezone.utc)))
        if rng.random() < 0.05:
            raise BankConnectionException("Mock provider temporarily unavailable")
        consent_handle = f"mock-consent-{user_id[:8]}-{rng.randint(1000, 9999)}"
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
        if from_date.tzinfo is None:
            from_date = from_date.replace(tzinfo=IST)
        if to_date.tzinfo is None:
            to_date = to_date.replace(tzinfo=IST)

        fixed = FIXED_MONTHLY.get(account_id, _DEFAULT_FIXED)
        variable = VARIABLE_TEMPLATES.get(account_id, _DEFAULT_VARIABLE)
        rng = random.Random(_seed_for(account_id, from_date))

        txs: list[ProviderTransaction] = []
        seq = 0

        for month_start in _iter_months(from_date, to_date):
            month_end = (datetime(month_start.year + 1, 1, 1, tzinfo=IST) if month_start.month == 12
                         else datetime(month_start.year, month_start.month + 1, 1, tzinfo=IST)) - timedelta(seconds=1)

            for (day, description, category, base, variance, direction) in fixed:
                txn_date = month_start.replace(day=min(day, month_end.day))
                if from_date <= txn_date <= to_date:
                    amount = round(base + rng.uniform(0, variance), 2)
                    seq += 1
                    txs.append(ProviderTransaction(
                        transaction_id=f"mock-{account_id}-{txn_date:%Y%m%d}-f{seq}",
                        description=description,
                        amount=amount,
                        transaction_type=direction,
                        transaction_date=txn_date,
                        category=category,
                        reference=f"MOCK/REF/{txn_date:%Y%m%d}/{seq:04d}",
                    ))

            for (description, category, min_amt, max_amt, direction, per_week) in variable:
                occurrences = max(1, round(per_week * (month_end.day / 7)))
                used_days = set()
                for _ in range(occurrences):
                    day = rng.randint(1, month_end.day)
                    if day in used_days:
                        continue
                    used_days.add(day)
                    txn_date = month_start.replace(day=day)
                    if from_date <= txn_date <= to_date:
                        amount = round(rng.uniform(min_amt, max_amt), 2)
                        seq += 1
                        txs.append(ProviderTransaction(
                            transaction_id=f"mock-{account_id}-{txn_date:%Y%m%d}-v{seq}",
                            description=description,
                            amount=amount,
                            transaction_type=direction,
                            transaction_date=txn_date,
                            category=category,
                            reference=f"MOCK/REF/{txn_date:%Y%m%d}/{seq:04d}",
                        ))

        txs.sort(key=lambda t: t.transaction_date)
        return txs

    async def revoke_consent(self, consent_handle: str) -> bool:
        return True
