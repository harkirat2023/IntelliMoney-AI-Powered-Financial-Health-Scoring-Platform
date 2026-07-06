# Consent Grant & Transaction Import Preference — Design Document

## 1. Overview

This phase begins **after** a user has successfully connected a bank account via the existing bank connection flow (`POST /bank/consent` → accounts persisted in `bank_accounts`).

The user now needs to:
1. Grant explicit consent for IntelliMoney to import their transaction data.
2. Choose how much historical data to import.
3. Review and confirm their choices before any sync begins.

No transaction fetching, sync, or background jobs are implemented here. This phase only handles consent recording and import preference storage — the **configuration** that the future sync engine will read.

---

## 2. Architecture Position

```
Bank Account Connected (existing)
         │
         ▼
  ┌──────────────────┐
  │  Import Preference │  ← NEW: /connect-bank/import-preference
  │  (Option selection)│
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │   Review Screen   │  ← NEW: /connect-bank/review
  │  (estimated sync) │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Consent Grant +   │  ← NEW: POST /consent/grant + POST /import-preference
  │  Save Preference  │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │    Complete       │  ← NEW: /connect-bank/complete
  │  (done + next)    │
  └──────────────────┘
```

The existing bank flow now inserts at the `Success` page:
- Old: `ConnectBank → Consent → Success` (end)
- New: `ConnectBank → Consent → Success → ImportPreference → Review → Complete`

---

## 3. Folder Structure

### Backend — New Files

```
backend/app/
├── api/
│   ├── routes/
│   │   ├── consent.py                  # NEW — grant, revoke, status
│   │   └── import_preference.py        # NEW — save, get
│   └── v1/
│       └── router.py                   # EXTEND — include consent + import_preference routers
├── domain/
│   ├── consents/                       # NEW domain
│   │   ├── __init__.py
│   │   ├── models.py                   # ConsentGrant domain model
│   │   └── repository.py              # Abstract consent repository
│   └── import_preferences/             # NEW domain
│       ├── __init__.py
│       ├── models.py                   # ImportPreference domain model
│       └── repository.py              # Abstract import preference repository
├── infrastructure/
│   └── database/
│       └── repositories/
│           ├── consent_repository.py   # NEW — Mongo implementation
│           └── import_preference_repository.py  # NEW — Mongo implementation
├── schemas/
│   ├── consent.py                      # NEW — request/response schemas
│   └── import_preference.py            # NEW — request/response schemas
├── services/
│   ├── consent_grant_service.py        # NEW — grant/revoke business logic
│   └── import_preference_service.py    # NEW — save/get business logic
├── core/
│   └── exceptions.py                   # EXTEND — new exceptions
├── db/
│   └── mongodb.py                      # EXTEND — consents + import_preferences indexes
└── models/
    └── documents.py                    # EXTEND — ConsentDocument + ImportPreferenceDocument TypedDicts
```

### Frontend — New Files

```
frontend/src/
├── pages/
│   ├── ImportPreference.jsx            # NEW — import option selection + estimated summary
│   ├── ReviewPage.jsx                  # NEW — review + confirm
│   └── CompletePage.jsx                # NEW — final confirmation + next steps
├── api/
│   ├── consent.js                      # NEW — consent API client
│   └── importPreference.js             # NEW — import preference API client
├── components/
│   └── import/
│       ├── ImportOptionCard.jsx        # NEW — option selection card
│       ├── EstimatedSummary.jsx        # NEW — estimated sync summary banner
│       ├── DateRangePicker.jsx         # NEW — date selection for Option 3
│       └── ReviewSummary.jsx           # NEW — review confirmation card
├── App.jsx                             # EXTEND — add /connect-bank/import-preference, /review, /complete
└── landing/
    └── data/
        └── navigation.js              # EXTEND — no changes needed (uses existing bank link)
```

---

## 4. New Collections

### 4.1 `consents`

