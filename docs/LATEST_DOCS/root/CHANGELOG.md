# Changelog

## [1.14.0] - 2026-07-06

### Added
- **One-Click Startup Scripts**: `scripts/start-IntelliMoney.bat` — 7-step automated startup (env validation, Docker startup, Python venv+install, uvicorn backend, npm frontend, health checks, browser open). `scripts/stop-IntelliMoney.bat` — graceful stop (backend, frontend, Docker, port cleanup).
- **Structured Logging**: Startup logs written to `logs/startup.log` with timestamps and step status.

## [1.13.0] - 2026-07-06

### Added
- **Receipt OCR & Manual Expense Import**: Image preprocessing with OpenCV (deskew, denoise, adaptive threshold, contrast enhancement).
- **OCR Service**: Tesseract OCR via pytesseract with regex extraction for merchant, amount, date, time, currency.
- **Receipt Validation Service**: Image size/format checks, field validation, update validation.
- **Receipt Service Orchestrator**: Upload → validate → OCR → categorize → create expense → publish event (receipt.processed, receipt.confirmed).
- **Receipt Domain Model**: 16 fields, 6 statuses (uploaded, processing, processed, confirmed, failed, expired).
- **8 Receipt Endpoints**: `POST /receipts/upload`, `/receipts/{id}/process`, `/receipts/{id}/confirm`, `GET /receipts`, `GET /receipts/{id}`, `PATCH /receipts/{id}`, `DELETE /receipts/{id}`, `GET /receipts/{id}/image`.
- **4 Frontend Pages**: ReceiptsOverviewPage (grid with status badges), ReceiptUploadPage (drag-drop + camera), ReceiptReviewPage (editable fields + confirm), ReceiptHistoryPage (table with delete).
- **ReceiptsLayout**: 4-item sidebar nav (Overview, Upload, Review, History).
- **MongoDB Indexes**: receipts (3), receipt_processing_logs (2).

## [1.12.0] - 2026-07-06

### Added
- **AI Financial Goal Planning Engine**: 10 financial goal types (savings, emergency_fund, debt_repayment, investment, retirement, education, home_purchase, travel, wedding, custom).
- **5 Domain Models**: FinancialGoal, GoalProgress (4 milestones), GoalRecommendation, GoalPrediction (60-month), GoalNotification.
- **5 Repositories**: Full CRUD with ownership verification.
- **7 Services**: GoalFeasibilityService (4-factor scoring), SavingsPlanService (overspend detection), GoalPredictionService (probability of success), GoalProgressService (milestone tracking), GoalRecommendationService (3 rec types), GoalNotificationService (completion/milestone/at-risk), GoalPlanningService (orchestrator with event publishing).
- **9 Goal Endpoints**: `POST /goals`, `PUT /goals/{id}`, `DELETE /goals/{id}`, `GET /goals`, `GET /goals/{id}`, `POST /goals/analyze`, `POST /goals/recalculate`, `GET /goals/recommendations`, `GET /goals/progress`.
- **6 Frontend Pages**: GoalsOverviewPage, CreateGoalPage, GoalDetailPage, GoalRecommendationsPage, GoalProgressPage, GoalHistoryPage.
- **GoalsLayout**: 5-item sidebar nav.
- **Events**: goal.created, goal.updated, goal.deleted, goal.completed, goal.milestone_reached, goal.at_risk, goal.progress_updated.

## [1.11.0] - 2026-07-06

### Added
- **LangChain AI Copilot**: Natural language queries over financial data with 11 custom LangChain tools.
- **5 Models**: ChatSession, ChatMessage, ConversationMemory, ConversationSummary, AiFeedback.
- **5 Services**: LLMService (with TokenCounter via tiktoken), RAGService (FAISS vector store), MemoryService (auto-summarization at 10 messages), ToolRegistry (11 tools), CopilotService (orchestrator with injection detection, PII masking, context building).
- **Prompt System**: SYSTEM_PROMPT + FINANCIAL_CONTEXT_PROMPT with injection guard pattern.
- **7 Copilot Endpoints**: `POST /copilot/chat` (core chat), `GET /copilot/sessions`, `GET /copilot/sessions/{id}`, `DELETE /copilot/sessions`, `POST /copilot/feedback`, `GET /copilot/suggestions`, `GET /copilot/settings`.
- **4 Frontend Pages**: CopilotChatPage (chat interface), CopilotHistoryPage (session list), CopilotHistoryDetailPage (session detail), CopilotSettingsPage (model/temperature config).
- **CopilotLayout**: 3-item nav (Chat, History, Settings).
- **Config**: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE.

