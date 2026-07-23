# IntelliMoney

AI-powered financial health scoring platform with expense tracking, budget management, analytics, bank account connection (read-only via RBI Account Aggregator), and personalized financial intelligence.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, React Router 7, Recharts, Lucide Icons, Axios, Tailwind CSS 3, PostCSS, Framer Motion, `useReducedMotion` |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Motor (async MongoDB) |
| **Database** | MongoDB 7, Redis 7 (optional cache) |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **ML/NLP** | Scikit-learn (TF-IDF + Logistic Regression), Joblib |
| **AI/LLM** | LangChain, OpenAI API, RAG (FAISS), tiktoken |
| **OCR** | Tesseract OCR (pytesseract), OpenCV, Pillow |
| **Encryption** | Fernet (AES-256-GCM) for sensitive bank data at rest |
| **Infrastructure** | Docker Compose, Nginx, GitHub Actions |
| **Testing** | Pytest, HTTPX |

## Folder Structure

```
IntelliMoney/
├── backend/                   FastAPI application (layered architecture)
│   ├── app/
│   │   ├── ai/                    AI Transaction Intelligence (9-stage pipeline)
│   │   ├── api/
│   │   │   ├── routes/            30 route modules (auth, bank, sync, consent, expenses,
│   │   │   │                      budgets, intelligence, processing, dashboard_v2,
│   │   │   │                      dashboard_v2_extended, health_v2, budget_intelligence_v2,
│   │   │   │                      copilot_v2, goal_planning_v2, receipt_ocr_v2, ...)
│   │   │   └── v1/                router.py (aggregates all routes) + websocket
│   │   ├── budget_intelligence/   Budget Intelligence V2 (5 models, 5 repos, 8 services)
│   │   ├── core/                  Config, exceptions, encryption, security, middleware
│   │   ├── copilot/               LangChain AI Copilot (5 models, 5 repos, 5 services)
│   │   ├── dashboard/             Dashboard V2 (3 services: Dashboard, Notification, Widget)
│   │   ├── db/                    MongoDB connection + index management (35+ collections)
│   │   ├── domain/                Domain models + interfaces (bank_accounts, consents,
│   │   │                          import_preferences, sync, financial_transactions, expenses, users, recurring)
│   │   ├── goal_planning/         AI Goal Planning V2 (5 models, 5 repos, 7 services)
│   │   ├── health/                Financial Health V2 (4 models, 4 repos, 7 services)
│   │   ├── infrastructure/
│   │   │   ├── bank_integration/  Provider adapters + consent manager + merchant normalization
│   │   │   ├── cache/             Redis cache client
│   │   │   ├── database/repositories/ Mongo repos (sync, bank, consent, import_preference,
│   │   │   │                              expense, user, intelligence repos)
│   │   │   ├── messaging/         Event bus infrastructure
│   │   │   └── websocket/         Connection manager + auth
│   │   ├── ml/                    ML model artifacts (TF-IDF + Logistic Regression)
│   │   ├── models/                MongoDB TypedDict document definitions
│   │   ├── presentation/          Response serializers
│   │   ├── processing/            Financial Processing Engine (6 models, 6 repos, 10 services)
│   │   ├── receipt_ocr/           Receipt OCR V2 (2 models, 2 repos, 4 services)
│   │   ├── schemas/               Pydantic v2 request/response schemas
│   │   ├── services/              Business logic layer (sync, bank, consent, intelligence, etc.)
│   │   └── utils/                 Date, frequency, ObjectId utilities
│   ├── tests/                     Backend test suite
│   └── requirements.txt
├── frontend/                  React SPA (Webpack)
│   ├── src/
│   │   ├── api/                   Axios client + domain modules
│   │   ├── auth/                  Auth context + provider
│   │   ├── components/            UI components (bank/, import/, ProtectedRoute, etc.)
│   │   ├── dashboard/             Dashboard V2 pages (7: Overview, Analytics, Spending,
│   │   │                          Cashflow, Budgets, Insights, Notifications)
│   │   ├── landing/               Public landing page (isolated from dashboard)
│   │   ├── layouts/               AppLayout, DashboardLayout, HealthLayout,
│   │   │                          BudgetIntelligenceLayout, CopilotLayout,
│   │   │                          GoalsLayout, ReceiptsLayout
│   │   ├── pages/                 Route-level page components
│   │   │   ├── Sync.jsx, SyncHistory.jsx, SyncStatus.jsx
│   │   │   ├── ConnectBank.jsx, ConsentPage.jsx, ConnectSuccess.jsx
│   │   │   ├── ImportPreference.jsx, ReviewPage.jsx, CompletePage.jsx
│   │   │   ├── ManageAccounts.jsx
│   │   │   ├── health/            Health V2 pages (5: Overview, History, Trends, Recs, Risk)
│   │   │   ├── budgetIntelligence/ BI pages (5: Overview, Recs, Optimization, Trends, Opps)
│   │   │   ├── copilot/           Copilot pages (4: Chat, History, Detail, Settings)
│   │   │   ├── goals/             Goal pages (6: Overview, Create, Detail, Recs, Progress, History)
│   │   │   └── receipts/          Receipt pages (4: Overview, Upload, Review, History)
│   │   ├── store/                 Observer-pattern state stores
│   │   └── utils/                 Currency formatting
│   └── package.json
├── ml/                        ML training scripts + data
├── docker/                    Dockerfiles + Nginx config
├── scripts/                   One-click startup/stop batch files
└── docs/                      Documentation
```