Tracks the explicit user-facing consent grants for transaction import. Separate from the AA-level consent stored in `bank_accounts.consent_status`.

```python
class ConsentDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId           # FK to bank_accounts._id
    consent_status: Literal[            # Status of user-facing consent
        "granted",                       # User approved transaction import
        "revoked",                       # User revoked import permission
        "expired",                       # Consent duration passed
    ]
    consent_version: str                 # "1.0"
    granted_at: datetime                 # When consent was granted
    expires_at: datetime | None          # Optional expiry
    revoked_at: datetime | None          # When revoked (if applicable)
    created_at: datetime
    updated_at: datetime
```

**Indexes:**

```python
await database.consents.create_index([("user_id", 1), ("bank_account_id", 1)])
await database.consents.create_index([("bank_account_id", 1)])
await database.consents.create_index([("consent_status", 1), ("expires_at", 1)])
```

### 4.2 `import_preferences`

Stores the user's choice for how much transaction history to import.

```python
class ImportPreferenceDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId           # FK to bank_accounts._id
    import_type: Literal[               # User's import choice
        "import_all",                    # All available history
        "start_fresh",                   # No history, only new transactions
        "from_date",                     # From a specific date forward
    ]
    import_start_date: datetime | None  # Populated when import_type == "from_date"
    created_at: datetime
    updated_at: datetime
```

**Unique constraint:** One `import_preference` per `(user_id, bank_account_id)` — enforced via unique compound index + upsert.

**Indexes:**

```python
await database.import_preferences.create_index(
    [("user_id", 1), ("bank_account_id", 1)], unique=True
)
await database.import_preferences.create_index([("bank_account_id", 1)])
```

---

## 5. API Design

### 5.1 Consent Endpoints

Prefix: `/api/v1/consent` (all JWT-protected)

| Method | Path | Request Body | Response | Description |
|--------|------|-------------|----------|-------------|
| `POST` | `/grant` | `ConsentGrantRequest` | `ConsentGrantResponse` | Record user consent to import transactions for a bank account |
| `POST` | `/revoke` | `ConsentRevokeRequest` | `ConsentRevokeResponse` | Revoke previously granted import consent |
| `GET` | `/status` | Query: `bank_account_id` | `ConsentStatusResponse` | Get current consent status for an account |

### 5.2 Import Preference Endpoints

Prefix: `/api/v1/import-preference` (all JWT-protected)

| Method | Path | Request Body | Response | Description |
|--------|------|-------------|----------|-------------|
| `POST` | `/` | `ImportPreferenceRequest` | `ImportPreferenceResponse` | Save import type preference for a bank account |
| `GET` | `/` | Query: `bank_account_id` | `ImportPreferenceResponse` | Get saved import preference for an account |

### 5.3 Schemas

```python
# ── schemas/consent.py ──

class ConsentGrantRequest(BaseModel):
    bank_account_id: str                 # Which account the user is consenting for
    consent_version: str = "1.0"
    consent_duration_days: int = 365     # Optional expiry (default 1 year)

class ConsentGrantResponse(BaseModel):
    id: str
    bank_account_id: str
    consent_status: Literal["granted"]
    granted_at: datetime
    expires_at: datetime | None

class ConsentRevokeRequest(BaseModel):
    bank_account_id: str

class ConsentRevokeResponse(BaseModel):
    id: str
    consent_status: Literal["revoked"]
    revoked_at: datetime

class ConsentStatusResponse(BaseModel):
    id: str
    bank_account_id: str
    consent_status: Literal["granted", "revoked", "expired", "not_found"]
    granted_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None


# ── schemas/import_preference.py ──

class ImportPreferenceRequest(BaseModel):
    bank_account_id: str
    import_type: Literal["import_all", "start_fresh", "from_date"]
    import_start_date: datetime | None = None   # Required if import_type == "from_date"

    @field_validator("import_start_date")
    @classmethod
    def validate_start_date(cls, v, info):
        if info.data.get("import_type") == "from_date" and v is None:
            raise ValueError("import_start_date is required when import_type is 'from_date'")
        return v

class ImportPreferenceResponse(BaseModel):
    id: str
    bank_account_id: str
    import_type: str
    import_start_date: datetime | None
    created_at: datetime
    updated_at: datetime
```

