# IntelliMoney — Project State

## Current Version: 1.14.0

## Completed Phases

### Phase 14: One-Click Startup Scripts (V1.14 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| `scripts/start-IntelliMoney.bat` — 7-step automated startup (env validation, Docker, backend venv+install+uvicorn, frontend npm+dev, health checks, browser open, colored summary) | High | ✅ Done |
| `scripts/stop-IntelliMoney.bat` — graceful stop of backend, frontend, Docker, port cleanup | High | ✅ Done |
| Structured logging to `logs/startup.log` | Medium | ✅ Done |

### Phase 13: Receipt OCR & Manual Expense Import (V1.13 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| Receipt domain model (16 fields, 6 statuses: uploaded/processing/processed/confirmed/failed/expired) | High | ✅ Done |
| Image preprocessing service (OpenCV: deskew, denoise, adaptive threshold, contrast enhancement) | High | ✅ Done |
| OCR service (Tesseract via pytesseract, regex extraction for merchant/amount/date/time/currency) | High | ✅ Done |
| Receipt validation service (image size/format checks, field validation, update validation) | Medium | ✅ Done |
| Receipt service orchestrator (upload→validate→OCR→categorize→createExpense→publishEvent) | High | ✅ Done |
| 8 backend routes (POST upload, POST process, POST confirm, GET list, GET detail, PATCH update, DELETE, GET image) | High | ✅ Done |
| File storage via configurable `UPLOAD_DIR`, MIME type detection | Medium | ✅ Done |
| Config: UPLOAD_DIR, MAX_UPLOAD_SIZE (10MB), ALLOWED_MIME_TYPES | Medium | ✅ Done |
| Frontend: ReceiptsOverviewPage (grid with status badges), ReceiptUploadPage (drag-drop + camera capture) | High | ✅ Done |
| Frontend: ReceiptReviewPage (editable fields + confirm action), ReceiptHistoryPage (table with delete) | High | ✅ Done |
| ReceiptsLayout with 4-item sidebar nav | High | ✅ Done |

### Phase 12: AI Financial Goal Planning Engine (V1.12 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 5 domain models: FinancialGoal (10 types), GoalProgress (4 milestones), GoalRecommendation, GoalPrediction (60-month), GoalNotification | High | ✅ Done |
| 5 repositories with full CRUD | High | ✅ Done |
| GoalFeasibilityService (4-factor feasibility scoring) | High | ✅ Done |
| SavingsPlanService (discretionary overspend detection, savings rate optimization) | High | ✅ Done |
| GoalPredictionService (60-month projection with probability of success) | High | ✅ Done |
| GoalProgressService (milestone tracking, missed detection, status transitions) | High | ✅ Done |
| GoalRecommendationService (3 recommendation types with confidence/impact/steps) | Medium | ✅ Done |
| GoalNotificationService (completion/milestone/at-risk/alerts) | Medium | ✅ Done |
| GoalPlanningService orchestrator (full pipeline + event publishing) | High | ✅ Done |
| 9 backend routes (CRUD + analyze, recalculate, recommendations, progress) | High | ✅ Done |
| 6 frontend pages (Overview, Create, Detail, Recommendations, Progress, History) | High | ✅ Done |
| GoalsLayout with 5-item sidebar nav | High | ✅ Done |
| MongoDB indexes for 6 collections | High | ✅ Done |

### Phase 11: LangChain AI Copilot (V1.11 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 5 domain models: ChatSession, ChatMessage, ConversationMemory, ConversationSummary, AiFeedback | High | ✅ Done |
| 5 repositories (Mongo implementations) | High | ✅ Done |
| SYSTEM_PROMPT + FINANCIAL_CONTEXT_PROMPT with injection guard | High | ✅ Done |
| LLMService with TokenCounter (tiktoken), configurable model/temperature/max_tokens | High | ✅ Done |
| RAGService with FAISS vector store for financial context retrieval | High | ✅ Done |
| MemoryService with auto-summarization (triggers at 10 messages) | High | ✅ Done |
| ToolRegistry with 11 tools wrapping existing collections (spending, budget, health, goals, etc.) | High | ✅ Done |
| CopilotService orchestrator with injection detection, PII masking, context building, tool execution | High | ✅ Done |
| 7 backend routes (POST /copilot/chat, GET sessions, GET sessions/{id}, DELETE sessions, POST feedback, GET suggestions, GET settings) | High | ✅ Done |
| 4 frontend pages (CopilotChatPage, CopilotHistoryPage, CopilotHistoryDetailPage, CopilotSettingsPage) | High | ✅ Done |
| CopilotLayout with 3-item nav (Chat, History, Settings) | High | ✅ Done |
| Config: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS | High | ✅ Done |