## Features

### Core Infrastructure (V1.0)
- **Secure Auth**: JWT registration/login with bcrypt password hashing
- **Expense Tracking**: Full CRUD with filters + NLP auto-categorization
- **Budget Management**: Monthly limits with usage tracking (safe/warning/over) and alerts
- **Dashboard**: Spending trends, category breakdown, health score, recommendations
- **Financial Health**: Weighted scoring (0-100) across 4 dimensions
- **Anomaly Detection**: ML-powered spending anomaly detection with severity levels
- **Recurring Expenses**: Auto-detection from history + upcoming predictions
- **Subscription Tracker**: Auto-detection + payment recording + cost analysis
- **Financial Reports**: Automated weekly/monthly reports with insights
- **Budget Optimizer**: ML-based smart budget suggestions with confidence scoring
- **WebSocket**: Real-time connection management with token auth
- **Event Bus**: In-memory event-driven architecture foundation
- **Design System**: Tailwind CSS with emerald/blue theme, glassmorphism, reusable primitives

### Landing Page (V1.1)
- Premium SaaS landing page with 13 Framer Motion-animated sections
- 5 sub-pages: Features, About, Contact, Privacy Policy, Terms of Service
- Preview mockups: Health Score gauge, Spending chart, AI Copilot chat, Dashboard

### Bank Connection (V1.2)
- Provider adapter pattern (Mock AA provider: SBI, HDFC, ICICI)
- Consent lifecycle (initiate, finalize, revoke, expiry detection)
- Field-level encryption via Fernet (AES-256-GCM)

### Consent & Import Preference (V1.3)
- User-facing consent grant (separate from AA-level consent)
- Import scope per account: all history, start fresh, or from a specific date

### Financial Data Synchronization Engine (V1.4)
- Full sync lifecycle with consent validation, dedup, progress tracking
- Sync audit log with state machine (pending→running→completed/failed)
- Retry logic (max 3 retries), concurrency protection

### AI Transaction Intelligence Engine (V1.5)
- 9-stage pipeline: Validate → Merchant Normalize → Income/Expense Detect → Category Predict → Recurring Detect → Confidence Score → Review Decide → Build Model → Bulk Persist
- 31 merchants with 3-tier alias matching (exact/contains/regex)
- 5-factor confidence scoring, auto-approval thresholds
- Manual review queue for low-confidence items
- Feedback learning for future ML retraining

### Financial Processing Engine (V1.6)
- 9-stage pipeline: Validate → Dedup (atomic claim) → Expense Generation → Budget Usage → Cash Flow → Savings → Financial Metrics → Dashboard Aggregation → Budget Alerts
- Period-scoped aggregations, idempotent upserts, atomic claim-based dedup
- 6 output collections, 7 event types, config-driven settings

