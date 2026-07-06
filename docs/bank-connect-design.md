# Read-Only Bank Account Connection — Design Document

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ ConnectBank │ │ Consent  │ │ Success  │ │ ManageBank  │ │
│  │   Page      │ │  Page    │ │  Page    │ │   Page      │ │
│  └──────┬──────┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘ │
│         │             │           │               │        │
│  ┌──────┴─────────────┴───────────┴───────────────┴──────┐ │
│  │                bank.js (API module)                    │ │
│  └────────────────────────┬──────────────────────────────┘ │
└───────────────────────────┼────────────────────────────────┘
                            │ HTTP
┌───────────────────────────┼────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌────────────────────────┴──────────────────────────────┐  │
│  │              POST /api/v1/bank/*                       │  │
│  │              GET  /api/v1/bank/*                       │  │
│  │              DELETE /api/v1/bank/*                     │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────┴──────────────────────────────┐  │
│  │                  BankService                           │  │
│  │  ┌──────────────┐ ┌──────────┐ ┌──────────────────┐   │  │
│  │  │ Connect/     │ │ Consent  │ │ Disconnect/      │   │  │
│  │  │ Link Account │ │ Manager  │ │ Revoke Access    │   │  │
│  │  └──────┬───────┘ └────┬─────┘ └───────┬──────────┘   │  │
│  └─────────┼──────────────┼───────────────┼───────────────┘  │
│            │              │               │                  │
│  ┌─────────┴──────────────┴───────────────┴───────────────┐  │
│  │              Provider Adapter Layer                     │  │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐  │  │
│  │  │ MockAA   │ │ Setu   │ │ Finvu  │ │ OneMoney     │  │  │
│  │  │ Provider │ │Adapter │ │Adapter │ │ Adapter      │  │  │
│  │  └──────────┘ └────────┘ └────────┘ └──────────────┘  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴─────────────────────────────────┐  │
│  │              BankRepository                             │  │
│  │              (MongoDB - bank_accounts)                  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴─────────────────────────────────┐  │
│  │                    MongoDB                              │  │
│  │              Collection: bank_accounts                  │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Folder Structure

### Backend — New Files

```
backend/app/
├── api/
│   └── routes/
│       └── bank.py                      # NEW — bank endpoints
├── core/
│   └── config.py                        # EXTEND — AA provider settings
├── db/
│   └── mongodb.py                       # EXTEND — bank_accounts indexes
├── domain/
│   └── bank_accounts/
│       ├── __init__.py
│       ├── models.py                    # NEW — domain model
│       └── repository.py                # NEW — abstract repository
├── infrastructure/
│   ├── bank_integration/
│   │   ├── __init__.py
│   │   ├── base.py                      # NEW — abstract provider adapter
│   │   ├── mock_provider.py             # NEW — mock for dev/testing
│   │   ├── setu_adapter.py             # NEW — Setu AA adapter
│   │   ├── finvu_adapter.py            # NEW — Finvu AA adapter
│   │   ├── onemoney_adapter.py         # NEW — OneMoney AA adapter
│   │   └── consent_manager.py           # NEW — consent lifecycle
│   └── database/
│       └── repositories/
│           └── bank_repository.py       # NEW — Mongo implementation
├── schemas/
│   └── bank.py                          # NEW — request/response schemas
└── services/
    └── bank_service.py                  # NEW — business logic
```

### Frontend — New Files

```
frontend/src/
├── App.jsx                              # EXTEND — add /connect-bank routes
├── api/
│   └── bank.js                          # NEW — API client for bank endpoints
├── pages/
│   ├── ConnectBank.jsx                  # NEW — bank selection + initiate
│   ├── ConsentPage.jsx                  # NEW — consent confirmation
│   ├── ConnectSuccess.jsx               # NEW — success confirmation
│   └── ManageAccounts.jsx               # NEW — connected accounts list
├── components/
│   └── bank/
│       ├── BankCard.jsx                 # NEW — individual bank display
│       ├── ConsentForm.jsx              # NEW — consent details + confirm
│       ├── AccountList.jsx              # NEW — list of connected accounts
│       └── DisconnectDialog.jsx         # NEW — confirm disconnect modal
├── landing/
│   ├── features.js                      # EXTEND — add "Bank Connect" feature
│   └── navigation.js                    # EXTEND — add /connect-bank link
```

---

## 3. API Design

### 3.1 Route Module

File: `backend/app/api/routes/bank.py`

```python
router = APIRouter(prefix="/bank", tags=["bank"])
```

### 3.2 Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/bank/connect` | JWT | Initiate bank connection — returns consent URL |
| `POST` | `/api/v1/bank/consent` | JWT | Submit user consent for a provider |
| `GET` | `/api/v1/bank/accounts` | JWT | List all connected bank accounts |
| `GET` | `/api/v1/bank/status` | JWT | Get overall connection status |
| `DELETE` | `/api/v1/bank/disconnect/{account_id}` | JWT | Disconnect a specific account |

### 3.3 Request/Response Schemas

File: `backend/app/schemas/bank.py`

```python
# --- Request Schemas ---

class BankConnectRequest(BaseModel):
    provider: str                    # "mock", "setu", "finvu", "onemoney"
    consent_version: str = "1.0"

class ConsentSubmitRequest(BaseModel):
    provider: str
    consent_handle: str              # From AA provider
    consent_token: str               # Signed consent artefact
    account_ids: list[str]           # Encrypted account identifiers

# --- Response Schemas ---

class BankAccountPublic(BaseModel):
    id: str
    provider: str
    bank_name: str
    masked_account_number: str       # e.g. "XXXXXX1234"
    account_type: str                # "savings", "current", "credit_card"
    connection_status: str           # "active", "expired", "revoked"
    consent_status: str              # "pending", "active", "expired", "revoked"
    consent_expiry: datetime | None
    created_at: datetime
    updated_at: datetime

class ConnectInitResponse(BaseModel):
    consent_url: str                 # URL to redirect user for AA consent
    consent_handle: str
    expires_at: datetime

class BankStatusResponse(BaseModel):
    total_accounts: int
    active_accounts: int
    providers_connected: list[str]
    last_sync: datetime | None
```

### 3.4 Exception Handling

New exceptions in `app/core/exceptions.py`:

```python
class BankConnectionException(AppException):
    """Raised when bank connection fails at provider level"""
    def __init__(self, detail: str = "Bank connection failed"):
        super().__init__(status_code=502, detail=detail, code="BANK_CONNECTION_ERROR")

class ConsentExpiredException(AppException):
    def __init__(self):
        super().__init__(status_code=400, detail="Consent has expired", code="CONSENT_EXPIRED")

class ConsentDeniedException(AppException):
    def __init__(self):
        super().__init__(status_code=403, detail="User denied consent", code="CONSENT_DENIED")

class ProviderNotFoundException(AppException):
    def __init__(self, provider: str):
        super().__init__(status_code=404, detail=f"Unknown provider: {provider}", code="PROVIDER_NOT_FOUND")

class NoActiveConnectionsException(AppException):
    def __init__(self):
        super().__init__(status_code=400, detail="No active bank connections found", code="NO_ACTIVE_CONNECTIONS")
```

---

## 4. Database Schema

### 4.1 New Collection: `bank_accounts`

File: `backend/app/models/documents.py`

```python
class BankAccountDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    provider: str                                    # "mock", "setu", "finvu", "onemoney"
    consent_handle: str                              # AA consent reference
    provider_account_id: str                         # Encrypted account ID from provider
    bank_name: str                                   # e.g. "State Bank of India"
    masked_account_number: str                       # e.g. "XXXXXX1234"
    account_type: str                                # "savings", "current", "credit_card"
    account_holder_name: str                         # Name on account
    ifsc_code: str                                   # Bank branch identifier
    connection_status: Literal["active", "expired", "revoked", "error"]
    consent_status: Literal["pending", "active", "expired", "revoked", "denied"]
    consent_token: str                               # Encrypted consent artefact
    consent_version: str
    consent_expiry: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### 4.2 Indexes

File: `backend/app/db/mongodb.py`

```python
await database.bank_accounts.create_index([("user_id", 1), ("connection_status", 1)])
await database.bank_accounts.create_index([("user_id", 1), ("provider", 1)])
await database.bank_accounts.create_index([("consent_handle", 1)], unique=True, sparse=True)
await database.bank_accounts.create_index([("consent_expiry", 1)], expireAfterSeconds=0)
```

### 4.3 Domain Model

File: `backend/app/domain/bank_accounts/models.py`

```python
class BankAccount(BaseModel):
    id: PyObjectId
    user_id: PyObjectId
    provider: str
    consent_handle: str
    provider_account_id: str
    bank_name: str
    masked_account_number: str
    account_type: str
    account_holder_name: str
    ifsc_code: str
    connection_status: str
    consent_status: str
    consent_token: str
    consent_version: str
    consent_expiry: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### 4.4 Repository Interface

File: `backend/app/domain/bank_accounts/repository.py`

```python
class BankAccountRepository(ABC):
    @abstractmethod
    async def create(self, account: BankAccount) -> BankAccount: ...
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[BankAccount]: ...
    
    @abstractmethod
    async def get_active_by_user_id(self, user_id: str) -> list[BankAccount]: ...
    
    @abstractmethod
    async def get_by_id(self, account_id: str) -> BankAccount | None: ...
    
    @abstractmethod
    async def get_by_consent_handle(self, consent_handle: str) -> BankAccount | None: ...
    
    @abstractmethod
    async def update_connection_status(self, account_id: str, status: str) -> BankAccount: ...
    
    @abstractmethod
    async def update_consent_status(self, account_id: str, status: str, expiry: datetime | None = None) -> BankAccount: ...
    
    @abstractmethod
    async def delete(self, account_id: str) -> None: ...
    
    @abstractmethod
    async def count_active_by_user_id(self, user_id: str) -> int: ...
```

---

## 5. Provider Adapter Pattern

### 5.1 Abstract Base

File: `backend/app/infrastructure/bank_integration/base.py`

```python
class BankProviderAdapter(ABC):
    """Abstract adapter for AA provider integrations."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def initiate_consent(
        self,
        user_id: str,
        consent_version: str,
        redirect_url: str,
    ) -> ConsentInitResponse:
        """
        Step 1: Create a consent request with the AA.
        Returns a URL to redirect the user for authentication + approval.
        """
        ...

    @abstractmethod
    async def check_consent_status(
        self,
        consent_handle: str,
    ) -> ConsentStatusResponse:
        """
        Step 2: Poll consent status after user returns from AA.
        Returns whether consent was granted, denied, or still pending.
        """
        ...

    @abstractmethod
    async def fetch_accounts(
        self,
        consent_handle: str,
        consent_token: str,
    ) -> list[ProviderAccount]:
        """
        Step 3: After consent granted, fetch linked accounts from AA.
        Returns decrypted account metadata (never raw credentials).
        """
        ...

    @abstractmethod
    async def fetch_transactions(
        self,
        consent_handle: str,
        consent_token: str,
        account_id: str,
        from_date: datetime,
        to_date: datetime,
    ) -> list[ProviderTransaction]:
        """
        Step 4: Fetch transaction data for a given account within consent scope.
        Used by the sync engine (future phase).
        """
        ...

    @abstractmethod
    async def revoke_consent(
        self,
        consent_handle: str,
    ) -> bool:
        """Step 5: Revoke previously granted consent."""
        ...
```

### 5.2 Data Transfer Objects

```python
class ConsentInitResponse(BaseModel):
    consent_handle: str
    consent_url: str
    expires_at: datetime

class ConsentStatusResponse(BaseModel):
    status: Literal["ACTIVE", "EXPIRED", "REVOKED", "DENIED", "PENDING"]
    consent_token: str | None        # Only populated when ACTIVE

class ProviderAccount(BaseModel):
    provider_account_id: str         # Encrypted AA reference
    bank_name: str
    masked_account_number: str
    account_type: str
    account_holder_name: str
    ifsc_code: str

class ProviderTransaction(BaseModel):
    transaction_id: str
    description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    category: str | None
    reference: str | None
```

### 5.3 Provider Registry

```python
class BankProviderRegistry:
    """Maps provider names to adapter instances. Configured at startup."""

    def __init__(self):
        self._adapters: dict[str, BankProviderAdapter] = {}

    def register(self, name: str, adapter: BankProviderAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> BankProviderAdapter:
        adapter = self._adapters.get(name)
        if not adapter:
            raise ProviderNotFoundException(name)
        return adapter

    def list_providers(self) -> list[str]:
        return list(self._adapters.keys())
```

### 5.4 Mock Provider

File: `backend/app/infrastructure/bank_integration/mock_provider.py`

```python
class MockAAProvider(BankProviderAdapter):
    """
    Development-only mock that simulates Account Aggregator responses.
    Returns synthetic bank accounts and transactions without real API calls.
    Register with provider_name="mock".
    """

    @property
    def provider_name(self) -> str: return "mock"

    async def initiate_consent(self, user_id, consent_version, redirect_url) -> ConsentInitResponse:
        # Returns a fake consent URL (simulating AA redirect)
        ...

    async def check_consent_status(self, consent_handle) -> ConsentStatusResponse:
        # Automatically returns ACTIVE with a fake token after 2s delay
        ...

    async def fetch_accounts(self, consent_handle, consent_token) -> list[ProviderAccount]:
        # Returns 2–3 synthetic Indian bank accounts
        # e.g. SBI Savings, HDFC Current, ICICI Credit Card
        ...

    async def fetch_transactions(self, consent_handle, consent_token, account_id, from_date, to_date) -> list[ProviderTransaction]:
        # Returns 20–50 synthetic transactions across categories
        ...

    async def revoke_consent(self, consent_handle) -> bool:
        return True
```

---

## 6. Consent Architecture

### 6.1 Consent Lifecycle

```
USER                    FRONTEND              BACKEND               AA PROVIDER
 │                        │                      │                      │
 │  1. Choose Bank        │                      │                      │
 ├───────────────────────►│                      │                      │
 │                        │  2. POST /connect    │                      │
 │                        ├─────────────────────►│                      │
 │                        │                      │  3. Initiate Consent │
 │                        │                      ├─────────────────────►│
 │                        │                      │  4. Consent URL      │
 │                        │                      │◄─────────────────────┤
 │                        │  5. Consent URL      │                      │
 │                        │◄─────────────────────┤                      │
 │  6. Redirect to AA     │                      │                      │
 │◄───────────────────────┤                      │                      │
 │                        │                      │                      │
 │═══ User authenticates at AA, reviews consent ═══════════════════════►│
 │═══ User approves/denies data sharing        ═══════════════════════►│
 │                        │                      │                      │
 │  7. AA redirects back  │                      │                      │
 ├───────────────────────►│                      │                      │
 │                        │  8. POST /consent    │                      │
 │                        │  (consent_handle     │                      │
 │                        │   + consent_token)   │                      │
 │                        ├─────────────────────►│                      │
 │                        │                      │  9. Verify Consent   │
 │                        │                      ├─────────────────────►│
 │                        │                      │ 10. Fetch Accounts   │
 │                        │                      ├─────────────────────►│
 │                        │                      │ 11. Account List     │
 │                        │                      │◄─────────────────────┤
 │                        │ 12. Save to DB       │                      │
 │                        │◄─────────────────────┤                      │
 │ 13. Success Page       │                      │                      │
 │◄───────────────────────┤                      │                      │

Status transitions per account:
   PENDING  ──(user approves)──►  ACTIVE
   PENDING  ──(user denies)───►  DENIED
   ACTIVE   ──(expiry)────────►  EXPIRED
   ACTIVE   ──(user revokes)──►  REVOKED
   ACTIVE   ──(AA revokes)────►  REVOKED
```

### 6.2 Consent Manager

File: `backend/app/infrastructure/bank_integration/consent_manager.py`

```python
class ConsentManager:
    """
    Orchestrates the consent lifecycle across all providers.
    Handles creation, verification, polling, expiry detection, and revocation.
    """

    def __init__(self, registry: BankProviderRegistry, repo: BankAccountRepository):
        self.registry = registry
        self.repo = repo

    async def create_consent(self, user_id: str, provider: str, redirect_url: str) -> ConnectInitResponse:
        """Initiate consent via the provider adapter. Returns AA redirect URL."""
        adapter = self.registry.get(provider)
        return await adapter.initiate_consent(user_id, "1.0", redirect_url)

    async def finalize_consent(self, user_id: str, provider: str, consent_handle: str, consent_token: str, account_ids: list[str]) -> list[BankAccount]:
        """After user returns from AA, verify consent and persist accounts."""
        adapter = self.registry.get(provider)
        status = await adapter.check_consent_status(consent_handle)
        if status.status != "ACTIVE":
            raise ConsentDeniedException()
        accounts = await adapter.fetch_accounts(consent_handle, consent_token)
        persisted = []
        for acc in accounts:
            if account_ids and acc.provider_account_id not in account_ids:
                continue
            bank_account = BankAccount(
                user_id=user_id, provider=provider, ...
            )
            persisted.append(await self.repo.create(bank_account))
        return persisted

    async def revoke_consent(self, account_id: str) -> None:
        """Revoke a specific account's consent at the provider + DB level."""
        account = await self.repo.get_by_id(account_id)
        adapter = self.registry.get(account.provider)
        await adapter.revoke_consent(account.consent_handle)
        await self.repo.update_consent_status(account_id, "revoked")

    async def check_expired_consents(self) -> int:
        """Background job: find and mark expired consents."""
        # Queries bank_accounts where consent_expiry < now
        # Marks as EXPIRED
        ...

    async def get_active_accounts(self, user_id: str) -> list[BankAccount]:
        return await self.repo.get_active_by_user_id(user_id)
```

---

## 7. Service Layer

File: `backend/app/services/bank_service.py`

```python
class BankService:
    """
    Business logic for bank account connection.
    Orchestrates ConsentManager, BankRepository, and ProviderAdapter.
    """

    def __init__(self, consent_manager: ConsentManager, repo: BankAccountRepository):
        self.consent_manager = consent_manager
        self.repo = repo

    async def initiate_connection(self, user_id: str, provider: str) -> ConnectInitResponse:
        """Step 1: Validate provider, create consent, return AA redirect URL."""
        return await self.consent_manager.create_consent(
            user_id=user_id,
            provider=provider,
            redirect_url=f"/connect-bank/consent?provider={provider}",
        )

    async def complete_consent(self, user_id: str, req: ConsentSubmitRequest) -> list[BankAccountPublic]:
        """Step 2: Finalize consent, persist accounts."""
        accounts = await self.consent_manager.finalize_consent(
            user_id=user_id,
            provider=req.provider,
            consent_handle=req.consent_handle,
            consent_token=req.consent_token,
            account_ids=req.account_ids,
        )
        return [serialize_bank_account(a) for a in accounts]

    async def list_accounts(self, user_id: str) -> list[BankAccountPublic]:
        accounts = await self.repo.get_by_user_id(user_id)
        return [serialize_bank_account(a) for a in accounts]

    async def get_status(self, user_id: str) -> BankStatusResponse:
        active = await self.repo.get_active_by_user_id(user_id)
        providers = list({a.provider for a in active})
        return BankStatusResponse(
            total_accounts=len(active),
            active_accounts=len(active),
            providers_connected=providers,
            last_sync=max((a.last_synced_at for a in active if a.last_synced_at), default=None),
        )

    async def disconnect(self, user_id: str, account_id: str) -> None:
        account = await self.repo.get_by_id(account_id)
        if not account or str(account.user_id) != user_id:
            raise NotFoundException("Bank account not found")
        await self.consent_manager.revoke_consent(account_id)
```

---

## 8. Security Architecture

### 8.1 Data Protection

| Data | Protection Method |
|------|------------------|
| `provider_account_id` | AES-256-GCM encryption at rest in MongoDB |
| `consent_token` | AES-256-GCM encryption at rest in MongoDB |
| `masked_account_number` | Stored as-is (masked, not raw) |
| Bank credentials | **Never stored** — user authenticates directly at AA |
| Consent artefacts | Signed JWT from AA, verified on each fetch |

### 8.2 Encryption Utility

```python
# backend/app/core/encryption.py (NEW)

from cryptography.fernet import Fernet
from app.core.config import get_settings

class FieldEncryptor:
    """Field-level encryption for sensitive bank data."""

    def __init__(self):
        key = get_settings().bank_encryption_key.encode()
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

### 8.3 Config Extension

```python
# backend/app/core/config.py — new fields

class Settings(BaseSettings):
    # ... existing fields ...

    # Bank Connection
    bank_encryption_key: str = Field(default="change-this-bank-encryption-key-32bytes!")
    bank_consent_redirect_base: str = "http://localhost:5173/connect-bank/consent"
    aa_setu_base_url: str = ""
    aa_finvu_base_url: str = ""
    aa_onemoney_base_url: str = ""
    aa_client_id: str = ""
    aa_client_secret: str = ""
```

### 8.4 Security Flow

```
1. User selects provider on /connect-bank
2. Backend calls AA provider to create consent request
3. User is redirected to AA portal (NOT our server)
4. User authenticates at AA (2FA/bank login) — NOT our server
5. User reviews/approves data consent scope
6. AA redirects user back to our /connect-bank/consent with consent_handle
7. Backend calls AA to verify consent status + fetch decrypted account references
8. Only masked + encrypted data is stored in our MongoDB
9. Actual transaction data fetched on-demand via AA using valid consent token
10. Consent expiry is enforced both at AA level and our DB level
```

### 8.5 Compliance Notes

- **RBI AA compliance**: Data stored only with explicit user consent. Consent has finite expiry. User can revoke anytime.
- **No screen-scraping**: All data access via AA's encrypted API — never via user credentials.
- **Data minimization**: Only request and store the minimum required data (account metadata + transactions).
- **Audit trail**: Every consent creation, approval, data fetch, and revocation is logged with timestamps.
- **User control**: Users can see all connected accounts and revoke any connection from `/connect-bank/manage`.

---

## 9. Frontend Routes

### 9.1 Route Configuration

```jsx
// App.jsx — new routes under LandingLayout for public, protected for management

<Route element={<LandingLayout />}>
  <Route index element={<HomePage />} />
  <Route path="features" element={<FeaturesPage />} />
  <Route path="about" element={<AboutPage />} />
  <Route path="contact" element={<ContactPage />} />
  <Route path="privacy" element={<PrivacyPage />} />
  <Route path="terms" element={<TermsPage />} />
  <Route path="connect-bank" element={<ConnectBank />} />
  <Route path="connect-bank/consent" element={<ConsentPage />} />
  <Route path="connect-bank/success" element={<ConnectSuccess />} />
</Route>

<Route path="/app" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
  <Route index element={<Dashboard />} />
  {/* ... existing routes ... */}
  <Route path="bank-accounts" element={<ManageAccounts />} />
