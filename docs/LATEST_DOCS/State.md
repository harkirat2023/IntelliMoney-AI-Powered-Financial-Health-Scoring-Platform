# IntelliMoney — Comprehensive Codebase Audit Report

**Generated:** 2026-07-21  
**Source:** Raw code files only (`backend/`, `frontend/`, `ml/`, config files). No existing `.md` documents consulted.

---

## 1. TECH STACK SUMMARY

### Frontend
| Layer | Technology | Details |
|---|---|---|
| Framework | React 19.0.0 | No Next.js; SPA with `react-router-dom` v7 |
| Build | Webpack 5 + Babel | Entry: `./src/main.jsx` (relative to `frontend/`) |
| UI/Styling | Tailwind CSS 3.4 + custom CSS | `postcss.config.js`, `tailwind.config.js`, 2510-line `styles.css` |
| Components | Radix UI (Accordion, Dialog, NavMenu) | `@radix-ui/*` packages |
| State | Custom stores with subscribe/notify pattern | No Redux/Zustand; 8 manual store files |
| API Client | Axios | Interceptor attaches `Bearer` token from localStorage |
| Charts | Recharts 2.15 | Bar, Line, Pie charts |
| Animation | Framer Motion 12 | Landing page transitions |
| Icons | Lucide React 0.468 | 90+ icon components |
| Auth | Custom JWT (no Clerk) | `AuthContext.jsx` with localStorage token |

### Backend
| Layer | Technology | Details |
|---|---|---|
| Runtime | Python 3.12 | FastAPI 0.115+ with async lifespan |
| Server | Uvicorn (dev), Gunicorn (prod) | `start.py` / `Procfile` |
| Database | MongoDB 7 + Motor (async driver) | AsyncIOMotorClient with pooling |
| Auth | JWT (python-jose) + bcrypt | `HS256`, 24h expiry |
| AI/LLM | OpenAI (GPT-4o) via LangChain | `ChatOpenAI`, custom `LLMService` |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) | FAISS vector store for RAG |
| ML Classifier | scikit-learn (LogisticRegression + TfidfVectorizer) | Joblib serialized model at `app/ml/` |
| OCR | Tesseract (pytesseract) + OpenCV | Receipt text extraction |
| Validation | Pydantic v2 + Pydantic-Settings | Strict schema validation |
| Encryption | cryptography (Fernet) | Bank encryption key for sensitive data |
| Event Bus | Custom in-memory | `EventBus` + `Event` classes |
| Cache | Redis (optional) | Via `redis.py` infrastructure layer |

### Infrastructure & Hosting
| Environment | Technology | Details |
|---|---|---|
| Local Dev | Docker Compose | MongoDB, Redis (profile), Backend (8080), Frontend (5173/3002) |
| Production Backend | Railway (render.yaml) | `rootDir: backend`, Python web service |
| Production Frontend | Vercel (vercel.json) | `rootDir: frontend`, SPA rewrites |
| Database | MongoDB Atlas | Connection string via env `MONGODB_URL` |
| Cache | Redis | Optional; configured via `REDIS_URL` |
| ML Model Path | `backend/app/ml/expense_classifier.joblib` | Trained at build time via `render.yaml` |

---

## 2. APPLICATION EXECUTION & PORTS

### Frontend (Webpack Dev Server)
- **Command:** `npm run dev` (from `frontend/`)
- **Port:** 5173
- **Proxy:** `/api` → `http://localhost:8080` (dev only)
- **API Base URL:** `http://localhost:8080/api/v1` (default, overridable via `API_BASE_URL` env)
- **Env file:** `frontend/.env` (not committed, `.env.example` provided)

### Backend (FastAPI)
- **Command:** `uvicorn app.main:app --reload --host 0.0.0.0 --port 8080` (via `start.py`)
- **Port:** 8080
- **Host:** `0.0.0.0`
- **Auto-docs:** `/docs` (Swagger), `/redoc` (ReDoc)
- **Health:** `/healthz`, `/api/health`
- **Socket:** `/api/v1/ws`, `/api/v1/ws/dashboard`

### Docker Compose
```yaml
mongodb:  mongodb:7          → port 27017
redis:    redis:7-alpine     → port 6379 (profile: with-redis)
backend:  Dockerfile.backend → port 8080 (env: MONGODB_URL=mongodb://mongodb:27017)
frontend: Dockerfile.frontend→ port 3002 (nginx serving static build)
```

### Startup Orchestration (`scripts/start-IntelliMoney.bat`)
```
Docker mode:
  1. docker compose up -d
  2. docker compose run --rm seed

Native mode:
  1. python -m venv venv → pip install -r requirements.txt
  2. python scripts/create_indexes.py
  3. python backend/scripts/seed_demo.py
  4. uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
  5. npm install → npm run dev (port 5173)
```