### Dashboard V2 (Phase 5)
- Pre-computed dashboard data from processing engine
- 7 interactive pages: Overview, Analytics, Spending, Cashflow, Budgets, Insights, Notifications
- Real-time WebSocket updates (7 event types)
- 4 chart components (SpendingChart, CategoryPieChart, CashflowChart, TrendsChart)
- Customizable widget system with 4 widget types (Spending, Budget, Health, Recurring)
- Notification center with read/unread tracking, activity feed, AI insights

### Financial Health Engine V2 (Phase 6)
- 10-factor weighted health score formula (savings rate, budget adherence, expense stability, income stability, debt-to-income, emergency fund, discretionary ratio, recurring commitments, income growth, category diversity)
- 5 risk levels: Excellent, Good, Fair, Moderate, Poor
- 7 services: HealthScoreCalculator, RiskAssessmentService, HealthHistoryService, TrendAnalysisService, RecommendationEngine, HealthAggregationService, FinancialHealthService
- 8 backend routes (calculate, recalculate, current, history, trends, breakdown, recommendations, risk)
- 5 frontend pages: Overview, History, Trends, Recommendations, Risk

### Budget Intelligence V2 (Phase 7)
- Smart budget allocation with ML-based recommendations
- Category trend analysis with spending pattern detection
- Budget forecasting with prediction models
- Budget risk assessment (overspending categories, volatility scoring)
- Savings opportunity detection with actionable steps
- 8 services: SmartBudgetService, CategoryTrendService, BudgetForecastService, BudgetRiskService, BudgetRecommendationService, BudgetOptimizationService, SavingsOpportunityService, BudgetIntelligenceService
- 8 backend routes (generate, recalculate, current, recommendations, optimization, trends, risk, opportunities)
- 5 frontend pages: Overview, Recommendations, Optimization, Trends, Opportunities

### LangChain AI Copilot (Phase 8)
- Natural language queries over financial data
- 11 custom LangChain tools wrapping existing collections
- RAG (FAISS) for financial context retrieval
- Conversation memory with auto-summarization
- Injection detection and PII masking
- 7 backend routes (chat, sessions, session detail, delete sessions, feedback, suggestions, settings)
- 4 frontend pages: Chat, History, History Detail, Settings

### AI Financial Goal Planning Engine (Phase 9)
- 10 financial goal types (savings, emergency_fund, debt_repayment, investment, retirement, education, home_purchase, travel, wedding, custom)
- Goal feasibility analysis with 4-factor scoring
- Savings plan with discretionary overspend detection
- 60-month goal projection with probability of success
- Milestone tracking with missed detection
- 7 services: GoalFeasibilityService, SavingsPlanService, GoalPredictionService, GoalProgressService, GoalRecommendationService, GoalNotificationService, GoalPlanningService
- 9 backend routes (CRUD + analyze, recalculate, recommendations, progress)
- 6 frontend pages: Overview, Create, Detail, Recommendations, Progress, History

### Receipt OCR & Manual Expense Import (Phase 10)
- Image preprocessing with OpenCV (deskew, denoise, threshold)
- Tesseract OCR with regex extraction (merchant, amount, date, time, currency)
- Receipt validation (image checks, field validation, update validation)
- Full upload→validate→OCR→categorize→createExpense→publishEvent pipeline
- 8 backend routes (upload, process, confirm, CRUD, image serving)
- 4 frontend pages: Overview, Upload (drag-drop), Review (editable fields), History (with delete)

### One-Click Startup (Phase 11)
- `scripts/start-IntelliMoney.bat`: 7-step automated startup (env validation, Docker, backend venv+install+uvicorn, frontend npm+dev, health checks, browser launch)
- `scripts/stop-IntelliMoney.bat`: Graceful stop (backend, frontend, Docker, port cleanup)
- Structured logging to `logs/startup.log`

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 7+ (local or Atlas)
- Redis 7+ (optional)

### 1. Clone and setup

```bash
git clone <repo-url>
cd IntelliMoney

# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB connection string
# Set SECRET_KEY and BANK_ENCRYPTION_KEY (required)

# Train ML model
cd ..
python ml/train_model.py

# Frontend
cd frontend
npm install
cp .env.example .env
```

### 2. Start services