### Phase 10: Budget Intelligence V2 (V1.10 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 5 domain models: BudgetIntelligence, BudgetRecommendation, BudgetPrediction, BudgetRisk, SavingsOpportunity | High | ✅ Done |
| 5 repositories with unique-key upserts | High | ✅ Done |
| SmartBudgetService (ML-based budget allocation, category-level optimization) | High | ✅ Done |
| CategoryTrendService (spending pattern analysis, trend direction) | High | ✅ Done |
| BudgetForecastService (prediction models for future spending) | High | ✅ Done |
| BudgetRiskService (overspending detection, volatility scoring, trend direction) | High | ✅ Done |
| BudgetRecommendationService (3 types: adjustment/reallocation/reduction, confidence scoring) | High | ✅ Done |
| BudgetOptimizationService (global budget allocation optimization) | Medium | ✅ Done |
| SavingsOpportunityService (6 opportunity types: subscription/utility/dining/groceries/transport/entertainment) | Medium | ✅ Done |
| BudgetIntelligenceService orchestrator (generate/recalculate pipeline) | High | ✅ Done |
| 8 backend routes (generate, recalculate, current, recommendations, optimization, trends, risk, opportunities) | High | ✅ Done |
| 5 frontend pages (Overview, Recommendations, Optimization, Trends, Opportunities) | High | ✅ Done |
| BudgetIntelligenceLayout with 5-item sidebar nav | High | ✅ Done |
| 9/9 integration tests passing | High | ✅ Done |

### Phase 9: Financial Health Engine V2 (V1.9 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 4 domain models: FinancialHealth, HealthHistory, RiskProfile, HealthRecommendation | High | ✅ Done |
| 4 repositories with unique-key upserts | High | ✅ Done |
| HealthScoreCalculator (10-factor weighted formula, 5 risk levels) | High | ✅ Done |
| RiskAssessmentService (category risk scoring, volatility analysis, emergency fund detection) | High | ✅ Done |
| HealthHistoryService (period-over-period tracking) | High | ✅ Done |
| TrendAnalysisService (direction detection, momentum scoring) | High | ✅ Done |
| RecommendationEngine (5 types: savings/risk/investment/emergency/debt) | High | ✅ Done |
| HealthAggregationService (comprehensive health aggregation) | Medium | ✅ Done |
| FinancialHealthService orchestrator with full pipeline | High | ✅ Done |
| 8 backend routes (calculate, recalculate, current, history, trends, breakdown, recommendations, risk) | High | ✅ Done |
| 5 frontend pages (Overview, History, Trends, Recommendations, Risk) | High | ✅ Done |
| HealthLayout with 5-item sidebar nav | High | ✅ Done |

### Phase 8: Dashboard V2 + Real-Time WebSockets (V1.8 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| DashboardService with 22 pre-computed metrics (overview, analytics, activity feed, AI insights) | High | ✅ Done |
| NotificationService with read/unread tracking, mark-all-read | High | ✅ Done |
| WidgetService with 4 widget types (Spending, Budget, Health, Recurring) + get_all_widgets | High | ✅ Done |
| DashboardGateway (WebSocket handler for dashboard events) | High | ✅ Done |
| 8 pre-computed endpoints (summary, spending, cashflow, monthly, overview, analytics, budgets, insights) | High | ✅ Done |
| 4 notification endpoints + activity feed + widgets endpoint | Medium | ✅ Done |
| 7 frontend pages under DashboardLayout (Overview, Analytics, Spending, Cashflow, Budgets, Insights, Notifications) | High | ✅ Done |
| DashboardLayout with 7-item sidebar nav | High | ✅ Done |
| 4 chart components (SpendingChart, CategoryPieChart, CashflowChart, TrendsChart) | High | ✅ Done |
| 4 widget components (SpendingWidget, BudgetWidget, HealthWidget, RecurringWidget) | Medium | ✅ Done |
| NotificationCenter component with real-time updates | Medium | ✅ Done |
| DashboardSkeleton loading state | Medium | ✅ Done |
| Observer store (dashboardStore) with event mapping | Medium | ✅ Done |
| API client with 12 methods | High | ✅ Done |
| Responsive CSS with mobile-first approach | Medium | ✅ Done |