### Environment Flags
| Variable | Default | Purpose |
|---|---|---|
| `API_BASE_URL` | `http://localhost:8080/api/v1` | Frontend API target |
| `ML_ALLOW_FALLBACK` | `false` | Fallback to keyword matching if model missing |
| `BANK_ENCRYPTION_KEY` | (required) | Fernet key for bank data encryption |
| `OPENAI_API_KEY` | (required for Copilot) | GPT-4o access |
| `REDIS_URL` | `""` (empty = disabled) | Redis cache connection |

---

## 3. COMPLETE ROUTE MAPPING

### 3A. FRONTEND ROUTES

#### Public Routes (LandingLayout — no auth required)
| Path | Component | Source File |
|---|---|---|
| `/` | `HomePage` | `frontend/src/landing/pages/HomePage.jsx` |
| `/features` | `FeaturesPage` | `frontend/src/landing/pages/FeaturesPage.jsx` |
| `/about` | `AboutPage` | `frontend/src/landing/pages/AboutPage.jsx` |
| `/contact` | `ContactPage` | `frontend/src/landing/pages/ContactPage.jsx` |
| `/privacy` | `PrivacyPage` | `frontend/src/landing/pages/PrivacyPage.jsx` |
| `/terms` | `TermsPage` | `frontend/src/landing/pages/TermsPage.jsx` |
| `/connect-bank` | `ConnectBank` | `frontend/src/pages/ConnectBank.jsx` |
| `/connect-bank/consent` | `ConsentPage` | `frontend/src/pages/ConsentPage.jsx` |
| `/connect-bank/success` | `ConnectSuccess` | `frontend/src/pages/ConnectSuccess.jsx` |
| `/connect-bank/manage` | `ManageAccounts` | `frontend/src/pages/ManageAccounts.jsx` |
| `/connect-bank/import-preference` | `ImportPreference` | `frontend/src/pages/ImportPreference.jsx` |
| `/connect-bank/review` | `ReviewPage` | `frontend/src/pages/ReviewPage.jsx` |
| `/connect-bank/complete` | `CompletePage` | `frontend/src/pages/CompletePage.jsx` |

#### Auth Routes (no layout)
| Path | Component | Source File |
|---|---|---|
| `/login` | `Login` | `frontend/src/pages/Login.jsx` |
| `/register` | `Register` | `frontend/src/pages/Register.jsx` |

#### Protected Routes (`/app` — wrapped in `AppLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app` | `Dashboard` | `frontend/src/pages/Dashboard.jsx` |
| `/app/expenses` | `Expenses` | `frontend/src/pages/Expenses.jsx` |
| `/app/budgets` | `Budgets` | `frontend/src/pages/Budgets.jsx` |
| `/app/budget-optimizer` | `BudgetOptimizer` | `frontend/src/pages/BudgetOptimizer.jsx` |
| `/app/reports` | `Reports` | `frontend/src/pages/Reports.jsx` |
| `/app/subscriptions` | `Subscriptions` | `frontend/src/pages/Subscriptions.jsx` |
| `/app/recurring` | `Recurring` | `frontend/src/pages/Recurring.jsx` |
| `/app/anomaly` | `Anomaly` | `frontend/src/pages/Anomaly.jsx` |
| `/app/bank-accounts` | `ManageAccounts` | `frontend/src/pages/ManageAccounts.jsx` |
| `/app/sync` | `Sync` | `frontend/src/pages/Sync.jsx` |
| `/app/sync/history` | `SyncHistory` | `frontend/src/pages/SyncHistory.jsx` |
| `/app/sync/status` | `SyncStatus` | `frontend/src/pages/SyncStatus.jsx` |

#### Dashboard V2 Sub-routes (`/app/dashboard` — `DashboardLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/dashboard` | `OverviewPage` | `frontend/src/dashboard/pages/OverviewPage.jsx` |
| `/app/dashboard/overview` | `OverviewPage` | same |
| `/app/dashboard/analytics` | `AnalyticsPage` | `frontend/src/dashboard/pages/AnalyticsPage.jsx` |
| `/app/dashboard/spending` | `SpendingPage` | `frontend/src/dashboard/pages/SpendingPage.jsx` |
| `/app/dashboard/cashflow` | `CashflowPage` | `frontend/src/dashboard/pages/CashflowPage.jsx` |
| `/app/dashboard/budgets` | `BudgetsPage` | `frontend/src/dashboard/pages/BudgetsPage.jsx` |
| `/app/dashboard/insights` | `InsightsPage` | `frontend/src/dashboard/pages/InsightsPage.jsx` |
| `/app/dashboard/notifications` | `NotificationsPage` | `frontend/src/dashboard/pages/NotificationsPage.jsx` |