```bash
# Using Docker (recommended)
docker compose up -d

# Or manually:
# Terminal 1: MongoDB (must be running)
# Terminal 2: cd backend && uvicorn app.main:app --reload --port 8080
# Terminal 3: cd frontend && npm run dev
```

### 3. Load demo data

```bash
cd backend
.venv\Scripts\activate
python seed_demo.py
```

### 4. Access

- Frontend: http://localhost:5173
- API Docs: http://localhost:8080/docs
- Demo login: `demo@example.com` / `password123`

### 5. One-Click Startup (Windows)

For a fully automated startup experience on Windows:

```batch
:: Double-click this file:
scripts\start-IntelliMoney.bat
```

This single batch file automatically:

1. **Validates** your environment (Git, Python, Node.js, npm, Docker)
2. **Starts Docker** containers (MongoDB, Redis) if Docker Desktop is running
3. **Creates** a Python virtual environment and installs dependencies
4. **Starts** the FastAPI backend on port 8080
5. **Starts** the Webpack dev server on port 5173
6. **Performs** health checks on all services
7. **Opens** the application in your browser
8. **Displays** a summary with URLs and status

To stop all services:

```batch
:: Double-click this file:
scripts\stop-IntelliMoney.bat
```

The stop script gracefully terminates backend, frontend, and Docker containers without deleting your data.

> **Note:** You must configure `backend/.env` with `SECRET_KEY` and `BANK_ENCRYPTION_KEY` before running the startup script for the first time. Copy from `.env.example` if needed.

## API Overview

All endpoints are prefixed with `/api/v1/`. See full interactive docs at `/docs` when running.

| Category | Endpoints |
|----------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Bank | `POST /bank/connect`, `POST /bank/consent`, `GET /bank/accounts`, `GET /bank/status`, `DELETE /bank/disconnect/{id}` |
| Consent | `POST /consent/grant`, `POST /consent/revoke`, `GET /consent/status` |
| Import Preference | `POST /import-preference/`, `GET /import-preference/` |
| Sync | `POST /sync/start`, `POST /sync/manual`, `GET /sync/status`, `GET /sync/history`, `POST /sync/retry` |
| Expenses | `GET/POST /expenses`, `GET/PUT/DELETE /expenses/{id}` |
| Budgets | `GET/POST /budgets`, `GET /budgets/status`, `PUT/DELETE /budgets/{id}` |
| Analytics | `GET /analytics/summary`, `/monthly-spending`, `/category-breakdown`, `/payment-methods`, `/recent-expenses` |
| Health | `GET /financial-health/score` |
| Recommendations | `GET /recommendations` |
| Alerts | `GET /alerts`, `PATCH /alerts/{id}/read` |
| Anomaly | `GET /anomaly`, `POST /anomaly/detect`, `GET /anomaly/alerts`, `GET /anomaly/weekly-report` |
| Budget Suggestions | `GET /budget-suggestions`, `POST /generate`, `POST /{id}/apply`, `DELETE /{id}`, `GET /optimization-report` |
| Reports | `GET /reports`, `POST /generate/weekly`, `/generate/monthly`, `PATCH /{id}/read` |
| Subscriptions | `GET/POST /subscriptions`, `PUT/DELETE /{id}`, `GET /suggestions/detect`, `GET /insights`, `POST /{id}/record-payment` |
| Recurring | `GET/POST /recurring`, `PUT/DELETE /{id}`, `GET /suggestions/detect`, `GET /upcoming` |
| ML | `POST /ml/categorize` |
| Intelligence | `POST /intelligence/process`, `/process-all`, `/reprocess`, `GET /intelligence/status`, `/history`, `/review`, `PATCH /intelligence/review/{id}`, `POST /intelligence/feedback/{id}` |
| Financial Transactions | `GET /financial-transactions`, `GET /financial-transactions/{id}`, `PUT /financial-transactions/{id}` |
| Processing | `POST /processing/process`, `/process-all`, `/reprocess`, `GET /processing/status`, `/history` |
| Dashboard V2 | `GET /dashboard/summary`, `/spending`, `/cashflow`, `/monthly`, `/overview`, `/analytics`, `/budgets`, `/insights`, `/notifications`, `/notifications/unread-count`, `POST /notifications/{id}/read`, `POST /notifications/read-all`, `/activity`, `/widgets` |
| Health V2 | `POST /health/calculate`, `/recalculate`, `GET /health/current`, `/history`, `/trends`, `/breakdown`, `/recommendations`, `/risk` |
| Budget Intelligence V2 | `POST /budget-intelligence/generate`, `/recalculate`, `GET /budget-intelligence/current`, `/recommendations`, `/optimization`, `/trends`, `/risk`, `/opportunities` |
| Copilot V2 | `POST /copilot/chat`, `GET /copilot/sessions`, `GET /copilot/sessions/{id}`, `DELETE /copilot/sessions`, `POST /copilot/feedback`, `GET /copilot/suggestions`, `GET /copilot/settings` |
| Goals V2 | `POST /goals`, `PUT /goals/{id}`, `DELETE /goals/{id}`, `GET /goals`, `GET /goals/{id}`, `POST /goals/analyze`, `POST /goals/recalculate`, `GET /goals/recommendations`, `GET /goals/progress` |
| Receipts V2 | `POST /receipts/upload`, `POST /receipts/{id}/process`, `POST /receipts/{id}/confirm`, `GET /receipts`, `GET /receipts/{id}`, `PATCH /receipts/{id}`, `DELETE /receipts/{id}`, `GET /receipts/{id}/image` |
| WebSocket | `ws://host/api/v1/ws?token=<jwt>` |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for comprehensive architecture analysis and V2 design.
See [docs/AI_TRANSACTION_ENGINE.md](docs/AI_TRANSACTION_ENGINE.md) for AI pipeline architecture.
See [docs/FINANCIAL_PROCESSING_ENGINE.md](docs/FINANCIAL_PROCESSING_ENGINE.md) for Financial Processing Engine architecture.
See [docs/bank-connect-design.md](docs/bank-connect-design.md) for bank connection architecture.
See [docs/consent-import-design.md](docs/consent-import-design.md) for consent & import preference architecture.