</Route>
```

### 9.2 Page Responsibilities

```
/connect-bank           → Provider selection + "Connect Account" CTA
/connect-bank/consent   → Consent detail page, shows scope, confirm button
                           (after AA redirect, shows processing state)
/connect-bank/success   → Confirmation with connected account cards + next steps
/connect-bank/manage    → List all connected accounts + revoke option
                           (also accessible at /app/bank-accounts)
```

### 9.3 API Module

File: `frontend/src/api/bank.js`

```javascript
import { api } from "./client";

export const bankApi = {
  connect: (provider) => api.post("/api/v1/bank/connect", { provider }),
  submitConsent: (payload) => api.post("/api/v1/bank/consent", payload),
  getAccounts: () => api.get("/api/v1/bank/accounts"),
  getStatus: () => api.get("/api/v1/bank/status"),
  disconnect: (accountId) => api.delete(`/api/v1/bank/disconnect/${accountId}`),
};
```

---

## 10. Startup Wiring

File: `backend/app/main.py` — extension

```python
from app.infrastructure.bank_integration.mock_provider import MockAAProvider
from app.infrastructure.bank_integration.consent_manager import ConsentManager
from app.infrastructure.bank_integration.base import BankProviderRegistry
from app.services.bank_service import BankService

# At app startup or in a dependency provider:
registry = BankProviderRegistry()
registry.register("mock", MockAAProvider())
# registry.register("setu", SetuAAProvider(...))
# registry.register("finvu", FinvuAAProvider(...))
# registry.register("onemoney", OneMoneyAAProvider(...))

