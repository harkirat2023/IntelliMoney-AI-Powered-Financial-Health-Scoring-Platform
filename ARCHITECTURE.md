# IntelliMoney Architecture

## 1. EXISTING ARCHITECTURE ANALYSIS

### 1.1 Folder Structure (Current)

```
IntelliMoney/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app entry, lifespan, middleware
│   │   ├── ai/                               # AI Intelligence Pipeline (V1.5)
│   │   │   ├── __init__.py
│   │   │   ├── category_service.py           # CategoryPredictionService
│   │   │   ├── confidence_service.py         # ConfidenceService (weighted scoring)
│   │   │   ├── feedback_service.py           # FeedbackLearningService
│   │   │   ├── financial_transaction_service.py  # Orchestrator service
│   │   │   ├── income_service.py             # IncomeDetectionService
│   │   │   ├── merchant_service.py           # MerchantNormalizationService (wrapper)
│   │   │   ├── models.py                     # PipelineTransaction DTO
│   │   │   ├── pipeline.py                   # 9-stage ProcessingPipeline
│   │   │   ├── recurring_service.py          # RecurringDetectionService
│   │   │   └── validation_service.py         # ValidationService
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                      # Auth dependency (get_current_user)
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                  # register, login, me
│   │   │   │   ├── sync.py                  # 5 sync endpoints
│   │   │   │   ├── bank.py                  # 5 bank connection endpoints
│   │   │   │   ├── consent.py               # 3 consent endpoints
│   │   │   │   ├── import_preference.py     # 2 import preference endpoints
│   │   │   │   ├── intelligence.py          # NEW — 8 intelligence endpoints
│   │   │   │   ├── financial_transactions.py # NEW — 3 financial tx endpoints
│   │   │   │   ├── expenses.py              # CRUD + filters
│   │   │   │   ├── budgets.py               # CRUD + status
│   │   │   │   ├── analytics.py             # summary, monthly, categories, payment, recent
│   │   │   │   ├── financial_health.py      # score
│   │   │   │   ├── recommendations.py       # list
│   │   │   │   ├── ml.py                    # categorize
│   │   │   │   ├── alerts.py                # list, mark-read
│   │   │   │   ├── anomaly.py               # list, detect, alerts, weekly-report, mark-read
│   │   │   │   ├── budget_suggestion.py     # list, generate, apply, dismiss, optimization-report
│   │   │   │   ├── reports.py               # list, summary, generate-weekly, generate-monthly, mark-read
│   │   │   │   ├── subscriptions.py         # CRUD, suggestions, insights, record-payment
│   │   │   │   └── recurring.py             # CRUD, suggestions, upcoming
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py                # Aggregates all route modules
│   │   │       └── websocket.py             # WS endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                    # Pydantic Settings
│   │   │   ├── constants.py                 # Categories, CATEGORY_KEYWORD_MAP, CONFIDENCE_THRESHOLDS, TRANSACTION_TAGS, MERCHANT_CONFIDENCE_WEIGHTS
│   │   │   ├── exceptions.py                # AppException hierarchy (+3 AI exceptions)
│   │   │   ├── encryption.py                # Fernet field-level encryption
│   │   │   ├── logging.py                   # Logging config
│   │   │   ├── security.py                  # JWT, bcrypt
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── error_handler.py         # Global exception handler
│   │   │       ├── request_id.py            # X-Request-ID middleware
│   │   │       └── request_logger.py        # Request logging middleware
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── mongodb.py                   # Connection management + indexes (+bank_accounts)
│   │   ├── domain/
│   │   │   ├── bank_accounts/               # NEW — domain model + repository interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # BankAccount Pydantic domain model
│   │   │   │   └── repository.py            # Abstract bank repository interface
│   │   │   ├── consents/                    # NEW — user-facing consent domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # ConsentGrant Pydantic model with is_active(), revoke()
│   │   │   │   └── repository.py            # Abstract consent repository (6 methods)
│   │   │   ├── import_preferences/          # NEW — import preference domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # ImportPreference Pydantic model with get_sync_range()
│   │   │   │   └── repository.py            # Abstract import preference repository (3 methods)
│   │   │   ├── sync/                        # NEW — sync domain (V1.4)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # BankTransaction + SyncLog (state machine: mark_running/completed/failed, can_retry)
│   │   │   │   └── repository.py            # Abstract BankTransactionRepository (6 methods) + SyncLogRepository (9 methods)
│   │   │   ├── financial_transactions/      # NEW — AI Transaction domain (V1.5)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # FinancialTransaction (24 fields, from_mongo/to_mongo, ReviewStatus)
│   │   │   │   └── repository.py            # Abstract FinancialTransactionRepository (11 methods)
│   │   │   ├── expenses/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py                # Expense Pydantic domain model
│   │   │   │   └── repository.py            # Abstract repository interface
│   │   │   ├── recurring/
│   │   │   │   └── __init__.py
│   │   │   └── users/
│   │   │       ├── __init__.py
│   │   │       ├── models.py                # User Pydantic domain model
│   │   │       └── repository.py            # Abstract repository interface
│   │   ├── infrastructure/
│   │   │   ├── bank_integration/            # Provider adapters + consent manager
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                  # Abstract BankProviderAdapter
│   │   │   │   ├── mock_provider.py         # Mock AA provider (3 accounts, 30 txs)
│   │   │   │   ├── consent_manager.py       # Consent lifecycle + provider registry
│   │   │   │   ├── dtos.py                  # DTOs for provider communication
│   │   │   │   └── merchant/                # NEW — Merchant Normalization
│   │   │   │       ├── __init__.py
│   │   │   │       ├── merchant_data.py     # 31 merchants with alias patterns
│   │   │   │       └── merchant_normalizer.py  # Clean + 3-tier alias match + cache
│   │   │   ├── cache/
│   │   │   │   ├── __init__.py
│   │   │   │   └── redis.py                 # Redis cache client
│   │   │   ├── database/
│   │   │   │   └── repositories/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── bank_repository.py   # Mongo bank repository implementation (NEW)
│   │   │       ├── consent_repository.py       # Mongo consent repository
│   │   │       ├── import_preference_repository.py # Mongo import preference repo
│   │   │       ├── sync_repository.py          # Mongo BankTransaction + SyncLog repos
│   │   │       └── intelligence/               # NEW — AI intelligence repos
│   │   │           ├── __init__.py
│   │   │           ├── financial_transaction_repository.py  # MongoFinancialTransactionRepository
│   │   │           ├── feedback_repository.py               # MongoFeedbackRepository
│   │   │           └── merchant_repository.py               # MongoMerchantRepository
│   │   │   │       ├── expense_repository.py # Mongo implementation
│   │   │   │       └── user_repository.py    # Mongo implementation
│   │   │   ├── messaging/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── event_bus.py             # In-memory event bus
│   │   │   │   └── events.py                # Event dataclass
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                  # WS token validation
│   │   │       └── manager.py               # Connection manager
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── expense_classifier.joblib     # Trained model
│   │   │   └── README.md
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── documents.py                 # TypedDict schemas (+BankAccountDocument, ConsentDocument, ImportPreferenceDocument)
│   │   ├── presentation/
│   │   │   ├── __init__.py
│   │   │   └── serializers.py               # _id -> id, user_id str
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── ai.py                        # NEW — ProcessPendingRequest, ProcessResultResponse, ReviewQueueResponse, ReviewSubmissionRequest, FeedbackSubmissionRequest, FeedbackResponse, IntelligenceStatusResponse (V1.5)
│   │   │   ├── financial_transactions.py    # NEW — FinancialTransactionResponse (20 fields, from_domain), FinancialTransactionUpdateRequest (V1.5)
│   │   │   ├── sync.py                      # SyncStartRequest/Response, SyncStatusResponse, SyncHistoryResponse, SyncRetryRequest/Response (V1.4)
│   │   │   ├── bank.py                      # Bank request/response schemas
│   │   │   ├── consent.py                   # Consent grant/revoke/status schemas
│   │   │   ├── import_preference.py         # Import preference request/response schemas
│   │   │   ├── common.py                    # PyObjectId, TimestampMixin
│   │   │   ├── user.py                      # UserCreate, UserLogin, UserPublic, Token
│   │   │   ├── expense.py                   # ExpenseCreate, ExpenseUpdate, ExpensePublic
│   │   │   ├── budget.py                    # BudgetCreate, BudgetUpdate, BudgetPublic, BudgetStatus
│   │   │   ├── analytics.py                 # SummaryResponse, ChartPoint, RecentExpense, etc.
│   │   │   ├── ml.py                        # CategorizeRequest, CategorizeResponse
│   │   │   ├── alert.py                     # BudgetAlertPublic
│   │   │   ├── anomaly.py                   # SpendingAnomaly, AnomalyAlert, WeeklySpendingReport
│   │   │   ├── budget_suggestion.py          # BudgetSuggestion, BudgetOptimizationReport
│   │   │   ├── report.py                    # FinancialReport, ReportSummary
│   │   │   ├── subscription.py              # Subscription, SubscriptionSuggestion, etc.
│   │   │   └── recurring.py                 # RecurringExpenseCreate, etc.
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── intelligence_service.py      # NEW — singleton-per-app factory wiring all AI services + pipeline + repos + event bus (V1.5)
│   │   │   ├── sync_service.py              # Sync orchestration: start, manual_all, status, history, retry, _execute_sync (V1.4)
│   │   │   ├── bank_service.py              # Connection, consent, status, disconnect
│   │   │   ├── consent_grant_service.py     # Grant/revoke/get_status for user-facing consent
│   │   │   ├── import_preference_service.py # Save/get import type preference
│   │   │   ├── serializers.py               # Re-exports from utils/presentation
│   │   │   ├── ml_service.py                # ExpenseCategorizer
│   │   │   ├── analytics_service.py         # Summary, category breakdown, monthly, recent
│   │   │   ├── budget_service.py            # Budget status calculation
│   │   │   ├── financial_service.py         # Financial health scoring
│   │   │   ├── recommendation_service.py    # Rule-based recommendations
│   │   │   ├── alert_service.py             # Budget alert sync + thresholds
│   │   │   ├── anomaly_service.py           # Spending anomaly detection
│   │   │   ├── budget_suggestion_service.py  # Budget optimization suggestions
│   │   │   ├── report_service.py            # Weekly/monthly report generation
│   │   │   ├── subscription_service.py      # Subscription CRUD + detection
│   │   │   ├── recurring_service.py         # Recurring expense CRUD + detection
│   │   │   └── notification_service.py      # Protocol + noop notifier
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── date_utils.py                # utc_now, month_bounds, date_to_datetime
│   │       ├── frequency.py                 # _calculate_next_date, _detect_frequency
│   │       └── object_id.py                 # to_object_id
│   ├── tests/
│   │   ├── test_backend_flows.py            # Integration tests with fakes
│   │   └── test_ml_service.py               # ML categorization tests
│   ├── seed_demo.py                         # Demo data seeder
│   ├── .env / .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx                         # Entry point
│   │   ├── App.jsx                          # Router config (+bank routes)
│   │   ├── styles.css                       # Global styles
│   │   ├── api/
│   │   │   ├── client.js                    # Axios instance + interceptor
│   │   │   └── bank.js                      # API client (5 methods) (NEW)
│   │   ├── auth/
│   │   │   └── AuthContext.jsx              # Auth context + provider
│   │   ├── components/
│   │   │   ├── bank/                        # NEW — bank UI components
│   │   │   │   ├── BankCard.jsx             # Account card with status badge
│   │   │   │   └── DisconnectDialog.jsx     # Revoke confirmation modal
│   │   │   ├── ProtectedRoute.jsx           # Auth guard
│   │   │   ├── ErrorBoundary.jsx            # Error boundary
│   │   │   └── AlertBell.jsx                # Budget alert dropdown
│   │   ├── config/
│   │   │   └── constants.js                 # Categories, methods, frequencies
│   │   ├── hooks/
│   │   │   ├── useApi.js                    # Generic API hook
│   │   │   ├── useStore.js                  # Store subscription hook
│   │   │   └── useWebSocket.js             # WebSocket hook with reconnect
│   │   ├── layouts/
│   │   │   └── AppLayout.jsx                # Sidebar + topbar + outlet (+bank link)
│   │   ├── pages/
│   │   │   ├── ConnectBank.jsx              # NEW — provider selection + initiate
│   │   │   ├── ConsentPage.jsx              # NEW — consent confirmation
│   │   │   ├── ConnectSuccess.jsx           # NEW — success confirmation
│   │   │   ├── ManageAccounts.jsx           # NEW — account management + revoke
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Expenses.jsx
│   │   │   ├── Budgets.jsx
│   │   │   ├── BudgetOptimizer.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── Recurring.jsx
│   │   │   ├── Subscriptions.jsx
│   │   │   └── Anomaly.jsx
│   │   ├── store/
│   │   │   ├── authStore.js                 # Auth store (observer pattern)
│   │   │   ├── dashboardStore.js            # Dashboard data store
│   │   │   └── notificationStore.js         # Notification store
│   │   └── utils/
│   │       └── format.js                    # Currency formatting
│   ├── webpack.config.js
│   ├── package.json
│   ├── .env / .env.example
│   ├── index.html
│   └── .babelrc
├── ml/
│   ├── train_model.py                       # TF-IDF + Logistic Regression training
│   └── data/
│       └── expenses.csv                     # Training data
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx/
│       └── default.conf
├── scripts/
│   └── create_indexes.py                    # Standalone index creation
├── docs/
│   ├── api-overview.md
│   └── bank-connect-design.md               # Bank connection architecture (NEW)
├── docker-compose.yml
├── start_all.py                             # Dev startup script
├── project_structure.txt
└── README.md
```