### 5.4 Exception Extensions

```python
class ConsentNotFoundException(AppException):
    """No consent record found for this account"""
    def __init__(self):
        super().__init__(status_code=404, detail="Consent not found", code="CONSENT_NOT_FOUND")

class ConsentAlreadyRevokedException(AppException):
    """Attempted to revoke already revoked consent"""
    def __init__(self):
        super().__init__(status_code=400, detail="Consent already revoked", code="CONSENT_ALREADY_REVOKED")

class ImportPreferenceNotFoundException(AppException):
    """No import preference found for this account"""
    def __init__(self):
        super().__init__(status_code=404, detail="Import preference not found", code="IMPORT_PREFERENCE_NOT_FOUND")

class BankAccountNotActiveException(AppException):
    """Operation requires an active bank account"""
    def __init__(self):
        super().__init__(status_code=400, detail="Bank account is not active", code="BANK_ACCOUNT_NOT_ACTIVE")
```

---

## 6. Service Layer Design

### 6.1 ConsentGrantService

```python
class ConsentGrantService:
    """
    Manages user-facing consent grants for transaction import.
    This is SEPARATE from AA-level consent (ConsentManager).
    AA consent = permission to fetch data from bank via AA.
    User consent = permission for IntelliMoney to import and store that data.
    """

    def __init__(self, consent_repo: ConsentRepository, bank_repo: BankAccountRepository):
        ...

    async def grant(self, user_id: str, req: ConsentGrantRequest) -> ConsentGrantResponse:
        """Record user consent to import transactions for a bank account.
        Validates:
        - Bank account exists and belongs to user
        - Bank account connection_status is active
        - No existing active consent (idempotent: returns existing if same)
        """
        ...

    async def revoke(self, user_id: str, req: ConsentRevokeRequest) -> ConsentRevokeResponse:
        """Revoke import consent. Validates:
        - Bank account belongs to user
        - Consent exists and is currently granted (not already revoked/expired)
        - Sets revoked_at and updates consent_status
        """
        ...

    async def get_status(self, user_id: str, bank_account_id: str) -> ConsentStatusResponse:
        """Return current consent status. Returns not_found if no record exists."""
        ...
```

### 6.2 ImportPreferenceService

```python
class ImportPreferenceService:
    """
    Manages user's import type preference for each bank account.
    The future sync engine will read this to determine how far back to fetch.
    """

    def __init__(self, pref_repo: ImportPreferenceRepository):
        ...

    async def save(self, user_id: str, req: ImportPreferenceRequest) -> ImportPreferenceResponse:
        """Save or update import preference. Uses upsert on (user_id, bank_account_id).
        Validates:
        - import_start_date is present when import_type == "from_date"
        - import_start_date is not in the future (optional validation)
        """
        ...

    async def get(self, user_id: str, bank_account_id: str) -> ImportPreferenceResponse:
        """Return saved import preference for an account."""
        ...
```

---

## 7. Domain Models

### 7.1 `domain/consents/models.py`

```python
class ConsentGrant(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    bank_account_id: PyObjectId
    consent_status: str = "granted"       # granted, revoked, expired
    consent_version: str = "1.0"
    granted_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    def is_active(self) -> bool:
        return (
            self.consent_status == "granted"
            and (self.expires_at is None or self.expires_at > utc_now())
        )

    def revoke(self) -> None:
        self.consent_status = "revoked"
        self.revoked_at = utc_now()
        self.updated_at = utc_now()

    def to_mongo(self) -> dict: ...
    @classmethod
    def from_mongo(cls, doc: dict) -> "ConsentGrant": ...
```