#### Health Sub-routes (`/app/health` — `HealthLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/health` | `HealthOverviewPage` | `frontend/src/pages/health/HealthOverviewPage.jsx` |
| `/app/health/history` | `HealthHistoryPage` | `frontend/src/pages/health/HealthHistoryPage.jsx` |
| `/app/health/trends` | `HealthTrendsPage` | `frontend/src/pages/health/HealthTrendsPage.jsx` |
| `/app/health/recommendations` | `HealthRecommendationsPage` | `frontend/src/pages/health/HealthRecommendationsPage.jsx` |
| `/app/health/risk` | `HealthRiskPage` | `frontend/src/pages/health/HealthRiskPage.jsx` |

#### Budget Intelligence Sub-routes (`/app/budget-intelligence` — `BudgetIntelligenceLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/budget-intelligence` | `BIOOverviewPage` | `frontend/src/pages/budgetIntelligence/BIOOverviewPage.jsx` |
| `/app/budget-intelligence/recommendations` | `BIRecommendationsPage` | `frontend/src/pages/budgetIntelligence/BIRecommendationsPage.jsx` |
| `/app/budget-intelligence/optimization` | `BIOptimizationPage` | `frontend/src/pages/budgetIntelligence/BIOptimizationPage.jsx` |
| `/app/budget-intelligence/trends` | `BITrendsPage` | `frontend/src/pages/budgetIntelligence/BITrendsPage.jsx` |
| `/app/budget-intelligence/opportunities` | `BIOpportunitiesPage` | `frontend/src/pages/budgetIntelligence/BIOpportunitiesPage.jsx` |

#### Copilot Sub-routes (`/app/copilot` — `CopilotLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/copilot` | `CopilotChatPage` | `frontend/src/pages/copilot/CopilotChatPage.jsx` |
| `/app/copilot/history` | `CopilotHistoryPage` | `frontend/src/pages/copilot/CopilotHistoryPage.jsx` |
| `/app/copilot/history/:sessionId` | `CopilotHistoryDetailPage` | `frontend/src/pages/copilot/CopilotHistoryDetailPage.jsx` |
| `/app/copilot/settings` | `CopilotSettingsPage` | `frontend/src/pages/copilot/CopilotSettingsPage.jsx` |

#### Goals Sub-routes (`/app/goals` — `GoalsLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/goals` | `GoalsOverviewPage` | `frontend/src/pages/goals/GoalsOverviewPage.jsx` |
| `/app/goals/create` | `CreateGoalPage` | `frontend/src/pages/goals/CreateGoalPage.jsx` |
| `/app/goals/recommendations` | `GoalRecommendationsPage` | `frontend/src/pages/goals/GoalRecommendationsPage.jsx` |
| `/app/goals/progress` | `GoalProgressPage` | `frontend/src/pages/goals/GoalProgressPage.jsx` |
| `/app/goals/history` | `GoalHistoryPage` | `frontend/src/pages/goals/GoalHistoryPage.jsx` |
| `/app/goals/:goalId` | `GoalDetailPage` | `frontend/src/pages/goals/GoalDetailPage.jsx` |

#### Receipts Sub-routes (`/app/receipts` — `ReceiptsLayout`)
| Path | Component | Source File |
|---|---|---|
| `/app/receipts` | `ReceiptsOverviewPage` | `frontend/src/pages/receipts/ReceiptsOverviewPage.jsx` |
| `/app/receipts/upload` | `ReceiptUploadPage` | `frontend/src/pages/receipts/ReceiptUploadPage.jsx` |
| `/app/receipts/review` | `ReceiptReviewPage` | `frontend/src/pages/receipts/ReceiptReviewPage.jsx` |
| `/app/receipts/history` | `ReceiptHistoryPage` | `frontend/src/pages/receipts/ReceiptHistoryPage.jsx` |

#### Catch-all
| Path | Behavior |
|---|---|
| `*` | Redirects to `/` (unauthenticated) or `/app` (authenticated) |

---

### 3B. BACKEND API ENDPOINTS

All mounted at prefix `/api/v1`. Prefix omitted for brevity.

#### Auth — `app/api/routes/auth.py` (prefix: `/auth`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create user + JWT | No |
| POST | `/auth/login` | Verify password + JWT | No |
| GET | `/auth/me` | Return current user profile | Yes |

#### Expenses — `app/api/routes/expenses.py` (prefix: `/expenses`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/expenses` | Create expense (auto-categorize via ML) | Yes |
| GET | `/expenses` | List with filters (date, category, method, amount) | Yes |
| GET | `/expenses/{id}` | Get single expense | Yes |
| PUT | `/expenses/{id}` | Update expense fields | Yes |
| DELETE | `/expenses/{id}` | Delete expense | Yes |

#### Budgets — `app/api/routes/budgets.py` (prefix: `/budgets`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/budgets` | Create budget (unique by category+month+year) | Yes |
| GET | `/budgets` | List all budgets | Yes |
| GET | `/budgets/status` | Budget vs actual spending per category | Yes |
| PUT | `/budgets/{id}` | Update budget | Yes |
| DELETE | `/budgets/{id}` | Delete budget | Yes |