### 1.2 Architecture Style

**Monolithic Backend + SPA Frontend**

- **Backend**: Single FastAPI application with modular route files. Uses a layered structure (routes -> services -> infrastructure). Bank module follows clean architecture (repository pattern, domain models, provider adapter abstraction).
- **Frontend**: Single-page React application built with Webpack. Uses React Context for auth, custom observer-pattern stores for state, and Axios for HTTP. Bank pages use `useAuth()` for authorization guards.
- **Database**: MongoDB with Motor (async driver). Indexes created at startup in `mongodb.py`. `bank_accounts` collection added with consent/connection indexes.

### 1.3 Architecture Patterns Detected

| Pattern | Status | Location |
|---------|--------|----------|
| Repository Pattern | Partial | `domain/*/repository.py` (abstract), `infrastructure/database/repositories/` (concrete) — bank uses it fully; other domains partially |
| Event Bus | Present and active (V1.5) | `infrastructure/messaging/event_bus.py` — publishes `ai.pipeline.completed`, `ai.feedback.recorded`, `ai.review.submitted` |
| WebSocket Manager | Present | `infrastructure/websocket/manager.py` |
| Middleware Pipeline | Present | CORS, RequestID, RequestLogger, ErrorHandler |
| Provider Adapter | Implemented for Bank | `infrastructure/bank_integration/base.py` + `mock_provider.py` |
| Observer Stores (frontend) | Present | `store/*.js` |
| Context Provider (frontend) | Present | `auth/AuthContext.jsx` |
| Dependency Injection | Partial | FastAPI `Depends` for DB and auth |
| Field-Level Encryption | Implemented for Bank | `core/encryption.py` — Fernet AES-256-GCM |