## [1.10.0] - 2026-07-06

### Added
- **Budget Intelligence V2**: ML-based budget recommendations, category trend analysis, forecasting, risk assessment, savings opportunities.
- **5 Models**: BudgetIntelligence, BudgetRecommendation, BudgetPrediction, BudgetRisk, SavingsOpportunity.
- **8 Services**: SmartBudgetService, CategoryTrendService, BudgetForecastService, BudgetRiskService, BudgetRecommendationService (3 rec types), BudgetOptimizationService, SavingsOpportunityService (6 types), BudgetIntelligenceService (orchestrator).
- **8 Budget Intelligence Endpoints**: `POST /budget-intelligence/generate`, `/recalculate`, `GET /budget-intelligence/current`, `/recommendations`, `/optimization`, `/trends`, `/risk`, `/opportunities`.
- **5 Frontend Pages**: BIOOverviewPage, BIRecommendationsPage, BIOptimizationPage, BITrendsPage, BIOpportunitiesPage.
- **BudgetIntelligenceLayout**: 5-item sidebar nav.
- **9/9 Integration Tests**: All passing.

## [1.9.0] - 2026-07-06

### Added
- **Financial Health Engine V2**: Enhanced scoring with 10-factor weighted formula, 5 risk levels.
- **4 Models**: FinancialHealth, HealthHistory, RiskProfile, HealthRecommendation.
- **7 Services**: HealthScoreCalculator (10 factors), RiskAssessmentService (category risk, volatility, emergency fund), HealthHistoryService, TrendAnalysisService (direction + momentum), RecommendationEngine (5 types), HealthAggregationService, FinancialHealthService (orchestrator).
- **8 Health Endpoints**: `POST /health/calculate`, `/recalculate`, `GET /health/current`, `/history`, `/trends`, `/breakdown`, `/recommendations`, `/risk`.
- **5 Frontend Pages**: HealthOverviewPage, HealthHistoryPage, HealthTrendsPage, HealthRecommendationsPage, HealthRiskPage.
- **HealthLayout**: 5-item sidebar nav.

## [1.8.0] - 2026-07-06

### Added
- **Dashboard V2 + Real-Time WebSockets**: Pre-computed dashboard data with event-driven updates.
- **DashboardService**: 22 pre-computed metrics — overview, analytics, activity feed (7 types), AI insights (6 types).
- **NotificationService**: Read/unread tracking, mark-all-read, filtered queries.
- **WidgetService**: 4 widget types (Spending, Budget, Health, Recurring) with get_all/get_single.
- **DashboardGateway**: WebSocket handler subscribed to 7 event types (dashboard.* events).
- **11 Dashboard Endpoints**: `GET /dashboard/summary`, `/spending`, `/cashflow`, `/monthly`, `/overview`, `/analytics`, `/budgets`, `/insights`, `/notifications`, `/notifications/unread-count`, `/activity`, `/widgets`, `POST /notifications/{id}/read`, `/notifications/read-all`.
- **7 Frontend Pages**: OverviewPage, AnalyticsPage, SpendingPage, CashflowPage, BudgetsPage, InsightsPage, NotificationsPage.
- **4 Chart Components**: SpendingChart, CategoryPieChart, CashflowChart, TrendsChart.
- **4 Widget Components**: SpendingWidget, BudgetWidget, HealthWidget, RecurringWidget.
- **DashboardLayout**: 7-item sidebar nav.
- **API Client**: 12 methods in dashboard.js.
- **Dashboard Store**: Observer-pattern store with event mapping.

## [1.7.0] - 2026-07-05