consent_manager = ConsentManager(registry, BankAccountRepository())
bank_service = BankService(consent_manager, BankAccountRepository())
```

Dependency injection in route:

```python
@router.post("/connect")
async def connect_bank(
    req: BankConnectRequest,
    user: dict = Depends(get_current_user),
    service: BankService = Depends(get_bank_service),
):
    return await service.initiate_connection(str(user["_id"]), req.provider)
```

---

## 11. Wiring Guide — All Files to Modify

### Backend — Modified Files

| File | Change |
|------|--------|
| `app/core/config.py` | Add `bank_encryption_key`, AA URL configs, `consent_redirect_base` |
| `app/core/exceptions.py` | Add `BankConnectionException`, `ConsentExpiredException`, `ConsentDeniedException`, `ProviderNotFoundException`, `NoActiveConnectionsException` |
| `app/core/encryption.py` | **NEW** — Fernet field-level encryption utility |
| `app/db/mongodb.py` | Add `bank_accounts` indexes |
| `app/main.py` | Wire `BankProviderRegistry`, register mock provider |
| `app/api/v1/router.py` | Add `router.include_router(bank.router, tags=["bank"])` |
| `app/schemas/common.py` | Optionally add consent-related mixins |

### Backend — New Files

| File | Purpose |
|------|---------|
| `app/api/routes/bank.py` | 5 bank endpoints |
| `app/schemas/bank.py` | Request/response Pydantic schemas |
| `app/models/documents.py` | Add `BankAccountDocument` TypedDict |
| `app/domain/bank_accounts/__init__.py` | Package init |
| `app/domain/bank_accounts/models.py` | `BankAccount` domain model |
| `app/domain/bank_accounts/repository.py` | Abstract repository interface |
| `app/infrastructure/database/repositories/bank_repository.py` | Mongo repository implementation |
| `app/infrastructure/bank_integration/__init__.py` | Package init |
| `app/infrastructure/bank_integration/base.py` | Abstract `BankProviderAdapter` |
| `app/infrastructure/bank_integration/mock_provider.py` | Mock AA provider for dev |
| `app/infrastructure/bank_integration/consent_manager.py` | Consent lifecycle orchestrator |
| `app/services/bank_service.py` | Business logic service |

### Frontend — Modified Files

| File | Change |
|------|--------|
| `App.jsx` | Add `/connect-bank` routes (public) and `/app/bank-accounts` (protected) |
| `src/api/client.js` | Optionally add bank-specific interceptors |
| `src/landing/data/navigation.js` | Add "Connect Bank" link |
| `src/landing/data/features.js` | Add bank connect feature card |

### Frontend — New Files

| File | Purpose |
|------|---------|
| `src/api/bank.js` | API client module |
| `src/pages/ConnectBank.jsx` | Provider selection page |
| `src/pages/ConsentPage.jsx` | Consent confirmation + processing |
| `src/pages/ConnectSuccess.jsx` | Success confirmation |
| `src/pages/ManageAccounts.jsx` | Connected accounts management |
| `src/components/bank/BankCard.jsx` | Bank display card |
| `src/components/bank/ConsentForm.jsx` | Consent detail + confirm |
| `src/components/bank/AccountList.jsx` | Connected accounts list |
| `src/components/bank/DisconnectDialog.jsx` | Revoke confirmation modal |

---

## 12. Future Sync Engine Integration

The sync engine (Phase 4 — Transaction Management) will integrate via:

```python
# Future: backend/app/services/sync_service.py

class SyncService:
    def __init__(self, bank_service: BankService, consent_manager: ConsentManager):
        ...

    async def sync_all_accounts(self, user_id: str) -> SyncResult:
        """Fetch all transactions from all connected accounts since last sync."""
        accounts = await self.bank_service.list_accounts(user_id)
        for account in accounts:
            transactions = await consent_manager.fetch_transactions(
                account.consent_handle,
                account.consent_token,
                account.provider_account_id,
                from_date=account.last_synced_at or (utc_now() - timedelta(days=90)),
                to_date=utc_now(),
            )
            # Deduplicate, categorize, persist
            ...

    async def schedule_sync(self, user_id: str, interval: int = 3600):
        """Add to Celery/ARQ periodic sync queue."""
        ...
```