### 1.4 Data Flow Diagram

```
Browser (React SPA)
    │
    ├── Axios ──► HTTP ──► FastAPI Router ──► Route Handler
    │                                                  │
    │                                          ┌───────┴───────┐
    │                                          │   Services    │
    │                                          │  (business    │
    │                                          │   logic)      │
    │                                          └───────┬───────┘
    │                                                  │
    │                                          ┌───────┴───────┐
    │                                          │ Infrastructure│
    │                                          │ (Mongo/Redis/ │
    │                                          │  AA Provider) │
    │                                          └───────┬───────┘
    │                                                  │
    │                                          ┌───────┴───────┐
    │                                          │   MongoDB     │
    │                                          │   + AA API    │
    │                                          └───────────────┘
    │
    └── WebSocket ──► WS ──► FastAPI WS ──► ConnectionManager
```

**Bank Connection Specific Flow:**
```
ConnectBank → POST /connect → AA Provider Initiate → Redirect to AA URL
    → User auths at AA → AA redirects back → POST /consent
    → Verify consent → Fetch accounts → Encrypt & store → Redirect to Success
    → (NEW) ImportPreference → POST /consent/grant + POST /import-preference/ → Complete
```

**Consent + Import Preference Flow (V1.3):**
```
Success → ImportPreference Page (select import_all/start_fresh/from_date)
    → Review Page (confirm details) → POST /consent/grant + POST /import-preference/
    → Complete Page (done)
```