#### Analytics — `app/api/routes/analytics.py` (prefix: `/analytics`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/analytics/summary` | Aggregated totals, savings, top category | Yes |
| GET | `/analytics/monthly-spending` | Per-month spending time series | Yes |
| GET | `/analytics/category-breakdown` | Amount per category | Yes |
| GET | `/analytics/payment-methods` | Amount per payment method | Yes |
| GET | `/analytics/recent-expenses` | Last 10 expenses | Yes |

#### Financial Health — `app/api/routes/financial_health.py` (prefix: `/financial-health`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/financial-health/score` | Composite financial health score | Yes |

#### Recommendations — `app/api/routes/recommendations.py` (prefix: `/recommendations`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/recommendations` | Generate actionable recommendations | Yes |

#### ML — `app/api/routes/ml.py` (prefix: `/ml`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/ml/categorize` | Predict expense category from description | No |

#### Alerts — `app/api/routes/alerts.py` (prefix: `/alerts`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/alerts` | List budget alerts | Yes |
| PATCH | `/alerts/{id}/read` | Mark alert as read | Yes |

#### Anomaly — `app/api/routes/anomaly.py` (prefix: `/anomaly`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/anomaly` | List spending anomalies | Yes |
| GET | `/anomaly/alerts` | Get anomaly alert summaries | Yes |
| POST | `/anomaly/detect` | Run anomaly detection | Yes |
| PATCH | `/anomaly/{id}/read` | Mark anomaly as read | Yes |
| GET | `/anomaly/weekly-report` | Generate weekly anomaly report | Yes |

#### Budget Suggestions — `app/api/routes/budget_suggestion.py` (prefix: `/budget-suggestions`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/budget-suggestions` | List suggestions | Yes |
| POST | `/budget-suggestions/generate` | Generate new suggestions | Yes |
| POST | `/budget-suggestions/{id}/apply` | Apply a suggestion | Yes |
| DELETE | `/budget-suggestions/{id}` | Dismiss a suggestion | Yes |
| GET | `/budget-suggestions/optimization-report` | Full optimization report | Yes |

#### Reports — `app/api/routes/reports.py` (prefix: `/reports`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/reports` | List reports (optional type filter) | Yes |
| GET | `/reports/summary` | Report summary | Yes |
| GET | `/reports/{id}` | Get single report | Yes |
| POST | `/reports/generate/weekly` | Generate weekly report | Yes |
| POST | `/reports/generate/monthly` | Generate monthly report | Yes |
| PATCH | `/reports/{id}/read` | Mark report as read | Yes |

#### Subscriptions — `app/api/routes/subscriptions.py` (prefix: `/subscriptions`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/subscriptions` | List subscriptions | Yes |
| POST | `/subscriptions` | Create subscription | Yes |
| GET | `/subscriptions/{id}` | Get subscription | Yes |
| PUT | `/subscriptions/{id}` | Update subscription | Yes |
| DELETE | `/subscriptions/{id}` | Delete subscription | Yes |
| GET | `/subscriptions/suggestions/detect` | Detect subscription patterns | Yes |
| GET | `/subscriptions/insights` | Subscription spending insights | Yes |
| POST | `/subscriptions/{id}/record-payment` | Record payment for subscription | Yes |

#### Bank — `app/api/routes/bank.py` (prefix: `/bank`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/bank/connect` | Initiate bank connection (returns consent URL) | Yes |
| POST | `/bank/consent` | Submit consent and import accounts | Yes |
| GET | `/bank/accounts` | List connected bank accounts | Yes |
| GET | `/bank/status` | Connection status overview | Yes |
| DELETE | `/bank/disconnect/{id}` | Disconnect bank account | Yes |

#### Consent — `app/api/routes/consent.py` (prefix: `/consent`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/consent/grant` | Grant consent for account | Yes |
| POST | `/consent/revoke` | Revoke consent | Yes |
| GET | `/consent/status` | Consent status for an account | Yes |

#### Import Preference — `app/api/routes/import_preference.py` (prefix: `/import-preference`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/import-preference/` | Save import preference | Yes |
| GET | `/import-preference/` | Get import preference | Yes |

#### Recurring — `app/api/routes/recurring.py` (prefix: `/recurring`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/recurring` | List recurring expenses | Yes |
| POST | `/recurring` | Create recurring expense | Yes |
| GET | `/recurring/{id}` | Get recurring expense | Yes |
| PUT | `/recurring/{id}` | Update recurring expense | Yes |
| DELETE | `/recurring/{id}` | Delete recurring expense | Yes |
| GET | `/recurring/suggestions/detect` | Detect recurring patterns | Yes |
| GET | `/recurring/upcoming` | Upcoming recurring expenses | Yes |

#### Sync — `app/api/routes/sync.py` (prefix: `/sync`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/sync/start` | Start sync by bank account | Yes |
| POST | `/sync/manual` | Manual sync all accounts | Yes |
| GET | `/sync/status` | Sync status (optional account filter) | Yes |
| GET | `/sync/history` | Sync history with pagination | Yes |
| POST | `/sync/retry` | Retry failed sync | Yes |