## Project State

See [PROJECT_STATE.md](PROJECT_STATE.md) for detailed feature status, known issues, and technical debt.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Comprehensive architecture analysis and V2 design |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Current feature status, known issues, technical debt |
| [ROADMAP.md](ROADMAP.md) | Future phases and planned work |
| [docs/AI_TRANSACTION_ENGINE.md](docs/AI_TRANSACTION_ENGINE.md) | AI Transaction Intelligence Engine architecture |
| [docs/FINANCIAL_PROCESSING_ENGINE.md](docs/FINANCIAL_PROCESSING_ENGINE.md) | Financial Processing Engine architecture |
| [docs/DASHBOARD_V2.md](docs/DASHBOARD_V2.md) | Dashboard V2 architecture |
| [docs/FINANCIAL_HEALTH_V2.md](docs/FINANCIAL_HEALTH_V2.md) | Financial Health Engine V2 architecture |
| [docs/BUDGET_INTELLIGENCE_V2.md](docs/BUDGET_INTELLIGENCE_V2.md) | Budget Intelligence V2 architecture |
| [docs/AI_COPILOT.md](docs/AI_COPILOT.md) | LangChain AI Copilot architecture |
| [docs/GOAL_PLANNING_ENGINE.md](docs/GOAL_PLANNING_ENGINE.md) | AI Goal Planning Engine architecture |
| [docs/RECEIPT_OCR.md](docs/RECEIPT_OCR.md) | Receipt OCR & Expense Import architecture |
| [docs/bank-connect-design.md](docs/bank-connect-design.md) | Bank connection architecture |
| [docs/consent-import-design.md](docs/consent-import-design.md) | Consent & import preference architecture |

## Resume Description

**IntelliMoney - AI-Powered Financial Health Platform**  
Built a full-stack financial analytics platform with Python/FastAPI/React/MongoDB/Scikit-learn. Implemented JWT auth, bank account connection (RBI AA Provider Adapter pattern with field-level encryption), expense tracking, budget management, ML-based categorization (TF-IDF + Logistic Regression), anomaly detection, financial health scoring, subscription tracking, recurring expense detection, automated reporting, and real-time WebSocket infrastructure. Architected for extensibility with event-driven patterns, repository abstraction, and layered design.