**Sync Engine Flow (V1.4):**
```
Sync Page → POST /sync/start (or /manual) → SyncService._execute_sync()
    → Validate BankAccount ownership
    → Check ConsentGrant.is_active()
    → Resolve ImportPreference.get_sync_range()
    → Decrypt provider_token + account_id via FieldEncryptor
    → Call ProviderAdapter.fetch_transactions() (with 120s timeout)
    → bulk_create() with compound unique index (dedup)
    → Update BankAccount.last_synced_at
    → Update SyncLog (completed with fetched/imported/skipped counts)
```

**AI Intelligence Pipeline Flow (V1.5):**
```
POST /intelligence/process → FinancialTransactionService.process_pending()
    → Find unprocessed bank_tx_ids ($nin query)
    → ProcessingPipeline.process_batch() (asyncio.gather, semaphore 10)
        → 1. ValidationService.validate_bank_transaction()
        → 2. MerchantNormalizationService.normalize() (clean + 3-tier alias)
        → 3. IncomeDetectionService.classify() (DEBIT/CREDIT analysis)
        → 4. CategoryPredictionService.predict() (merchant → ML → keyword)
        → 5. RecurringDetectionService.detect() (subscriptions + utilities)
        → 6. ConfidenceService.calculate() (5-factor weighted)
        → 7. ConfidenceService.determine_review_status() (0.95/0.70 thresholds)
        → 8. Build FinancialTransaction model (24 fields)
        → 9. bulk_create() with bank_transaction_id unique index (dedup)
    → Publish ai.pipeline.completed event
    → Return ProcessResultResponse
```