#### Intelligence — `app/api/routes/intelligence.py` (prefix: `/intelligence`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/intelligence/process` | Process pending bank transactions | Yes |
| POST | `/intelligence/process-all` | Process all pending | Yes |
| POST | `/intelligence/reprocess` | Reprocess transactions | Yes |
| GET | `/intelligence/status` | Intelligence pipeline status | Yes |
| GET | `/intelligence/history` | Processed transaction history | Yes |
| GET | `/intelligence/review` | Get review queue | Yes |
| PATCH | `/intelligence/review/{tx_id}` | Submit review decision | Yes |
| POST | `/intelligence/feedback/{tx_id}` | Submit feedback for AI correction | Yes |

#### Financial Transactions — `app/api/routes/financial_transactions.py` (prefix: `/financial-transactions`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/financial-transactions` | List with pagination & category filter | Yes |
| GET | `/financial-transactions/{id}` | Get single transaction | Yes |
| PUT | `/financial-transactions/{id}` | Update category, merchant, tags, etc. | Yes |

#### Processing — `app/api/routes/processing.py` (prefix: `/processing`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/processing/process` | Process specific transactions | Yes |
| POST | `/processing/process-all` | Process all unprocessed | Yes |
| POST | `/processing/reprocess` | Reprocess transactions | Yes |
| GET | `/processing/status` | Processing batch status | Yes |
| GET | `/processing/history` | Processing batch history | Yes |

#### Dashboard V2 — `app/api/routes/dashboard_v2.py` (prefix: `/dashboard`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/dashboard/summary` | Period summary (spending, income, categories, trends, budgets) | Yes |
| GET | `/dashboard/spending` | Spending by category | Yes |
| GET | `/dashboard/cashflow` | Monthly cash flow (up to 24 months) | Yes |
| GET | `/dashboard/monthly` | Monthly trends breakdown | Yes |

#### Dashboard Extended — `app/api/routes/dashboard_v2_extended.py` (prefix: `/dashboard`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| GET | `/dashboard/overview` | Full dashboard overview | Yes |
| GET | `/dashboard/analytics` | Dashboard analytics | Yes |
| GET | `/dashboard/budgets` | Budget breakdown with counts | Yes |
| GET | `/dashboard/insights` | AI insights + budget alerts | Yes |
| GET | `/dashboard/notifications` | Paginated notifications | Yes |
| GET | `/dashboard/notifications/unread-count` | Unread notification count | Yes |
| POST | `/dashboard/notifications/{id}/read` | Mark notification read | Yes |
| POST | `/dashboard/notifications/read-all` | Mark all read | Yes |
| GET | `/dashboard/activity` | Activity feed | Yes |
| GET | `/dashboard/widgets` | Specific or all widget data | Yes |

#### Budget Intelligence V2 — `app/api/routes/budget_intelligence_v2.py` (prefix: `/budget-intelligence`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/budget-intelligence/generate` | Generate budget intelligence | Yes |
| POST | `/budget-intelligence/recalculate` | Recalculate intelligence | Yes |
| GET | `/budget-intelligence/current` | Current period intelligence | Yes |
| GET | `/budget-intelligence/recommendations` | AI recommendations | Yes |
| GET | `/budget-intelligence/optimization` | Optimization suggestions | Yes |
| GET | `/budget-intelligence/trends` | Prediction trends | Yes |
| GET | `/budget-intelligence/risk` | Risk assessment | Yes |
| GET | `/budget-intelligence/opportunities` | Savings opportunities | Yes |

#### Health V2 — `app/api/routes/health_v2.py` (prefix: `/health`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/health/calculate` | Calculate health score | Yes |
| POST | `/health/recalculate` | Recalculate health | Yes |
| GET | `/health/current` | Current health metrics | Yes |
| GET | `/health/history` | Historical health scores | Yes |
| GET | `/health/trends` | Trend analysis | Yes |
| GET | `/health/breakdown` | Factor-by-factor breakdown | Yes |
| GET | `/health/recommendations` | Health recommendations | Yes |
| GET | `/health/risk` | Risk assessment | Yes |

#### Copilot — `app/api/routes/copilot_v2.py` (prefix: `/copilot`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/copilot/chat` | Send message, get AI response | Yes |
| GET | `/copilot/sessions` | List chat sessions | Yes |
| GET | `/copilot/sessions/{id}` | Session history with messages | Yes |
| DELETE | `/copilot/sessions` | Delete all sessions | Yes |
| POST | `/copilot/feedback` | Submit message feedback | Yes |
| GET | `/copilot/suggestions` | Get proactive suggestions | Yes |
| GET | `/copilot/settings` | Get LLM settings | No |