### 7.2 `domain/import_preferences/models.py`

```python
class ImportPreference(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    bank_account_id: PyObjectId
    import_type: str                     # import_all, start_fresh, from_date
    import_start_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    def get_sync_range(self) -> tuple[datetime | None, datetime]:
        """Returns (from_date, to_date) for the sync engine.
        - import_all → (None, now) — earliest available
        - start_fresh → (now, now) — no history
        - from_date   → (import_start_date, now)
        """
        now = utc_now()
        if self.import_type == "import_all":
            return (None, now)
        elif self.import_type == "start_fresh":
            return (now, now)
        else:
            return (self.import_start_date, now)

    def to_mongo(self) -> dict: ...
    @classmethod
    def from_mongo(cls, doc: dict) -> "ImportPreference": ...
```

### 7.3 Abstract Repositories

```python
class ConsentRepository(ABC):
    @abstractmethod
    async def create(self, consent: ConsentGrant) -> ConsentGrant: ...

    @abstractmethod
    async def get_by_id(self, consent_id: str) -> ConsentGrant | None: ...

    @abstractmethod
    async def get_active_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None:
        """Get the currently active (granted, not expired) consent for an account."""
        ...

    @abstractmethod
    async def get_by_account(self, user_id: str, bank_account_id: str) -> ConsentGrant | None:
        """Get the latest consent record (any status) for an account."""
        ...

    @abstractmethod
    async def update_status(self, consent_id: str, status: str, revoked_at: datetime | None = None) -> ConsentGrant | None: ...

    @abstractmethod
    async def get_all_expired(self) -> list[ConsentGrant]:
        """Get all consents where expires_at < now and status is still 'granted'.
        Used by background expiry checker (future)."""
        ...


class ImportPreferenceRepository(ABC):
    @abstractmethod
    async def upsert(self, pref: ImportPreference) -> ImportPreference:
        """Insert or update on (user_id, bank_account_id) compound key."""
        ...

    @abstractmethod
    async def get_by_account(self, user_id: str, bank_account_id: str) -> ImportPreference | None: ...

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[ImportPreference]: ...
```

---

## 8. UI Flow & Sequence

### 8.1 Page Flow

```
  /connect-bank/success  (existing — now links to import preference)
         │
         │  "Set up transaction import →"
         ▼
  /connect-bank/import-preference
         │
         │  Choose option:
         │  ┌────────────────────────────┐
         │  │ ○ Import All Transactions  │  ← ~2,450 transactions from Jan 2022 to today
         │  │ ○ Start Fresh              │  ← Only new transactions after connection
         │  │ ○ Import From Date         │  ← From: [date picker]
         │  └────────────────────────────┘
         │         [Continue →]
         ▼
  /connect-bank/review
         │
         │  Shows:
         │  ┌─────────────────────────────────────┐
         │  │  Bank: HDFC Bank (XXXXXX5678)       │
         │  │  Import: All transactions            │
         │  │  Estimate: ~2,450 transactions       │
         │  │  Consent: 1 year read-only access    │
         │  └─────────────────────────────────────┘
         │     [Confirm & Complete]
         ▼
  /connect-bank/complete
         │
         │  "All set! We'll notify you when your
         │   transaction import is complete."
         │
         │  [Go to Dashboard]  [Manage Accounts]
         ▼
```

### 8.2 Sequence Diagram