### 1.5 API Structure

- Base: `/api/v1/`
- Versioned via `prefix="/api/v1"` in main.py
- Legacy redirect: `/api/{path}` -> `/api/v1/{path}`
- Health: `/api/health`
- Bank routes: `/api/v1/bank/*` (5 endpoints, all JWT-protected)
- Sync routes: `/api/v1/sync/*` (5 endpoints, all JWT-protected)
- Intelligence routes: `/api/v1/intelligence/*` (8 endpoints + 3 financial-transactions endpoints, all JWT-protected)

### 1.6 Database Collections (MongoDB)

| Collection | Key Fields | Indexes |
|------------|-----------|---------|
| users | email, name, hashed_password, monthly_income | email (unique) |
| expenses | user_id, amount, description, category, payment_method, date | (user_id, date) |
| budgets | user_id, category, limit, month, year | (user_id, category, month, year) unique |
| budget_alerts | user_id, budget_id, threshold, percentage, message | (user_id, created_at), (user_id, budget_id, threshold) unique |
| financial_scores | user_id, score, risk_level, savings_rate | (user_id, calculated_at) |
| recommendations | user_id, items, created_at | (user_id, created_at) |
| spending_anomalies | user_id, category, amount, severity | (user_id, created_at), (user_id, is_read) |
| budget_suggestions | user_id, category, current/suggested_limit | (user_id, is_applied) |
| financial_reports | user_id, report_type, totals, insights | (user_id, generated_at), (user_id, report_type) |
| recurring_expenses | user_id, description, frequency, dates | (user_id, is_active), (user_id, next_expected_date) |
| subscriptions | user_id, description, amount, frequency | (user_id, is_active), (user_id, next_payment_date) |
| **bank_accounts** | user_id, provider, bank_name, masked_account_number, account_type, connection_status, consent_status, consent_expiry, provider_account_id (encrypted), consent_token (encrypted) | (user_id, connection_status), (user_id, provider), (consent_handle) unique sparse, (consent_expiry) TTL |
| **consents** | user_id, bank_account_id, consent_status (granted/revoked/expired), consent_version, granted_at, expires_at, revoked_at | (user_id, bank_account_id), (bank_account_id), (consent_status, expires_at) |
| **import_preferences** | user_id, bank_account_id, import_type (import_all/start_fresh/from_date), import_start_date | (user_id, bank_account_id) unique, (bank_account_id) |
| **bank_transactions** | user_id, bank_account_id, sync_log_id, provider_account_id, transaction_id, description, amount, transaction_type (DEBIT/CREDIT), transaction_date, category, reference, created_at | (provider_account_id, transaction_id) unique, (user_id, bank_account_id, transaction_date) |
| **sync_logs** | user_id, bank_account_id, sync_type (initial/manual/retry), status (pending/running/completed/failed), started_at, completed_at, transactions_fetched/imported/skipped, error_message, error_category, retry_count, max_retries | (user_id, bank_account_id, created_at), (user_id, status) |
| **financial_transactions** (NEW) | user_id, bank_account_id, bank_transaction_id, sync_log_id, provider_account_id, transaction_id, original_description, amount, transaction_type, transaction_date, original_category, reference, cleaned_merchant, normalized_merchant, merchant_id, assigned_category, confidence_score, is_income, is_recurring, recurring_id, transaction_tags, is_refund, is_transfer, review_status, reviewed_by, reviewed_at, review_note, processed_at, created_at, updated_at | (bank_transaction_id) unique, (user_id, transaction_date), (user_id, assigned_category), (user_id, review_status) |
| **merchant_dictionary** (NEW) | merchant_name, display_name, category, is_active | (merchant_name) unique |
| **merchant_aliases** (NEW) | merchant_name, alias_type (exact/contains/regex), pattern, priority, is_active | (alias_type, priority) |
| **category_feedback** (NEW) | user_id, financial_transaction_id, original_description, original_merchant, suggested_category, user_category, feedback_type | (user_id, created_at), (suggested_category) |
| **transaction_tags** (NEW) | user_id, name, color | (user_id, name) unique |