#### Goals — `app/api/routes/goal_planning_v2.py` (prefix: `/goals`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/goals` | Create financial goal | Yes |
| PUT | `/goals/{id}` | Update goal | Yes |
| DELETE | `/goals/{id}` | Delete goal | Yes |
| GET | `/goals` | List goals (optional status filter) | Yes |
| GET | `/goals/{id}` | Get single goal | Yes |
| POST | `/goals/analyze` | Analyze goal feasibility | Yes |
| POST | `/goals/recalculate` | Recalculate all goal progress | Yes |
| GET | `/goals/recommendations` | Get goal recommendations | Yes |
| GET | `/goals/progress` | Get goal progress overview | Yes |

#### Receipts OCR — `app/api/routes/receipt_ocr_v2.py` (prefix: `/receipts`)
| Method | Path | Logic | Auth |
|---|---|---|---|
| POST | `/receipts/upload` | Upload receipt image | Yes |
| POST | `/receipts/{id}/process` | Process receipt (OCR + categorization) | Yes |
| POST | `/receipts/{id}/confirm` | Confirm processed receipt & create expense | Yes |
| GET | `/receipts` | List receipts (optional status filter) | Yes |
| GET | `/receipts/{id}` | Get receipt details | Yes |
| PATCH | `/receipts/{id}` | Update receipt data | Yes |
| DELETE | `/receipts/{id}` | Delete receipt | Yes |
| GET | `/receipts/{id}/image` | Get receipt image file | Yes |

#### WebSocket — `app/api/v1/websocket.py`
| Path | Type | Logic |
|---|---|---|
| `/ws` | WebSocket | Generic user channel (token auth) |
| `/ws/dashboard` | WebSocket | Dashboard real-time channel |
| `/ws/dashboard/subscribe` | POST | Subscribe to dashboard events |

#### Root Endpoints
| Path | Method | Logic |
|---|---|---|
| `/` | GET | App info (name, version, environment) |
| `/healthz` | GET | Simple health check |
| `/api/health` | GET | Detailed health (DB ping, ML model status) |
| `/api/{path}` | GET | Legacy redirect to `/api/v1/{path}` |

---

## 4. IMPLEMENTED FEATURES MATRIX

### Fully Functional Modules

| Module | Status | Backend Handler | Frontend UI | End-to-End |
|---|---|---|---|---|
| **User Auth** (register/login/me) | ✅ | `auth.py` | `AuthContext.jsx`, `Login.jsx`, `Register.jsx` | ✅ JWT stored in localStorage |
| **Expense CRUD** | ✅ | `expenses.py` | `Expenses.jsx` | ✅ |
| **Auto-categorization** | ✅ | `ml.py` + `ml_service.py` | Prediction button in Expenses | ✅ |
| **Analytics** (summary, charts) | ✅ | `analytics.py` | `Dashboard.jsx` (legacy) | ✅ |
| **Financial Health Score** | ✅ | `financial_health.py` | Dashboard.jsx (legacy) | ✅ |
| **Recommendations** | ✅ | `recommendations.py` | Dashboard.jsx (legacy) | ✅ |
| **Budgets CRUD + Status** | ✅ | `budgets.py` | `Budgets.jsx` | ✅ |
| **Budget Suggestions** | ✅ | `budget_suggestion.py` | `BudgetOptimizer.jsx` | ✅ |
| **Subscription Tracking** | ✅ | `subscriptions.py` | `Subscriptions.jsx` | ✅ |
| **Recurring Expenses** | ✅ | `recurring.py` | `Recurring.jsx` | ✅ |
| **Spending Anomaly Detection** | ✅ | `anomaly.py` | `Anomaly.jsx` | ✅ |
| **Reports (weekly/monthly)** | ✅ | `reports.py` | `Reports.jsx` | ✅ |
| **Alerts** | ✅ | `alerts.py` | Via notification store | ✅ |
| **Bank Connection (Mock)** | ✅ | `bank.py` + `mock_provider.py` | `ConnectBank.jsx` → Consent → Accounts | ✅ |
| **Consent Management** | ✅ | `consent.py` + `consent_grant_service.py` | `ConsentPage.jsx` | ✅ |
| **Import Preferences** | ✅ | `import_preference.py` | `ImportPreference.jsx` | ✅ |
| **Data Sync** | ✅ | `sync.py` + `sync_service.py` | `Sync.jsx`, `SyncHistory.jsx`, `SyncStatus.jsx` | ✅ |
| **Dashboard V2** (overview, analytics, budgets, insights) | ✅ | `dashboard_v2.py` + `dashboard_v2_extended.py` | `/app/dashboard/*` (7 pages) | ✅ |
| **Notifications** | ✅ | `dashboard_v2_extended.py` | `NotificationsPage.jsx`, `AlertBell.jsx` | ✅ |
| **Budget Intelligence V2** | ✅ | `budget_intelligence_v2.py` | `/app/budget-intelligence/*` (5 pages) | ✅ |
| **Financial Health V2** | ✅ | `health_v2.py` + `financial_health_service.py` | `/app/health/*` (5 pages) | ✅ |
| **AI Copilot** (chat, RAG, memory) | ✅ | `copilot_v2.py` + `copilot_service.py` | `/app/copilot/*` (4 pages) | ✅ |
| **Goal Planning** (CRUD + progress + recs) | ✅ | `goal_planning_v2.py` | `/app/goals/*` (7 pages) | ✅ |
| **Receipt OCR** (upload, process, confirm) | ✅ | `receipt_ocr_v2.py` + `receipt_service.py` | `/app/receipts/*` (4 pages) | ✅ |
| **WebSocket Realtime** | ✅ | `websocket.py` + `manager.py` | `useWebSocket.js` | ✅ (ping/pong) |