### Phase 7: Financial Processing Engine (V1.7 — ✅ Completed)

See `docs/FINANCIAL_PROCESSING_ENGINE.md` for full architecture.

| Task | Priority | Status |
|------|----------|--------|
| 6 domain models: BudgetUsage, CashFlowSummary, DashboardMetrics, FinancialMetrics, MonthlySummary, ProcessingBatch | High | ✅ Done |
| 6 repositories with unique-key upserts | High | ✅ Done |
| 10 services (ExpenseGeneration, BudgetProcessing, CashFlow, Savings, FinancialMetrics, DashboardAggregation, BudgetAlert, DashboardRead, FinancialProcessing, Factory) | High | ✅ Done |
| 9-stage pipeline with atomic claim-based dedup | High | ✅ Done |
| 5 processing endpoints (POST process, process-all, reprocess, GET status, history) | High | ✅ Done |
| 4 dashboard V1 endpoints (GET summary, spending, cashflow, monthly) | Medium | ✅ Done |
| 7 domain event types published | Medium | ✅ Done |
| Config-driven settings (ProcessingSettings) | Medium | ✅ Done |
| Structured logging across all services | Medium | ✅ Done |

### Phase 6: AI Transaction Intelligence Engine (V1.6 — ✅ Completed)

See `docs/AI_TRANSACTION_ENGINE.md` for full architecture.

| Task | Priority | Status |
|------|----------|--------|
| 9-stage processing pipeline | High | ✅ Done |
| 7 AI services (Validation, Merchant, Category, Confidence, Recurring, Income, Feedback) | High | ✅ Done |
| 31 merchants with 3-tier alias matching + 300s TTL cache | High | ✅ Done |
| 5-factor confidence scoring (merchant 0.40, ML 0.35, recurring 0.10, keyword 0.10, amount 0.05) | High | ✅ Done |
| 3 review statuses (auto_approved ≥0.95, approved ≥0.70, review_required <0.70) | High | ✅ Done |
| Manual review queue with atomic status update | High | ✅ Done |
| Feedback learning (category_feedback collection) | Medium | ✅ Done |
| 8 intelligence endpoints, 3 financial transaction endpoints | High | ✅ Done |
| 5 new DB collections with indexes | High | ✅ Done |
| Concurrent batch processing (asyncio.gather, semaphore 10) | Medium | ✅ Done |

### Phase 5: Financial Data Synchronization Engine (V1.5 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 5 sync endpoints (start, manual, status, history, retry) | High | ✅ Done |
| Sync orchestration with consent validation + import preference resolution | High | ✅ Done |
| Dedup via compound unique index + BulkWriteError handling | High | ✅ Done |
| Sync audit log with state machine (pending→running→completed/failed) | High | ✅ Done |
| Retry logic (max 3), concurrency protection (409 on running) | High | ✅ Done |
| Provider timeout handling (120s via asyncio.wait_for) | Medium | ✅ Done |
| 3 frontend pages (Sync, SyncHistory, SyncStatus) | High | ✅ Done |

### Phase 4: Consent & Import Preference (V1.4 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| User-facing consent grant (POST /consent/grant, revoke, status) | High | ✅ Done |
| Import preference (POST/GET /import-preference/, 3 scopes) | High | ✅ Done |
| UI flow: Success → ImportPreference → Review → Complete | High | ✅ Done |
| Security: CSRF state validation, ownership verification, input bounds | High | ✅ Done |
| Design document: docs/consent-import-design.md | Medium | ✅ Done |