---

## 2. ARCHITECTURAL ANALYSIS

### 2.1 Strengths

1. **Clean layered skeleton**: The domain/infrastructure split shows awareness of clean architecture principles. Repository interfaces exist.
2. **Good middleware stack**: Request ID tracking, request logging, global error handler, CORS.
3. **Event bus infrastructure**: Event-driven architecture foundation exists (though unused).
4. **WebSocket infrastructure**: Connection manager and WS auth exist.
5. **Comprehensive schema layer**: Pydantic models for all endpoints with validation.
6. **TypedDict document models**: MongoDB document shapes documented.
7. **Custom exception hierarchy**: AppException with typed subclasses.
8. **Health check endpoint**: Simple but present.
9. **Dual auth system**: Both AuthContext (React) and authStore exist (though redundant).
10. **Comprehensive test suite**: Fakes-based testing for backend flows.
11. **Provider Adapter Pattern**: Bank module uses clean abstract interface with registry — mock now, real providers later.
12. **Field-level encryption**: Sensitive bank data encrypted at rest with Fernet.
13. **Consent lifecycle management**: Full create/verify/revoke/expiry flow.

### 2.2 Code Smells & Technical Debt

| Issue | Location | Severity | Recommendation |
|-------|----------|----------|----------------|
| **Mixed DB access patterns** | `services/*.py` query MongoDB directly via `db.collection.find()` instead of using repositories | HIGH | Migrate all services to use repository abstractions |
| **Unused repository interfaces** | `domain/*/repository.py` - abstract, `infrastructure/database/repositories/` - concrete, but never referenced by services | HIGH | Either use them or remove them |
| **Event bus — publishers active, no subscribers** | `infrastructure/messaging/event_bus.py` — publishers exist for ai.pipeline.completed, ai.feedback.recorded, ai.review.submitted, but no subscribers yet | MEDIUM | Add downstream consumers (Dashboard, Budget Engine, Health Engine) |
| **Reactive vs. polling on frontend** | All pages poll APIs on mount instead of using WebSocket push | MEDIUM | Migrate to event-driven updates |
| **Dual state management** | Both `authStore.js` (observer) and `AuthContext.jsx` (Context) manage auth state | MEDIUM | Consolidate to one pattern |
| **Unused notification** | `notification_service.py` - protocol defined but only noop implementation | LOW | Implement or remove |
| **Hardcoded categories** | `constants.py` categories duplicated in frontend `config/constants.js` | LOW | Create shared config or API endpoint |
| **ML model path hardcoded** | `ml_service.py:8` - MODEL_PATH uses relative path resolution | LOW | Use config/settings |
| **No background task framework** | Anomaly detection, report generation, budget suggestion generation, consent expiry checking run synchronously in request-response cycle | MEDIUM | Use Celery/ARQ for background tasks |
| **No rate limiting** | No rate limiting on auth endpoints | MEDIUM | Add rate limiting |
| **Password in response** | No password in response (good) but recovery flow missing | LOW | Add password reset |
| **Seed script in backend** | `seed_demo.py` lives in backend but is a standalone script | LOW | Move to scripts/ |
| **No request validation logging** | No structured logging of request bodies for debugging | LOW | Add debug-level request body logging |
| **`start_all.py` uses shell=True** | Security concern for production | MEDIUM | Remove for prod, use docker-compose |
| **Webpack vs Vite confusion** | README mentions Vite but uses Webpack | LOW | Fix documentation |
| **No real AA adapters** | Only mock provider exists (Setu, Finvu, OneMoney, Perfios stubs not implemented) | MEDIUM | Phase 3 — implement once AA credentials are available |
| **Consent expiry background check** | `check_expired_consents` is defined but not scheduled as background task | MEDIUM | Add to Celery/ARQ or FastAPI lifespan |

---

## 3. IntelliMoney V2 ARCHITECTURE

### 3.1 Architecture Vision