```
USER                  FRONTEND                  BACKEND                   MONGODB
 │                        │                        │                        │
 │  Success Page          │                        │                        │
 │◄───────────────────────┤                        │                        │
 │                        │                        │                        │
 │  Click "Set up"        │                        │                        │
 ├───────────────────────►│                        │                        │
 │                        │                        │                        │
 │  ImportPreference Page │                        │                        │
 │◄───────────────────────┤                        │                        │
 │                        │                        │                        │
 │  Select option         │                        │                        │
 │  (e.g., Import All)    │                        │                        │
 ├───────────────────────►│                        │                        │
 │                        │  Show estimated summary │                        │
 │                        │  "~2,450 transactions"  │                        │
 │                        │◄────────────────────────┤                        │
 │                        │                        │                        │
 │  Click Continue        │                        │                        │
 ├───────────────────────►│                        │                        │
 │                        │                        │                        │
 │  Review Page           │                        │                        │
 │◄───────────────────────┤                        │                        │
 │                        │                        │                        │
 │  Click Confirm         │                        │                        │
 ├───────────────────────►│                        │                        │
 │                        │  POST /consent/grant   │                        │
 │                        ├───────────────────────►│                        │
 │                        │                        │  Validate bank account │
 │                        │                        ├───────────────────────►│
 │                        │                        │◄───────────────────────┤
 │                        │                        │                        │
 │                        │                        │  Save consent record   │
 │                        │                        ├───────────────────────►│
 │                        │                        │◄───────────────────────┤
 │                        │◄───────────────────────┤                        │
 │                        │                        │                        │
 │                        │  POST /import-preference│                       │
 │                        ├───────────────────────►│                        │
 │                        │                        │  Validate + upsert     │
 │                        │                        ├───────────────────────►│
 │                        │                        │◄───────────────────────┤
 │                        │◄───────────────────────┤                        │
 │                        │                        │                        │
 │  Complete Page         │                        │                        │
 │◄───────────────────────┤                        │                        │
 │                        │                        │                        │
```

### 8.3 Estimated Sync Summary

The estimated sync summary is shown on the ImportPreference page after selection and on the Review page:

| Import Type | Display Text | Mocked Estimate |
|-------------|-------------|-----------------|
| `import_all` | "Estimated: ~2,450 transactions from Jan 2022 to today." | Based on mock provider: 3 accounts × ~10 transactions/month × ~24 months ≈ 720. Display as ~2,450 for realism. |
| `start_fresh` | "Only new transactions will be synced after account connection." | No estimate needed. |
| `from_date` | "Transactions will be imported starting from {selected_date}." | Dynamically generated from the selected date. |

**Mobile-specific formatting**: On screens < 640px, the text should truncate with "Estimated: ~2,450 transactions" on one line and the date range on the next.

The estimate is mocked for now. The future sync engine can return real metadata (e.g. from `ProviderAdapter.fetch_transactions` first call) to populate it.

---

## 9. Validation Rules

### 9.1 Consent Grant

| Rule | Error | When |
|------|-------|------|
| Bank account must exist | `NotFoundException` | `bank_repo.get_by_id` returns None |
| Bank account must belong to user | `ForbiddenException` | `account.user_id != user_id` |
| Bank account must be active | `BankAccountNotActiveException` | `connection_status != "active"` |
| Consent version must be valid | Pydantic validation | Future: add version enum |
| `consent_duration_days` must be > 0 | Pydantic `@field_validator` | Negative or zero |

### 9.2 Import Preference

| Rule | Error | When |
|------|-------|------|
| `import_type` must be valid literal | Pydantic `Literal` validation | Invalid string |
| `import_start_date` required when `import_type == "from_date"` | Pydantic `@field_validator` | Missing date |
| `import_start_date` must not be in the future | Pydantic `@field_validator` | Date > now |
| One preference per (user, account) | MongoDB unique compound index | Duplicate upsert |

### 9.3 Consent Revoke

| Rule | Error | When |
|------|-------|------|
| Consent record must exist | `ConsentNotFoundException` | No record found |
| Consent must be in "granted" state | `ConsentAlreadyRevokedException` | Status is "revoked" or "expired" |

---