### Phase 3: Bank Account Connection (V1.3 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| Provider adapter pattern (abstract + registry) | High | ✅ Done |
| Mock AA provider (3 banks, 30 transactions, 5% failure) | High | ✅ Done |
| Consent lifecycle (initiate, finalize, revoke, expiry) | High | ✅ Done |
| Field-level encryption (Fernet AES-256-GCM) | High | ✅ Done |
| 5 API endpoints (connect, consent, accounts, status, disconnect) | High | ✅ Done |
| 4 frontend pages (ConnectBank, Consent, Success, ManageAccounts) | High | ✅ Done |
| Design document: docs/bank-connect-design.md | Medium | ✅ Done |

### Phase 2: Landing Page (V1.2 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| 13-section landing page with Framer Motion | Medium | ✅ Done |
| 5 sub-pages (Features, About, Contact, Privacy, Terms) | Medium | ✅ Done |
| UI primitives (Button, Card, SectionHeading, GradientText, Badge) | Medium | ✅ Done |
| Preview mockups (HealthScoreGauge, SpendingChart, CopilotChat, Dashboard) | Medium | ✅ Done |
| CSS isolation (.landing-page scope) | Medium | ✅ Done |
| SEO meta tags, OG cards, accessibility | Low | ✅ Done |

### Phase 1: Core Application (V1.1 — ✅ Completed)

| Task | Priority | Status |
|------|----------|--------|
| Auth: JWT registration/login, bcrypt hashing | High | ✅ Done |
| Expense tracking: Full CRUD + NLP categorization | High | ✅ Done |
| Budget management: CRUD + usage tracking (safe/warning/over) | High | ✅ Done |
| Budget alerts: 75%/90%/100% thresholds | High | ✅ Done |
| Dashboard: Summary, trends, category breakdown, health score | High | ✅ Done |
| Financial health: 4-factor weighted scoring (0-100) | High | ✅ Done |
| Recommendations: Rule-based engine | Medium | ✅ Done |
| Anomaly detection: ML-powered with severity levels | High | ✅ Done |
| Recurring expenses: CRUD + auto-detection + predictions | Medium | ✅ Done |
| Subscription tracker: CRUD + auto-detection + cost insights | Medium | ✅ Done |
| Financial reports: Weekly/monthly generation | Medium | ✅ Done |
| Budget suggestions: ML-based optimization | High | ✅ Done |
| WebSocket: Connection manager + token auth | Medium | ✅ Done |
| Event bus: In-memory infrastructure | Medium | ✅ Done |
| Repository pattern: Abstract interfaces + Mongo impl | Medium | ✅ Done |
| Middleware stack: RequestID, Logger, ErrorHandler, CORS | Medium | ✅ Done |
| Docker: Compose (MongoDB, Redis, Backend, Frontend, Nginx) | High | ✅ Done |
| CI/CD: GitHub Actions for tests + ML training | Medium | ✅ Done |
| Testing: Integration tests with fake collections | Medium | ✅ Done |

---

## Refactoring Summary

| Refactoring | Status |
|-------------|--------|
| Layered backend structure (api/core/db/domain/infrastructure/services/utils) | ✅ Done |
| Pydantic v2 schemas for all endpoints | ✅ Done |
| Custom exception hierarchy (AppException, NotFoundException, etc.) | ✅ Done |
| Middleware stack (RequestID, Logger, ErrorHandler) | ✅ Done |
| WebSocket manager + auth infrastructure | ✅ Done |
| Event bus infrastructure (in-memory) | ✅ Done |
| Repository pattern skeletons (abstract + Mongo impl) | Partial — some services still use direct DB |
| MongoDB index management in connection setup | ✅ Done (35+ collections indexed) |
| Docker Compose with all services | ✅ Done |
| Nginx reverse proxy for production | ✅ Done |
| GitHub Actions CI + ML pipeline | ✅ Done |
| Frontend store pattern (observer) | ✅ Done |
| Frontend WebSocket hook with auto-reconnect | ✅ Done |

---

## Known Issues