```
                    ┌─────────────────────────────────────┐
                    │          API Gateway / Nginx         │
                    │     SSL Termination, Rate Limit      │
                    └────────┬────────────┬───────────────┘
                             │            │
                    ┌────────┴────┐ ┌─────┴──────────┐
                    │  FastAPI    │ │  WebSocket     │
                    │  REST API  │ │  Server        │
                    │  (Stateless)│ │  (Stateful)    │
                    └──────┬─────┘ └───────┬──────────┘
                           │               │
                    ┌──────┴───────────────┴──────┐
                    │       Service Layer          │
                    │  (Business Logic Only)       │
                    └──────┬──────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐
   │  Repository │  │  Event Bus │  │  AI/ML     │
   │  Layer      │  │  (Redis)   │  │  Services  │
   └──────┬──────┘  └────────────┘  └─────┬──────┘
          │                                │
   ┌──────┴──────┐                  ┌──────┴──────┐
   │   MongoDB   │                  │  LangChain  │
   │   + Redis   │                  │  + Models   │
   └─────────────┘                  └─────────────┘
```

### 3.2 V2 Folder Structure — Bank Integration Additions

The current bank module already follows V2 architecture:

```
infrastructure/bank_integration/
├── base.py                  # Abstract BankProviderAdapter
├── mock_provider.py         # Mock (dev/testing)
├── setu_adapter.py          # FUTURE — Setu AA
├── finvu_adapter.py         # FUTURE — Finvu AA
├── onemoney_adapter.py      # FUTURE — OneMoney AA
├── consent_manager.py       # Consent lifecycle orchestrator
└── dtos.py                  # Provider communication DTOs
```

### 3.3 Backend Architecture (V2)

```
┌──────────────────────────────────────────────────────────────┐
│                     API Layer (routes/)                      │
│  Thin handlers: parse request, call service, return response │
├──────────────────────────────────────────────────────────────┤
│                     Service Layer (services/)                │
│  Business logic, orchestration, no direct DB access          │
├──────────────────────────────────────────────────────────────┤
│                  Domain Layer (domain/)                      │
│  Entities, value objects, repository interfaces              │
├──────────────────────────────────────────────────────────────┤
│               Infrastructure Layer (infrastructure/)         │
│  DB implementations, external APIs, cache, messaging, OCR   │
├──────────────────────────────────────────────────────────────┤
│                    AI/ML Layer (ai/)                         │
│  ML models, LangChain agents, forecasting, OCR processing   │
├──────────────────────────────────────────────────────────────┤
│                 Background Tasks (tasks/)                    │
│  Celery workers for sync, reports, alerts, anomaly detection│
└──────────────────────────────────────────────────────────────┘
```

Bank module already conforms to this:
- Routes: `bank.py` — thin handlers
- Service: `bank_service.py` — business logic (initiate, consent, list, status, disconnect)
- Domain: `bank_accounts/` — domain model + repository interface
- Infrastructure: `bank_integration/` — provider adapters + consent manager; `database/repositories/bank_repository.py` — Mongo impl

### 3.4 Frontend Architecture (V2)

```
┌──────────────────────────────────────────────┐
│          Pages (pages/)                      │
│  Route-level components, compose features    │
├──────────────────────────────────────────────┤
│        Features (features/)                  │
│  Domain-specific feature modules             │
├──────────────────────────────────────────────┤
│     Shared Components (components/)          │
│  ui/ (primitives), charts/ (reusable)       │
├──────────────────────────────────────────────┤
│       State (store/ + Context)              │
│  Zustand for global state, Context for auth  │
├──────────────────────────────────────────────┤
│     API Layer (api/)                        │
│  Domain-specific API modules                │
├──────────────────────────────────────────────┤
│     Hooks (hooks/)                          │
│  Shared hooks: useApi, useWebSocket, useStore│
└──────────────────────────────────────────────┘
```

Bank frontend follows this:
- Pages: `ConnectBank.jsx`, `ConsentPage.jsx`, `ConnectSuccess.jsx`, `ManageAccounts.jsx`
- Components: `bank/BankCard.jsx`, `bank/DisconnectDialog.jsx`
- API: `api/bank.js` — domain-specific API client
- Auth: `useAuth()` guard on all bank pages