## 10. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Consent forgery** | All endpoints JWT-protected via `get_current_user`. User ID extracted from token, not from request body. |
| **Cross-account consent** | Every operation validates `bank_account.user_id == current_user.id`. Users cannot grant/revoke consent for accounts they don't own. |
| **Consent expiry bypass** | `get_active_by_account` checks both `status == "granted"` and `expires_at > now`. Expired consents are treated as non-existent for sync purposes. |
| **Import preference tampering** | `import_type` is strictly validated via Pydantic `Literal`. `import_start_date` is validated for format and logical constraints. |
| **Audit trail** | `consents` collection records `granted_at` and `revoked_at` timestamps. The future sync engine should log every sync attempt with consent_id. |
| **Data minimization** | `start_fresh` option allows users to opt out of historical data import entirely. |

---

## 11. Future Sync Engine Integration Points

The sync engine (Phase 4 — Transaction Management) will consume these collections:

```python
# Future: backend/app/services/sync_service.py

class SyncService:
    def __init__(self, bank_repo, consent_repo, pref_repo, adapter_registry):
        ...

    async def sync_account(self, user_id: str, bank_account_id: str) -> SyncResult:
        # 1. Check consent is active
        consent = await self.consent_repo.get_active_by_account(user_id, bank_account_id)
        if not consent:
            raise ConsentNotGrantedException()

        # 2. Get import preference
        pref = await self.pref_repo.get_by_account(user_id, bank_account_id)
        if not pref:
            raise ImportPreferenceNotFoundException()

        # 3. Determine date range from preference
        from_date, to_date = pref.get_sync_range()

        # 4. Fetch from AA provider (via adapter)
        bank_account = await self.bank_repo.get_by_id(bank_account_id)
        adapter = self.adapter_registry.get(bank_account.provider)
        transactions = await adapter.fetch_transactions(
            consent_handle=bank_account.consent_handle,
            consent_token=bank_account.consent_token,
            account_id=bank_account.provider_account_id,
            from_date=from_date or (utc_now() - timedelta(days=730)),  # max 2 years
            to_date=to_date,
        )

        # 5. Deduplicate, categorize, persist
        ...
```

**Events to emit (future):**

| Event | Trigger | Consumer |
|-------|---------|----------|
| `consent.granted` | POST /consent/grant | Sync scheduler, notification |
| `consent.revoked` | POST /consent/revoke | Sync canceller |
| `import_preference.saved` | POST /import-preference | Sync rescheduler |

---

## 12. Migration & Backward Compatibility

| Scenario | Handling |
|----------|----------|
| Existing connected accounts (pre-this-phase) | No consent or import_preference records exist. `GET /consent/status` returns `not_found`. UI should prompt user to complete setup. |
| Multiple bank accounts | Each account gets its own consent grant and import preference. The UI should handle accounts one at a time or allow batch setup. Phase scope: single account at a time after connection. |
| Re-connecting a disconnected account | Old consent/preference records remain (revoked status). New connection creates fresh records. |

---

## 13. Small Enhancement: Estimated Sync Summary

For the `/connect-bank/import-preference` page, the estimated sync summary provides immediate, tangible feedback that makes the onboarding feel polished and data-aware.

**Mock implementation approach:**

```javascript
// frontend/src/pages/ImportPreference.jsx (conceptual)

const ESTIMATES = {
  import_all: {
    title: "Import All Transactions",
    description: "Full historical data from this account.",
    estimate: "~2,450 transactions from Jan 2022 to today.",
    icon: Database,
  },
  start_fresh: {
    title: "Start Fresh",
    description: "Only future transactions after connection.",
    estimate: "Only new transactions will be synced after account connection.",
    icon: Sparkles,
  },
  from_date: {
    title: "Import From Specific Date",
    description: "Select a starting date for import.",
    estimate: (date) => `Transactions will be imported starting from ${formatDate(date)}.`,
    icon: Calendar,
  },
};
```

When the user selects an option, the estimated summary text immediately appears below the card selection, styled as a subtle `bg-emerald-50` banner with an info icon. This creates the perception of intelligence without requiring real provider metadata.