### Added
- **Financial Processing Engine**: 9-stage pipeline implementation.
- **6 Domain Models**: BudgetUsage, CashFlowSummary, DashboardMetrics, FinancialMetrics, MonthlySummary, ProcessingBatch (with typed ProcessingError).
- **6 Repositories**: All with unique-key upserts — MongoBudgetUsageRepository, MongoCashFlowRepository, MongoDashboardMetricsRepository, MongoFinancialMetricsRepository, MongoMonthlySummaryRepository, MongoProcessingBatchRepository.
- **10 Services**: ExpenseGenerationService (idempotent expense creation), BudgetProcessingService (per-category usage tracking), CashFlowService (income/expense by category), SavingsService (rate + trend), FinancialMetricsService (weighted health score), DashboardAggregationService (6 pre-computed metric groups), BudgetAlertService (threshold-based deduped alerts), DashboardReadService (get_summary, get_cashflow, get_monthly_trends), FinancialProcessingService (orchestrator), Factory.
- **Atomic Claim-Based Dedup**: `findOneAndUpdate` with `{processed_at: null}` eliminates TOCTOU race condition.
- **Period-Scoped Aggregations**: Cash flow, savings, dashboard metrics use ALL transactions for the period.
- **5 Processing Endpoints**: `POST /processing/process`, `/process-all`, `/reprocess`, `GET /processing/status`, `/history`.
- **4 Dashboard V1 Endpoints**: `GET /dashboard/summary`, `/spending`, `/cashflow`, `/monthly`.
- **6 Output Collections**: `budget_usage` (unique on user_id+budget_id+month+year), `dashboard_metrics` (unique on user_id+period), `financial_metrics` (unique on user_id+period), `cash_flow_summary` (unique on user_id+year+month), `processing_batches`, `monthly_summary`.
- **7 Event Types**: processing.batch.started, processing.batch.completed, processing.expense.created, processing.budget.updated, processing.cashflow.updated, processing.financial_metrics.updated, processing.dashboard.updated.
- **Config-Driven Settings**: max_batch_size=500, confidence_threshold=0.7, alert_cooldown_hours=1.

## [1.6.0] - 2026-07-05

### Added
- **AI Transaction Intelligence Engine**: 9-stage processing pipeline implementation (not just design).
- **Merchant Normalization System**: 31 merchants with 3-tier alias matching + 300s TTL cache.
- **Category Prediction Service**: Reuses ExpenseCategorizer (TF-IDF + Logistic Regression).
- **Confidence Scoring**: 5-factor weighted formula with review thresholds.
- **Recurring Detection**: 8 subscriptions ±5% tolerance, utilities, rent.
- **Income Detection**: DEBIT/CREDIT analysis with reversal/refund/transfer classification.
- **Feedback Learning**: category_feedback collection.
- **8 Intelligence Endpoints**: process, process-all, reprocess, status, history, review, review/{id}, feedback/{id}.
- **3 Financial Transaction Endpoints**: list, get, update.
- **5 New Collections**: financial_transactions, merchant_dictionary, merchant_aliases, category_feedback, transaction_tags.

## [1.5.0] - 2026-07-05