1. **Duplicate state management**: `authStore.js` and `AuthContext.jsx` both manage auth state. This creates potential for sync issues.
2. **Direct DB access in services**: Some legacy services call `db.collection.find()` directly instead of going through repository abstractions.
3. **Unused repository interfaces**: Some domain repository interfaces and Mongo implementations exist but are not referenced by services.
4. **Notification service is noop**: `notification_service.py` defines a protocol but only provides a `NoopBudgetAlertNotifier`.
5. **No background task processing**: Anomaly detection, report generation, budget suggestion generation, and consent expiry checking run synchronously in the request-response cycle.
6. **Hardcoded category list**: Categories are duplicated in backend `constants.py` and frontend `config/constants.js`.
7. **Webpack instead of Vite**: README references Vite but the project uses Webpack.
8. **No TypeScript**: Frontend is plain JavaScript with no type safety.
9. **No rate limiting**: Auth endpoints are unprotected against brute force attacks.
10. **No request body logging**: Debugging difficult without request payload logging.
11. **Shell=True in start_all.py**: Security concern if used outside development.
12. **ML model path hardcoded**: `ml_service.py` uses relative path resolution instead of settings.
13. **No pagination on list endpoints**: Some list endpoints lack pagination.
14. **No data cleanup**: No mechanism to clean stale data.
15. **Sync runs synchronously**: Each sync request blocks until the provider returns.
16. **No incremental sync**: Every sync re-fetches the full date range.
17. **No sync scheduling**: Sync is only user-initiated.
18. **MonthlySummary not yet written**: Schema and repo exist but pipeline does not write to it yet.

---

## Database Collections (35+)

| Collection | Phase | Purpose |
|------------|-------|---------|
| users | Core | User accounts |
| expenses | Core | Expense records |
| budgets | Core | Monthly budgets |
| budget_alerts | Core | Threshold alerts |
| financial_scores | Core | Health scores |
| recommendations | Core | Recommendations |
| spending_anomalies | Core | Anomaly records |
| budget_suggestions | Core | Budget suggestions |
| financial_reports | Core | Generated reports |
| recurring_expenses | Core | Recurring expenses |
| subscriptions | Core | Subscriptions |
| bank_accounts | Bank | Connected bank accounts |
| consents | Consent | User-facing consents |
| import_preferences | Consent | Import scopes |
| bank_transactions | Sync | Raw provider transactions |
| sync_logs | Sync | Sync audit logs |
| financial_transactions | AI Engine | Enriched transactions |
| merchant_dictionary | AI Engine | Known merchants |
| merchant_aliases | AI Engine | Merchant alias patterns |
| category_feedback | AI Engine | User feedback |
| transaction_tags | AI Engine | Transaction tags |
| budget_usage | Processing | Budget usage tracking |
| dashboard_metrics | Processing | Pre-computed metrics |
| financial_metrics | Processing | Financial metrics |
| cash_flow_summary | Processing | Cash flow data |
| monthly_summary | Processing | Monthly summaries |
| processing_batches | Processing | Batch tracking |
| notifications | Dashboard V2 | User notifications |
| financial_health | Health V2 | Health scores |
| financial_health_history | Health V2 | Health history |
| financial_health_factors | Health V2 | Factor breakdowns |
| financial_risk_profile | Health V2 | Risk assessments |
| health_recommendations | Health V2 | Health recs |
| budget_intelligence | Budget V2 | Intelligence data |
| budget_recommendations | Budget V2 | Budget recs |
| budget_predictions | Budget V2 | Predictions |
| budget_opportunities | Budget V2 | Savings opps |
| budget_risk | Budget V2 | Risk assessments |
| chat_sessions | Copilot | Chat sessions |
| chat_messages | Copilot | Chat messages |
| conversation_memory | Copilot | Conversation state |
| conversation_summary | Copilot | Summaries |
| ai_feedback | Copilot | AI feedback |
| financial_goals | Goals | Financial goals |
| goal_progress | Goals | Goal progress |
| goal_recommendations | Goals | Goal recs |
| goal_predictions | Goals | Goal predictions |
| goal_notifications | Goals | Goal alerts |
| receipts | OCR | Receipt records |
| receipt_processing_logs | OCR | Processing logs |