### 3.5 AI/ML Architecture (V2)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        AI Intelligence Layer (ai/)                       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                ProcessingPipeline (9-stage)                     │    │
│  │  Validate → Merchant Normalize → Income/Expense Detect →       │    │
│  │  Category Predict → Recurring Detect → Confidence Score →      │    │
│  │  Review Decide → Build Model → Bulk Persist                    │    │
│  └─────────────────────────┬───────────────────────────────────────┘    │
│                            │                                            │
│  ┌─────────────────────────┴───────────────────────────────────────┐    │
│  │                    AI Services (7)                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │    │
│  │  │ Merchant     │ │ Category     │ │ Confidence           │    │    │
│  │  │ Normalization│ │ Prediction   │ │ Scoring (5-factor)   │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘    │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │    │
│  │  │ Recurring    │ │ Income       │ │ Feedback Learning    │    │    │
│  │  │ Detection    │ │ Detection    │ │ (category_feedback)  │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘    │    │
│  │  ┌─────────────────────────────────────────────────────────┐   │    │
│  │  │ ValidationService (guard for all inputs)                │   │    │
│  │  └─────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────┬───────────────────────────────────────┘    │
│                            │                                            │
│  ┌─────────────────────────┴───────────────────────────────────────┐    │
│  │                  Existing ML Service (reused)                   │    │
│  │  ExpenseCategorizer — TF-IDF + Logistic Regression (joblib)    │    │
│  │  Fallback: CATEGORY_KEYWORD_MAP (shared constants)              │    │
│  └─────────────────────────┬───────────────────────────────────────┘    │
│                            │                                            │
│  ┌─────────────────────────┴───────────────────────────────────────┐    │
│  │  Future: LangChain Copilot → FinancialHealth V2 → Budget Intel │    │
│  │  Future: OCR Engine → Forecasting (Prophet/ARIMA)              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.6 Event-Driven Architecture (V2)

```
Event Types:
├── user.registered
├── expense.created / updated / deleted
├── budget.created / alert_triggered / threshold_reached
├── bank.account_connected
├── bank.account_disconnected
├── transaction.imported / synced
├── anomaly.detected
├── report.generated
├── goal.milestone_reached
├── ocr.receipt_processed
├── **ai.pipeline.completed** (NEW) — `{processed_count, failed_count, bank_account_id}`
├── **ai.feedback.recorded** (NEW) — `{tx_id, feedback_type, original_category, user_category}`
└── **ai.review.submitted** (NEW) — `{tx_id, review_status, assigned_category}`

Flow:
Producer (Service) → EventBus (Redis Pub/Sub) → Consumer (Task/WebSocket)
                                                      │
                                                      └──→ WebSocket Manager → Browser
```

### 3.7 WebSocket Architecture (V2)

```
Client connects: wss://host/api/v1/ws?token=<jwt>

Channels:
├── user:{user_id}:alerts          → Budget alerts
├── user:{user_id}:anomalies       → Spending anomalies
├── user:{user_id}:transactions    → Live transaction sync
├── user:{user_id}:notifications   → General notifications
└── user:{user_id}:copilot         → AI copilot responses

ConnectionManager (infrastructure/websocket/manager.py):
├── connect(user_id, ws)           → Join user room
├── disconnect(user_id, ws)        → Leave user room
├── send_to_user(user_id, msg)     → Send to all user sockets
├── send_to_channel(channel, msg)  → Send to channel subscribers
└── broadcast(msg)                 → Send to all
```

### 3.8 LangChain AI Copilot Architecture (V2)

```
┌─────────────────────────────────────────────────────┐
│                 LangChain Agent                      │
│                                                      │
│  Query → Prompt Template → LLM → Tool Selection      │
│                                                      │
│  Tools:                                               │
│  ├── get_spending_summary(user_id, period)           │
│  ├── get_budget_status(user_id, month, year)         │
│  ├── get_financial_score(user_id)                    │
│  ├── get_recommendations(user_id)                    │
│  ├── get_transactions(user_id, filters)              │
│  ├── create_expense(user_id, data)                   │
│  ├── get_anomalies(user_id)                          │
│  ├── get_report(user_id, report_id)                  │
│  └── get_goal_progress(user_id)                      │
│                                                      │
│  Memory:                                              │
│  ├── ConversationBuffer (short-term)                  │
│  └── RedisChatMessageHistory (persistent)             │
└─────────────────────────────────────────────────────┘
```

### 3.9 OCR Architecture (V2)

```
Upload Receipt Image → Preprocessing → OCR Engine → Structured Data
                                                │
                                          ┌─────┴─────┐
                                          │  Category  │
                                          │  Guesser   │
                                          │  (ML-based)│
                                          └─────┬─────┘
                                                │
                                          ┌─────┴─────┐
                                          │  Create    │
                                          │  Expense   │
                                          │  (Service) │
                                          └───────────┘
```

### 3.10 Deployment Architecture (V2)

```
                    ┌─────────────┐
                    │   DNS/CDN   │
                    │  (Cloudflare)│
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐
   │  FastAPI    │  │  FastAPI   │  │  Frontend  │
   │  (Web)      │  │  (API)     │  │  (Static)  │
   └──────┬──────┘  └─────┬──────┘  └────────────┘
          │                │
          │         ┌──────┴──────┐
```