### ML/AI Pipeline (Intelligence Engine)

| Component | Status | Notes |
|---|---|---|
| `ProcessingPipeline` | ✅ | Merchant normalization, category prediction, confidence scoring, recurring detection, income classification, validation |
| `ExpenseCategorizer` (scikit-learn) | ✅ | LogisticRegression model at `backend/app/ml/expense_classifier.joblib` |
| Keyword Fallback | ✅ | When model absent + `ML_ALLOW_FALLBACK=true` |
| RAG (FAISS + HuggingFace) | ✅ | `RAGService` with `all-MiniLM-L6-v2` embeddings |
| LLM (GPT-4o via LangChain) | ✅ | `LLMService` with token counting, tool binding |
| MongoDB Indexes (47 indexes) | ✅ | All collections indexed at startup in `mongodb.py` |

---

## 5. BROKEN PIPELINES, DEAD ROUTES & TECHNICAL DEBT

~~### CRITICAL: Broken Frontend Build~~ ✅ FIXED

~~- Webpack entry `./src/main.jsx` now exists at `frontend/src/main.jsx`~~
~~- Root `main.jsx.old` / `main.jsx.archived` removed — only `frontend/src/main.jsx` is active~~
~~- `npm run dev` and `npm run build` work correctly~~

~~### CRITICAL: Double-Prefixed API URLs (401 errors)~~ ✅ FIXED

~~- `bank.js`, `consent.js`, `importPreference.js` no longer hardcode `/api/v1/` prefix~~
~~- `api/client.js` sets `baseURL: http://localhost:8080/api/v1` so all calls resolve correctly~~

### CRITICAL: Dual Dashboard Confusion (V1 vs V2)

| Issue | Severity | Details |
|---|---|---|
| **Two competing dashboards** | 🟠 HIGH | `/app` → uses `Dashboard.jsx` (legacy V1 with `/analytics/*`, `/financial-health/score`, `/recommendations`). `/app/dashboard` → uses `DashboardLayout` (V2 with `/dashboard/*` routes). Both active simultaneously, confusing UX. |
| **Two data loading paths** | 🟠 HIGH | `Dashboard.jsx` fetches via direct `api.get()` calls. `dashboardV2Store` fetches via `dashboardV2Api`. Same data, different endpoints, potential inconsistency. |

~~### MODERATE: Missing ML Model at Startup~~ ✅ FIXED

~~- Model file `backend/app/ml/expense_classifier.joblib` exists and is loaded by `ExpenseCategorizer.load()`~~
~~- `categorizer.load()` in `main.py:32` logs a warning (not crash) if model is missing, then falls back to keyword matching~~
~~- `ML_ALLOW_FALLBACK=true` env var controls fallback behavior~~

### MODERATE: Inconsistent Frontend Entry Points

| File | Issue |
|---|---|
| `D:\1. PLACEMENT\IntelliMoney\main.jsx` | Root-level entry with relative imports designed for running from project root |
| `frontend/src/` (no `main.jsx`) | Webpack expects `./src/main.jsx` from `frontend/` — **file doesn't exist** |
| `frontend/webpack.config.js:53-56` | `DefinePlugin` injects `process.env.API_BASE_URL` but frontend `.env` only sets `API_BASE_URL` for local dev — Vercel build uses webpack DefinePlugin |
| `frontend/webpack.config.js:68-73` | Dev proxy on `/api` targets `localhost:8080` but frontend's `api/client.js` uses `/api/v1` base URL — double-path for proxied requests |

### MODERATE: RAG Pipeline Ephemeral State

| File | Lines | Issue |
|---|---|---|
| `backend/app/copilot/services/rag_service.py` | 26, 39-42 | FAISS vector store is **in-memory only** (`self._vector_store`). Every server restart loses all indexed documents. No persistence to disk or MongoDB. |
| `backend/app/copilot/services/rag_service.py` | 18-20 | `HuggingFaceEmbeddings` is synchronous but `FAISS.afrom_documents` is async — potential blocking on event loop. |

~~### MODERATE: Missing Auth on Copilot Settings~~ ✅ FIXED

~~- `GET /copilot/settings` now requires authentication~~