### Added
- **AI Transaction Intelligence Engine**: 9-stage processing pipeline transforming raw `bank_transactions` into enriched `financial_transactions`.
- **Merchant Normalization System**: 5-step description cleaning (strip, remove payment suffixes, extract UPI/card location, lowercase) + 3-tier alias matching (exact 1.0, contains 0.85, regex 0.85) + 300s TTL cache. 31 seeded merchants (Swiggy, Zomato, Uber, Netflix, Amazon, Flipkart, etc.).
- **Category Prediction Service**: Reuses existing `ExpenseCategorizer` (TF-IDF + Logistic Regression). Merchant category (≥0.85 confidence) overrides ML. Keyword fallback via shared `CATEGORY_KEYWORD_MAP` in constants.
- **Confidence Scoring**: 5-factor weighted formula (merchant 0.40, ML 0.35, recurring 0.10, keyword 0.10, amount_normalcy 0.05). Thresholds: ≥0.95 auto_approved, ≥0.70 approved, <0.70 review_required.
- **Recurring Detection Service**: 8 known subscriptions ±5% amount tolerance, 6 utility keywords, 2 rent keywords. Tags: `#subscription`, `#utility`, `#rent`.
- **Income Detection Service**: DEBIT → never income. CREDIT → reversal (skip), refund (#refund), transfer (#transfer), or income (#salary).
- **Feedback Learning Service**: Records user corrections to `category_feedback` collection. Publishes `ai.feedback.recorded` event.
- **Manual Review Queue**: `GET /intelligence/review` for low-confidence items, `PATCH /intelligence/review/{id}` for atomic status update via `find_one_and_update` (TOCTOU-safe).
- **8 Intelligence Endpoints**: `POST /intelligence/process`, `/process-all`, `/reprocess`, `GET /intelligence/status`, `/history`, `/review`, `PATCH /intelligence/review/{id}`, `POST /intelligence/feedback/{id}`.
- **3 Financial Transaction Endpoints**: `GET /financial-transactions` (paginated, category filter), `GET /financial-transactions/{id}`, `PUT /financial-transactions/{id}` (auto-feedback on category change).
- **Domain Model**: `FinancialTransaction` (24 fields, from_mongo/to_mongo, ReviewStatus Literal).
- **Domain Repository**: `FinancialTransactionRepository` (11 abstract methods) + `MongoFinancialTransactionRepository` (bulk_create with BulkWriteError dedup, find_unprocessed_bank_tx_ids, atomic_review_update, update_fields).
- **Merchant Repositories**: `MongoMerchantRepository` (find_by_name, find_all_active, find_aliases_by_type), `MongoFeedbackRepository` (create_category_feedback, count_by_user).
- **5 New DB Collections**: `financial_transactions` (7 indexes, unique on bank_transaction_id), `merchant_dictionary`, `merchant_aliases`, `category_feedback`, `transaction_tags`.
- **3 New Exceptions**: `FinancialTransactionNotFoundException` (404), `DuplicateProcessException` (409), `InvalidReviewStateException` (400).
- **5 New TypedDicts**: `FinancialTransactionDocument`, `MerchantDictionaryDocument`, `MerchantAliasDocument`, `CategoryFeedbackDocument`, `TransactionTagDocument`.
- **Event Publishing**: `ai.pipeline.completed`, `ai.feedback.recorded`, `ai.review.submitted` — all with UUID `event_id` for dedup/tracing.
- **Concurrent Processing**: `asyncio.gather` with semaphore(10) in `process_batch` for parallel pipeline execution.
- **Service Factory**: `app/services/intelligence_service.py` — singleton-per-app wiring all 7 AI services + pipeline + 3 repos + event bus.
- **Structured Logging**: Added logging to `CategoryPredictionService`, `ConfidenceService`, `IncomeDetectionService`, `RecurringDetectionService`.
- **Pydantic Schemas**: `FinancialTransactionResponse` (20 fields with `from_domain` classmethod), `FinancialTransactionUpdateRequest`, `ProcessPendingRequest`, `ProcessResultResponse`, `ReviewQueueResponse`, `ReviewSubmissionRequest`, `FeedbackSubmissionRequest`, `FeedbackResponse`, `IntelligenceStatusResponse`.
- **Constants Extended**: `CONFIDENCE_THRESHOLDS`, `CATEGORY_KEYWORD_MAP` (shared, replaces duplicate maps), `TRANSACTION_TAGS`, `MERCHANT_CONFIDENCE_WEIGHTS`.
- **Backend Files**: 20+ new — `app/ai/` (7 services + pipeline + models), `app/domain/financial_transactions/` (2 files), `app/schemas/ai.py` + `financial_transactions.py`, `app/api/routes/intelligence.py` + `financial_transactions.py`, `app/services/intelligence_service.py`, `app/infrastructure/bank_integration/merchant/` (3 files), `app/infrastructure/database/repositories/intelligence/` (3 files).

### Fixed
- **Merchant cache bug** (`merchant_normalizer.py:36`): `timedelta.seconds` → `.total_seconds()` — cache appeared perpetually fresh after 24h.
- **Route bypasses repository** (`financial_transactions.py:132`): replaced `__import__("bson")` + private `_db` access with `service.update_transaction()` + `repo.update_fields()`.
- **Route accesses private service** (`intelligence.py:149`): replaced `service._feedback_service` with public `service.record_feedback()` method.
- **TOCTOU race condition** (`financial_transaction_service.py:150`): `submit_review` now uses atomic `find_one_and_update` with `{review_status: "review_required"}` filter — replaces check-then-update pattern.
- **Income service unused keywords** (`income_service.py:2-5`): removed dead `INCOME_KEYWORDS` list. Added `REVERSAL_KEYWORDS` to prevent misclassifying reversed/failed CREDIT transactions as income.
- **Service cache fragility** (`intelligence_service.py:33`): replaced `id(db)` (memory address, reusable after GC) with single-instance `_service_instance` pattern.
- **Duplicated keyword maps** (`category_service.py` + `ml_service.py`): extracted to shared `CATEGORY_KEYWORD_MAP` in `app/core/constants.py`.
- **Events without IDs** (`events.py:12`): `Event` now auto-generates `uuid4().hex` as `event_id`.
- **Boilerplate FinancialTransactionResponse**: 7 redundant constructions replaced with `FinancialTransactionResponse.from_domain()` classmethod.
- **Missing response fields**: Added `bank_transaction_id`, `reviewed_by`, `review_note` to `FinancialTransactionResponse`.

## [1.4.0] - 2026-07-05

### Added
- **Financial Data Synchronization Engine**: Full sync lifecycle orchestrator — consent validation, import preference resolution, provider adapter invocation, deduplication, progress tracking.
- **5 Sync Endpoints**: `POST /sync/start` (per-account), `POST /sync/manual` (all active accounts), `GET /sync/status` (per-account or all), `GET /sync/history` (paginated with filter), `POST /sync/retry` (retry failed with limit) — all JWT-protected with ownership verification.
- **Domain Models**: `domain/sync/` with `BankTransaction` (12 fields, from_mongo/to_mongo) and `SyncLog` (15 fields, state machine methods: mark_running, mark_completed, mark_failed, can_retry).
- **Abstract Repositories**: `BankTransactionRepository` (6 methods) and `SyncLogRepository` (9 methods including count_by_account/count_by_user for pagination).
- **Mongo Repositories**: `MongoBankTransactionRepository` with dedup via compound unique index + `BulkWriteError` handling, `MongoSyncLogRepository` with full CRUD + status updates.
- **Sync Service**: `SyncService.start_sync`, `manual_sync_all`, `get_status`, `get_history`, `retry_sync`, and `_execute_sync` background execution with consent check, provider timeout (120s), decryption via FieldEncryptor, bulk insert with dedup, last_synced_at update.
- **3 New Exceptions**: `ConsentNotGrantedException` (403), `SyncInProgressException` (409), `SyncRetryLimitExceededException` (400).
- **Bank Account Repository Extension**: `update_last_synced(account_id, synced_at)` — updates `last_synced_at` and `updated_at` on bank_accounts.
- **Bank Transaction Storage**: `bank_transactions` collection with compound unique index on `(provider_account_id, transaction_id)` for dedup, and `(user_id, bank_account_id, transaction_date)` for queries.
- **Sync Logs**: `sync_logs` collection with indexes on `(user_id, bank_account_id, created_at)` and `(user_id, status)`.
- **Backend Files**: 4 new — `domain/sync/` (3 files), `schemas/sync.py`, `infrastructure/database/repositories/sync_repository.py`, `services/sync_service.py`, `api/routes/sync.py`. 5 modified — `domain/bank_accounts/repository.py`, `infrastructure/database/repositories/bank_repository.py`, `models/documents.py`, `core/exceptions.py`, `api/v1/router.py`, `db/mongodb.py`.
- **Frontend Files**: 4 new — `api/sync.js`, `pages/Sync.jsx` (status per account with polling), `pages/SyncHistory.jsx` (paginated + retry), `pages/SyncStatus.jsx` (detailed per-account). 2 modified — `App.jsx` (3 routes under `/app/`), `AppLayout.jsx` ("Data Sync" nav link).
- **Logging**: Structured logging across sync lifecycle (info on start/complete, warning on consent expiry/provider errors, error on failures).
- **Concurrency Protection**: Re-checks for running syncs inside `_execute_sync` before marking as running.

### Fixed
- Retry limit bypass — new SyncLog now propagates `existing.retry_count + 1` to enforce `max_retries` cap.
- `from_date` zero-width range for "import all" — default to `utc_now() - 730 days` when `from_date is None`.
- History pagination total — added `count_by_account`/`count_by_user` with MongoDB `count_documents` for accurate page count.
- `sync_status` type mismatch — added `"pending"` to `Literal` to prevent Pydantic validation errors.
- Race condition — re-check for concurrent running syncs at start of `_execute_sync` execution.

### Changed
- `BankAccountRepository`: added `update_last_synced` abstract method.
- `MongoBankAccountRepository`: implemented `update_last_synced` with `$set: { last_synced_at, updated_at }`.
- `SyncService._execute_sync`: uses `asyncio.wait_for` with 120s timeout for provider calls.

---

## [1.3.0] - 2026-07-05

### Added
- **User-Facing Consent Grant**: Separate `consents` collection for user-facing transaction import consent (distinct from AA-level consent). 3 JWT-protected endpoints: `POST /consent/grant`, `POST /consent/revoke`, `GET /consent/status`.
- **Import Preference**: New `import_preferences` collection. Users choose import scope per account: `import_all`, `start_fresh`, `from_date`. 2 JWT-protected endpoints: `POST /import-preference/`, `GET /import-preference/`.
- **UI Flow**: 3 new pages — ImportPreference (3 option cards + date picker), ReviewPage (summary + confirm), CompletePage (success). CTA button on ConnectSuccess.
- **Domain Models**: `domain/consents/` (ConsentGrant model + ConsentRepository abstract), `domain/import_preferences/` (ImportPreference model + ImportPreferenceRepository abstract).
- **Mongo Repositories**: `consent_repository.py` (6 methods), `import_preference_repository.py` (atomic upsert via `update_one` with `upsert=True`).
- **Services**: `consent_grant_service.py` (grant with idempotency, revoke with state check, status), `import_preference_service.py` (save with ownership check, get).
- **Schemas**: `schemas/consent.py` (5 Pydantic schemas with `consent_duration_days` validator bounded 1–3650), `schemas/import_preference.py` (2 schemas with date validators).
- **Backend Files**: 13 new — exceptions (+4), TypedDicts (+2), domain models + repos (6 files), schemas (2), Mongo repos (2), services (2), routes (2).
- **Frontend Files**: 7 new — API modules (2), components (4), pages (3). Extended: ConnectSuccess (CTA), App.jsx (3 routes).
- **Design Document**: `docs/consent-import-design.md` — 13 sections (architecture, API, DB schemas, UI flow, sequence diagram, validation rules, security, sync engine integration).
- **UI Polish**: `prefers-reduced-motion` support in FadeIn, spring physics on accordion, staggered mobile menu, larger hero blur orbs, contained TrustedBy icons, card hover lift on Features/Testimonials/Benefits, 6 avatar gradients, newsletter input in Footer.

### Security
- **Disconnect revokes application consent**: `ConsentManager.revoke_consent` now also marks active user-facing consents as revoked in the `consents` collection.
- **CSRF state validation**: ConsentPage reads `state` query param and validates against `user._id`.
- **Bank-level consent check**: Application consent grant verifies `bank_account.consent_status == "active"` before proceeding.
- **Ownership on import preference save**: `ImportPreferenceService.save` validates bank account exists and belongs to user.
- **Absolute redirect URL**: Uses `settings.bank_consent_redirect_base` (configurable) instead of relative path.
- **ObjectId validation**: `to_object_id` raises `ValidationException` (422) for invalid IDs instead of crashing with 500.
- **Input bounds**: `consent_duration_days` maximum of 3650 (10 years). `import_start_date` validated for not-in-future.

### Fixed
- Dual consent systems desynchronized on disconnect — bank-level revoke now cascades to application-level consents.
- Import preference upsert race condition — replaced read-then-write with atomic `update_one(upsert=True)`.
- Consent grant missing bank-level status check — now verifies `consent_status == "active"`.
- Import preference save missing ownership verification — now validates bank account ownership.
- `consent_token` hardcoded to empty string on frontend — now reads from URL query params.
- ReviewPage no error isolation between consent grant and preference save — separate try/catch with step-specific messages.
- Catch-all route redirect — authenticated users now go to `/app`, unauthenticated to `/`.

### Changed
- `ConsentManager` constructor accepts optional `ConsentRepository` for cascading revoke.
- `BankService.initiate_connection` constructs absolute redirect URL from config.
- `ImportPreferenceRepository.upsert` uses atomic MongoDB upsert (no read-then-write).
- `ImportPreferenceService` constructor accepts optional `BankAccountRepository`.
- `FadeIn` component: `useReducedMotion` support, spring physics transition.
- Landing page components: improved glass opacity, card hover effects, varied avatar gradients.

---

## [1.2.0] - 2026-07-05

### Added
- **Bank Account Connection**: Read-only RBI Account Aggregator module with 5 JWT-protected endpoints
- **Provider Adapter Pattern**: Abstract `BankProviderAdapter` interface with `BankProviderRegistry` — extensible to Setu, Finvu, OneMoney, Perfios
- **Mock Bank Provider**: 3 synthetic Indian accounts (SBI, HDFC, ICICI) with 30 transactions, 5% random failure rate — fully offline
- **Consent Manager**: Full consent lifecycle (initiate, finalize, revoke, expiry detection)
- **Field-Level Encryption**: `provider_account_id` and `consent_token` encrypted via Fernet (AES-256-GCM) at rest
- **Backend Files**: 14 new + 5 modified — config, exceptions, encryption, schemas, domain model, repository, provider adapter, consent manager, bank service, bank routes
- **Frontend Files**: 8 new + 4 modified — API module, ConnectBank, ConsentPage, ConnectSuccess, ManageAccounts, BankCard, DisconnectDialog
- **Route Wiring**: 4 public `/connect-bank/*` routes under LandingLayout + 1 protected `/app/bank-accounts`
- **Navigation**: "Connect Bank" link in landing Navbar, "Bank Accounts" in dashboard sidebar
- **Landing Feature**: "Connect Your Bank" card in Features section + `Landmark` icon support
- **Design Document**: `docs/bank-connect-design.md` — 12 sections (architecture, API, security, compliance, wiring guide)

### Fixed
- `check_expired_consents` crashing on `"__all__"` ObjectId sentinel — added `get_all_active()` repo method
- `total_accounts` always equalling `active_accounts` in status endpoint — now counts all accounts vs filtered active
- Hardcoded default `bank_encryption_key` and `secret_key` in config — now required from env
- Dead try/except decrypt logic on plaintext `consent_handle` in `revoke_consent` — reads directly
- Public bank routes (no auth check) — added `useAuth()` guard + 401 handling on all 3 pages
- Client-side consent token generation — removed `auto-${consentHandle}` pattern
- Hardcoded 1-year consent expiry — now uses provider's actual `expires_at`
- Consent URL ignoring AA redirect — frontend now uses `window.location.href = res.data.consent_url`
- CSRF protection — state param (`user_id`) in consent redirect URL
- Duplicate `provider` and mismatched `consent_handle` in mock provider's `consent_url`
- Missing `provider` enum validation — added `ALLOWED_PROVIDERS` with Pydantic `@field_validator`

### Changed
- Frontend bank pages: auth-check redirect to `/login`, redirect to provider's `consent_url`
- `ConsentManager.finalize_consent` accepts `expires_at` parameter
- `BankService.get_status` counts all accounts (not just active) for `total_accounts`
- Config: `secret_key` and `bank_encryption_key` are now required env vars (no defaults)

---

## [1.1.0] - 2026-07-05

### Added
- **Landing Page**: 13-section premium SaaS landing page with Framer Motion animations
- **Public Routes**: Home (/), Features, About, Contact, Privacy Policy, Terms of Service
- **Route Migration**: Dashboard moved from / to /app/* — existing pages untouched
- **Design System**: Tailwind CSS 3 with custom emerald/blue theme, glassmorphism utilities
- **UI Primitives**: Button (5 variants, 4 sizes), Card (4 variants, hoverable), SectionHeading, GradientText, Badge
- **Animation System**: FadeIn (directional), StaggerList/StaggerItem, Counter (scroll-triggered)
- **Preview Mockups**: HealthScoreGauge (RadialBar), SpendingChart (Line), CopilotChatMock (animated), DashboardMockup (Bar)
- **Section Components**: HeroSection, TrustedBy, Features, HowItWorks, HealthScorePreview, SpendingPreview, CopilotPreview, DashboardPreview, Benefits, Testimonials, FAQ (with search), CTA
- **Sub-Pages**: FeaturesPage, AboutPage (team + values), ContactPage (form + contact info), PrivacyPage, TermsPage
- **Data Layer**: 6 static JS data files — navigation, features, testimonials, FAQ, howItWorks, stats
- **SEO**: OG tags, Twitter cards, meta description, Inter font preconnect, canonical URL
- **CSS Isolation**: Landing styles scoped under .landing-page — zero conflict with existing styles.css
- **Accessibility**: htmlFor/id on form labels, aria-expanded/aria-controls on accordion and mobile menu, role attributes

### Changed
- App.jsx route tree: landing routes at /, dashboard routes under /app
- Login.jsx redirect: / → /app
- Register.jsx redirect: / → /app
- AppLayout.jsx sidebar links: prefixed with /app
- main.jsx: imports landing/index.css
- index.html: SEO meta tags, OG tags, Inter font setup
- webpack.config.js: postcss-loader added to CSS rule chain

### Fixed
- Footer columns rendering empty (replaced dynamic navigation.find with hardcoded link groups)
- Global styles.css button styles bleeding into landing (.landing-page button reset)
- Contact form label/input association (added htmlFor + id)
- FAQ accordion missing ARIA attributes (aria-expanded, aria-controls, role="region")
- Mobile hamburger menu missing ARIA attributes
- Dead code removed: RevealSection, Container/Grid/Section layout components, unused exports (trustLogos, ctaButtons, initials, gradient)

---

## [1.0.0] - 2026-06-01

### Added
- **Authentication**: Email/password registration, JWT login, protected routes
- **Expense Tracking**: Full CRUD with category/payment method/date/amount filters
- **ML Categorization**: TF-IDF + Logistic Regression expense categorization with keyword fallback
- **Budget Management**: Monthly budget CRUD with usage tracking (safe/warning/over states)
- **Budget Alerts**: Automatic alerts at 75%, 90%, and 100% budget thresholds
- **Budget Suggestions**: ML-based smart budget optimization with confidence scoring
- **Budget Optimizer**: Interactive budget optimization with apply/dismiss workflow
- **Dashboard**: Monthly summary, 6-month trends, category breakdown, health score, recommendations
- **Financial Health Score**: Weighted scoring (savings 35%, budget adherence 30%, stability 20%, risk 15%)
- **Recommendation Engine**: Rule-based personalized financial recommendations
- **Spending Anomaly Detection**: ML-powered anomaly detection with severity levels
- **Weekly Spending Reports**: Automated weekly anomaly summaries with week-over-week comparison
- **Recurring Expenses**: CRUD + auto-detection from expense history + upcoming predictions
- **Subscription Tracker**: CRUD + auto-detection + payment recording + monthly/yearly cost insights
- **Financial Reports**: Weekly and monthly auto-generated reports with insights and recommendations
- **WebSocket**: Real-time connection management with token auth and auto-reconnect
- **Event Bus**: In-memory event-driven architecture infrastructure
- **Repository Pattern**: Abstract repository interfaces with MongoDB implementations
- **Redis Cache**: Optional Redis caching layer for performance
- **Middleware Stack**: Request ID tracking, request logging, global error handling, CORS
- **Docker Support**: Docker Compose with MongoDB, Redis, Backend, Frontend, Nginx
- **CI/CD**: GitHub Actions for testing and ML model training
- **Testing**: Comprehensive integration tests with fake MongoDB collections

### Changed
- Refactored backend into layered architecture: api/core/db/domain/infrastructure/services/utils
- Migrated all endpoints to Pydantic v2 schemas
- Implemented custom exception hierarchy (AppException, NotFoundException, AuthException, etc.)
- Added structured logging with request ID correlation
- Standardized API responses with error.code, error.message, error.request_id format
- Replaced direct MongoDB calls with repository pattern (partial migration)

### Fixed
- JWT token validation in WebSocket connections
- MongoDB unique index conflicts on duplicate budgets
- Expense category fallback when ML model not loaded

### Technical Debt (Acknowledged)
- Mixed DB access patterns (some services use repos, some query directly)
- Unused repository interfaces (abstract + Mongo impl exist but not wired)
- Unused event bus (infrastructure exists but no subscribers/publishers)
- Duplicate auth state management (authStore.js + AuthContext.jsx)
- No background task processing (sync operations in request cycle)
- No TypeScript on frontend
- No rate limiting on auth endpoints

---

## Future Releases

### [1.15.0] - Planned
- Migrate Webpack to Vite — faster dev builds, better DX
- Add TypeScript support — type safety across frontend
- Consolidate state management (authStore + AuthContext -> single pattern)
- Consolidate frontend stores to Zustand
- Fix code smells (mixed DB access, unused repos, hardcoded paths)
- Rate limiting middleware for auth endpoints
- Pagination on all list endpoints
- Background tasks (Celery/ARQ for async processing)
- Real AA provider adapters (Setu, Finvu, OneMoney, Perfios)
- Mobile OTP authentication

### [2.0.0] - Planned
- Expense forecasting (Prophet/ARIMA time series)
- Income forecasting — predict future income patterns
- Cash flow forecasting — project future account balances
- What-if analysis — scenario modeling for financial decisions
- Advanced analytics — deeper spending insights and patterns
- Natural language report generation
- Investment portfolio tracking
- Tax optimization suggestions
- Production deployment
- Security audit