### MODERATE: WebSocket Token in URL

| File | Lines | Issue |
|---|---|---|
| `frontend/src/hooks/useWebSocket.js` | 15 | Token passed as query param `?token=${token}` in WebSocket URL. Token is logged/visible in browser network tab. Should use WebSocket auth handshake instead. |
| `backend/app/infrastructure/websocket/auth.py` | (exists) | Validates token from query params — design is intentional but leaks token in URLs/logs. |

### LOW: Unused/Redundant Endpoints

| Endpoint | Reason |
|---|---|
| `POST /intelligence/reprocess` in `intelligence.py:42-53` | Identical logic to `POST /intelligence/process`. Same function called with same parameters. Dead code. |
| `POST /health/recalculate` | Logic identical to `POST /health/calculate` in `health_v2.py`. No behavioral difference. |
| `POST /budget-intelligence/recalculate` | Same as `POST /budget-intelligence/generate`. Unnecessary duplication. |
| `POST /goals/recalculate` | Same as internal recalculation logic. |
| `GET /api/{path}` legacy redirect | Catches all non-v1 paths and redirects to v1. Generic pattern could mask 404s. |
| `POST /ws/dashboard/subscribe` | Posts to a WebSocket route — unusual design. Calls `gateway.subscribe_to_events()` with no await. |

### LOW: WebSocket Ping/Pong Only

| File | Lines | Issue |
|---|---|---|
| `backend/app/api/v1/websocket.py` | 27-29 | Both `/ws` and `/ws/dashboard` only respond to "ping" with "pong". No real-time event pushing is implemented. The `connection_manager` and `DashboardGateway` exist but aren't used for data streaming. |
| `frontend/src/hooks/useWebSocket.js` | 26-33 | `onMessage` handler is never wired to any store. `dashboardV2Store.applyLiveUpdate` exists but is never called by the WebSocket hook. |

### LOW: Hardcoded Values / Tech Debt

| File | Lines | Issue |
|---|---|---|
| `backend/app/api/deps.py` | 12 | `tokenUrl` hardcoded to `/api/v1/auth/login` — should use config |
| `frontend/src/api/bank.js` | 4-8 | Uses `/api/v1/` hardcoded prefix |
| `backend/start.py` | 5 | Hardcoded fallback port 8080 |
| `backend/app/core/config.py` | 30 | CORS origins hardcoded list includes `localhost:80` |
| `frontend/src/utils/` | (assumed) | Format utilities — not verified; may lack proper currency formatting |
| `backend/app/receipt_ocr/` | (module) | OCR service depends on system-installed Tesseract — not in Dockerfile |
| `ml/data/expenses.csv` | (data file) | Training data not checked — if missing or small, model accuracy is poor |

### LOW: Excessive MongoDB Indexes

| Issue | Detail |
|---|---|
| 47 `create_index` calls in `mongodb.py` | Many indexes may be unnecessary, adding write overhead. `financial_health_history` has both `(user_id, calculated_at)` and `(user_id, period)` unique — period is unique per user so this is redundant. Same pattern for multiple collections. |

### LOW: Stale `package.json` Dependencies

| Dependency | Version | Notes |
|---|---|---|
| `webpack-dev-server` | `^4.15.1` | End-of-life; v4 has known security issues. Should migrate to v5 or Vite. |
| Missing `react-scripts` or Vite | — | No Vite config; pure Webpack 5 is verbose for SPA |
| Missing `@tanstack/react-query` | — | No declarative data fetching library; custom `useApi` hook is basic |

~~### LOW: No Database Seeds for New Modules~~ ✅ FIXED

~~- `backend/scripts/seed_demo.py` now seeds ALL modules: expenses, budgets, bank accounts, financial transactions, goals, goal progress, budget intelligence, financial health (with 6-month history), notifications, and receipts~~

### CRITICAL SUMMARY

| Severity | Count | Key Items |
|---|---|---|
| 🔴 BLOCKER | 3 | Missing webpack entry point, broken main.jsx imports, double-prefixed API URLs |
| 🟠 HIGH | 3 | Dual dashboard confusion, ML model missing at startup, inconsistent frontend entry |
| 🟡 MODERATE | 5 | Ephemeral RAG state, copilot settings unauthenticated, WebSocket token in URL, redundant endpoints, broken Docker build |
| 🟢 LOW | 7 | Ping-only websockets, hardcoded values, excessive indexes, stale deps, missing seeds |

**Recommended immediate actions:**
1. Fix webpack `entry` to point to root `main.jsx` OR create proper `frontend/src/main.jsx`
2. Fix root `main.jsx` imports to use correct relative paths
3. Remove hardcoded `/api/v1/` prefix from `bank.js`, `consent.js`, `importPreference.js`
4. Unify Dashboard V1 → V2 migration (redirect `/app` → `/app/dashboard`)
5. Ensure ML model is trained or set `ML_ALLOW_FALLBACK=true` in `.env`
