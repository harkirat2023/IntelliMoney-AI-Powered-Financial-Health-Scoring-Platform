# IntelliMoney — Startup Guide

## Quick Start

```bash
# 1. Backend
cd backend
cp .env.example .env    # edit with your keys
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev             # starts on http://localhost:5173

# 3. Open http://localhost:5173
```

### Docker (if preferred)

```bash
./start.sh
# or manually: docker compose up --build -d
# Frontend: http://localhost:3002
# Backend:  http://localhost:8080/api/v1
# Health:   http://localhost:8080/healthz
```

### Seed Demo Data

```bash
docker compose --profile with-seed run seed
# or directly: cd backend && python seed_demo.py
```

---

## Architecture Overview

```
Frontend (React 19, React Router 7)
  ↕ HTTP (axios → /api/v1/*)
  ↕ WebSocket (real-time updates)
Nginx (reverse-proxy, only in Docker)
  ↕
Backend (FastAPI, Python 3.12)
  ↕
MongoDB 7 ← Redis 7 (optional, for caching)
```

**Frontend**: React SPA at `frontend/`. No SSR. All pages lazy-loaded via `React.lazy()`.

**Backend**: FastAPI app at `backend/app/main.py`. Routes registered under `/api/v1/`. WebSocket at `/api/v1/ws`.

---

## Page → API Route Mapping

### Landing Pages (No API calls — static HTML)

| Page | Route | File |
|------|-------|------|
| Home | `/` | `landing/pages/HomePage.jsx` |
| Features | `/features` | `landing/pages/FeaturesPage.jsx` |
| About | `/about` | `landing/pages/AboutPage.jsx` |
| Contact | `/contact` | `landing/pages/ContactPage.jsx` |
| Privacy | `/privacy` | `landing/pages/PrivacyPage.jsx` |
| Terms | `/terms` | `landing/pages/TermsPage.jsx` |

### Auth

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Login | `/login` | `POST /auth/login` | `routes/auth.py` |
| Register | `/register` | `POST /auth/register` | `routes/auth.py` |
| AuthContext (global) | — | `GET /auth/me`, `POST /auth/refresh` | `routes/auth.py` |

### Dashboard (all under `/app/dashboard`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Overview | `/app/dashboard` | `GET /dashboard/overview` | `routes/dashboard_v2.py` |
| Analytics | `/app/dashboard/analytics` | `GET /dashboard/analytics` | `routes/dashboard_v2.py` |
| Spending | `/app/dashboard/spending` | `GET /dashboard/overview`, `GET /dashboard/widgets` | `routes/dashboard_v2.py` |
| Cash Flow | `/app/dashboard/cashflow` | `GET /dashboard/overview`, `GET /dashboard/cashflow` | `routes/dashboard_v2.py` |
| Budgets | `/app/dashboard/budgets` | `GET /dashboard/budgets` | `routes/dashboard_v2.py` |
| Insights | `/app/dashboard/insights` | `GET /dashboard/insights` | `routes/dashboard_v2.py` |
| Notifications | `/app/dashboard/notifications` | `GET /dashboard/notifications`, `GET /dashboard/notifications/unread-count`, `POST /dashboard/notifications/{id}/read`, `POST /dashboard/notifications/read-all` | `routes/dashboard_v2.py` |

### Core Modules (all under `/app`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Expenses | `/app/expenses` | `GET /expenses`, `POST /expenses`, `PUT /expenses/{id}`, `DELETE /expenses/{id}`, `POST /ml/categorize` | `routes/expenses.py`, `routes/ml.py` |
| Budgets | `/app/budgets` | `GET /budgets`, `GET /budgets/status`, `POST /budgets`, `PUT /budgets/{id}`, `DELETE /budgets/{id}`, `GET /alerts` | `routes/budgets.py`, `routes/alerts.py` |
| Budget Optimizer | `/app/budget-optimizer` | `GET /budget-suggestions`, `GET /budget-suggestions/optimization-report`, `POST /budget-suggestions/generate`, `POST /budget-suggestions/{id}/apply`, `DELETE /budget-suggestions/{id}` | `routes/budget_suggestion.py` |
| Reports | `/app/reports` | `GET /reports`, `GET /reports/summary`, `POST /reports/generate/weekly`, `POST /reports/generate/monthly`, `PATCH /reports/{id}/read` | `routes/reports.py` |
| Recurring | `/app/recurring` | `GET /recurring`, `POST /recurring`, `PUT /recurring/{id}`, `DELETE /recurring/{id}`, `GET /recurring/upcoming`, `GET /recurring/suggestions/detect` | `routes/recurring.py` |
| Subscriptions | `/app/subscriptions` | `GET /subscriptions`, `POST /subscriptions`, `PUT /subscriptions/{id}`, `DELETE /subscriptions/{id}`, `GET /subscriptions/suggestions/detect`, `GET /subscriptions/insights`, `POST /subscriptions/{id}/record-payment` | `routes/subscriptions.py` |
| Anomaly Detection | `/app/anomaly` | `GET /anomaly`, `GET /anomaly/alerts`, `GET /anomaly/weekly-report`, `POST /anomaly/detect`, `PATCH /anomaly/{id}/read` | `routes/anomaly.py` |
| Bank Accounts | `/app/bank-accounts` | `GET /bank/accounts`, `GET /bank/status`, `DELETE /bank/disconnect/{id}` | `routes/bank.py` |
| Sync | `/app/sync` | `GET /bank/accounts`, `GET /sync/status`, `POST /sync/start`, `POST /sync/manual` | `routes/sync.py`, `routes/bank.py` |
| Sync History | `/app/sync/history` | `GET /bank/accounts`, `GET /sync/history`, `POST /sync/retry` | `routes/sync.py`, `routes/bank.py` |
| Sync Status | `/app/sync/status` | `GET /sync/status`, `GET /sync/history`, `POST /sync/start` | `routes/sync.py` |

### Bank Connect Flow (public routes, no auth required)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Connect Bank | `/connect-bank` | `POST /bank/connect` | `routes/bank.py` |
| Consent | `/connect-bank/consent` | `POST /bank/consent` | `routes/bank.py` |
| Success | `/connect-bank/success` | `GET /bank/accounts` | `routes/bank.py` |
| Manage | `/connect-bank/manage` | `GET /bank/accounts`, `GET /bank/status`, `DELETE /bank/disconnect/{id}` | `routes/bank.py` |
| Import Preference | `/connect-bank/import-preference` | — (navigates to review) | — |
| Review | `/connect-bank/review` | `POST /consent/grant`, `POST /import-preference/` | `routes/consent.py`, `routes/import_preference.py` |
| Complete | `/connect-bank/complete` | `GET /bank/accounts` | `routes/bank.py` |

### Health (all under `/app/health`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Overview | `/app/health` | `POST /health/calculate`, `POST /health/recalculate`, `GET /health/current`, `GET /health/history`, `GET /health/trends`, `GET /health/breakdown`, `GET /health/recommendations`, `GET /health/risk` | `routes/health_v2.py` |
| History | `/app/health/history` | `GET /health/history` | `routes/health_v2.py` |
| Trends | `/app/health/trends` | `GET /health/trends`, `GET /health/current` | `routes/health_v2.py` |
| Risk | `/app/health/risk` | `GET /health/risk`, `GET /health/current`, `GET /health/breakdown` | `routes/health_v2.py` |
| Recommendations | `/app/health/recommendations` | `GET /health/recommendations` | `routes/health_v2.py` |

### Budget Intelligence (all under `/app/budget-intelligence`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Overview | `/app/budget-intelligence` | `POST /budget-intelligence/generate`, `POST /budget-intelligence/recalculate`, `GET /budget-intelligence/current`, `GET /budget-intelligence/recommendations`, `GET /budget-intelligence/optimization`, `GET /budget-intelligence/trends`, `GET /budget-intelligence/risk`, `GET /budget-intelligence/opportunities` | `routes/budget_intelligence_v2.py` |
| Recommendations | `/app/budget-intelligence/recommendations` | `GET /budget-intelligence/recommendations` | `routes/budget_intelligence_v2.py` |
| Optimization | `/app/budget-intelligence/optimization` | `GET /budget-intelligence/optimization` | `routes/budget_intelligence_v2.py` |
| Trends | `/app/budget-intelligence/trends` | `GET /budget-intelligence/trends`, `GET /budget-intelligence/risk` | `routes/budget_intelligence_v2.py` |
| Opportunities | `/app/budget-intelligence/opportunities` | `GET /budget-intelligence/opportunities` | `routes/budget_intelligence_v2.py` |

### AI Copilot (all under `/app/copilot`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Chat | `/app/copilot` | `POST /copilot/chat`, `GET /copilot/suggestions` | `routes/copilot_v2.py` |
| History | `/app/copilot/history` | `GET /copilot/sessions`, `DELETE /copilot/sessions` | `routes/copilot_v2.py` |
| History Detail | `/app/copilot/history/:sessionId` | `GET /copilot/sessions/{sessionId}` | `routes/copilot_v2.py` |
| Settings | `/app/copilot/settings` | `GET /copilot/settings` | `routes/copilot_v2.py` |

### Goals (all under `/app/goals`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Overview | `/app/goals` | `GET /goals`, `POST /goals/recalculate` | `routes/goal_planning_v2.py` |
| Create | `/app/goals/create` | `POST /goals/analyze`, `POST /goals` | `routes/goal_planning_v2.py` |
| Detail | `/app/goals/:goalId` | `GET /goals/{goalId}`, `PUT /goals/{goalId}`, `DELETE /goals/{goalId}` | `routes/goal_planning_v2.py` |
| Progress | `/app/goals/progress` | `GET /goals/progress` | `routes/goal_planning_v2.py` |
| History | `/app/goals/history` | `GET /goals` | `routes/goal_planning_v2.py` |
| Recommendations | `/app/goals/recommendations` | `GET /goals/recommendations` | `routes/goal_planning_v2.py` |

### Receipts / OCR (all under `/app/receipts`)

| Page | Route | API Calls | Backend File |
|------|-------|-----------|-------------|
| Overview | `/app/receipts` | `GET /receipts`, `GET /receipts/{id}/image` | `routes/receipt_ocr_v2.py` |
| Upload | `/app/receipts/upload` | `POST /receipts/upload` | `routes/receipt_ocr_v2.py` |
| Review | `/app/receipts/review` | `GET /receipts/{id}`, `POST /receipts/{id}/process`, `POST /receipts/{id}/confirm`, `PATCH /receipts/{id}`, `GET /receipts/{id}/image` | `routes/receipt_ocr_v2.py` |
| History | `/app/receipts/history` | `GET /receipts`, `DELETE /receipts/{id}`, `GET /receipts/{id}/image` | `routes/receipt_ocr_v2.py` |

---

## How Each Feature Works

### Auth (`/auth`)
- **Login**: Validates email + password against MongoDB `users` collection. Returns JWT access token (24h) + refresh token (7d).
- **Register**: Creates user in MongoDB with hashed password. Returns tokens.
- **Refresh**: Validates refresh token, issues new access + refresh tokens (rotation).
- **Rate limiting**: In-memory, 10 req/min per IP on login/register.
- **Auto-refresh**: Frontend axios interceptor catches 401, calls `/auth/refresh`, retries queued requests.

### Dashboard (`/dashboard`)
- **Overview**: Aggregates health score, spending, income, savings, cash flow, budget status, recent transactions, recurring, subscriptions, upcoming bills, AI insights, budget alerts, top categories, monthly trend, spending heatmap, and activity feed — all in one response from `DashboardService.get_overview()`.
- **Analytics**: Computes total spending/income, net savings, savings rate, daily average, busiest day, top merchants, category breakdown, monthly trend, budget overview.
- **Cash Flow**: Returns per-month income, expenses, and net cash flow for the last N months.
- **Widgets**: Modular widget data (spending heatmap, top categories, etc.).
- **Notifications**: CRUD for in-app notifications with read/unread tracking.
- **Real-time updates**: WebSocket at `/api/v1/ws/dashboard` pushes `dashboard.updated` and `notification.created` events.

### Expenses (`/expenses`)
- CRUD operations on MongoDB `expenses` collection.
- Category prediction via `/ml/categorize` using local scikit-learn model (falls back to keyword matching).
- Supports filters: category, date range, search query, pagination.

### Budgets (`/budgets`)
- CRUD operations. Each budget has category, monthly limit, year/month.
- `/budgets/status` computes per-category spent/remaining/percentage_used from expenses.
- `/alerts` returns budget threshold alerts.

### Budget Optimizer (`/budget-suggestions`)
- Suggests optimal budget limits based on spending history.
- Optimization report: analyzes all budgets and suggests adjustments.
- Generate endpoint triggers a fresh analysis pass.

### Reports (`/reports`)
- Generates weekly/monthly financial reports as MongoDB documents.
- Each report contains: total spending/income, net savings, savings rate, category breakdown, top expenses, budget performance, health score, insights, and recommendations.
- Insights are rule-based (savings rate thresholds, budget status, spending trends).

### Recurring Expenses (`/recurring`)
- Tracks recurring expenses with expected dates and frequency.
- `/upcoming` lists expenses due within N days.
- `/suggestions/detect` uses ML/rule-based detection of recurring patterns in transaction history.

### Subscriptions (`/subscriptions`)
- Tracks subscriptions with billing frequency and payment dates.
- `/suggestions/detect` identifies subscription-like recurring payments.
- `/insights` provides subscription spending analysis.
- `/record-payment` logs individual payments against a subscription.

### Bank Connection (`/bank`)
- Simulated bank provider flow (MockBankProvider):
  1. `POST /connect` — initiates with provider, returns redirect URL
  2. `POST /consent` — submits consent and fetches accounts
  3. `GET /accounts` — lists linked bank accounts
  4. `DELETE /disconnect/{id}` — removes account link
- Consent management with expiry tracking and revocation support.
- Import preferences control auto-import behavior per account.

### Data Sync (`/sync`)
- Manually triggered sync pipeline:
  1. Calls bank provider API for new transactions
  2. Stores raw bank transactions in `bank_transactions`
  3. Creates financial transactions with normalized merchants
  4. Runs categorization (ML model or keyword fallback)
  5. Detects recurring patterns
  6. Updates dashboard metrics
- Supports per-account and bulk sync.
- Status polling and retry for failed syncs.

### Health Score (`/health`)
- **Financial Health Score**: Weighted 10-factor model (savings rate 20%, budget adherence 15%, cash flow stability 15%, expense stability 10%, income consistency 10%, emergency fund 10%, recurring ratio 5%, essential spending 10%, debt readiness 2.5%, investment readiness 2.5%).
- **Calculate**: Pulls 6 months of data, computes all factors, stores result.
- **History**: Returns previous scores over time.
- **Trends**: Direction analysis (improving/stable/declining) with volatility.
- **Breakdown**: Per-factor component scores.
- **Risk Assessment**: Threshold-based risk for each factor.
- **Recommendations**: Rule-based (if savings_rate < 30%, recommend saving more, etc.).

### Budget Intelligence (`/budget-intelligence`)
- **Generate**: Analyzes all budgets and spending, produces budget score (0-100 weighted), per-category status (on-track/warning/over), trend direction, suggested limits.
- **Limits**: Rule-based — essential categories get closer to actual spend, discretionary get tighter caps.
- **Forecasting**: Simple trend extrapolation using month-over-month averages (not ML).
- **Optimization**: Suggests limit adjustments with confidence scores.
- **Risk**: Weighted risk formula based on usage %, volatility, and MoM change.
- **Opportunities**: Detects savings opportunities (overspending, unused subscriptions, etc.).
- **Recommendations**: Rule-based based on utilization, category type, and health score.

### AI Copilot (`/copilot`)
- **LLM**: Groq (default `llama3-8b-8192`) via `langchain-groq`.
- **Tools**: 11 MongoDB-backed tools (health check, budget, expenses, cash flow, etc.) — LLM can query live data.
- **RAG**: Local embeddings (`all-MiniLM-L6-v2`) + FAISS for conversation context retrieval.
- **Memory**: Conversation history stored per session. Auto-summarized when >3000 tokens.
- **Suggestions**: Rule-based suggestions based on health score and spending patterns.
- **Prompt injection protection**: Regex-based detection.

### Goals (`/goals`)
- CRUD for financial goals with target amounts and deadlines.
- **Analyze**: Feasibility check against income and spending.
- **Progress**: Tracks goal achievement over time with projections.
- **Recommendations**: Based on goal type and progress status.

### Receipts / OCR (`/receipts`)
- **Upload**: Accepts image files, stores to disk.
- **OCR Pipeline**: Image preprocessing (OpenCV) → Tesseract OCR → Rule-based extraction (merchant, amount, date, time, currency) → ML categorization.
- **Process**: Runs the full OCR pipeline on a stored receipt.
- **Confirm**: Marks receipt as confirmed, optionally creates expense.
- **Validation**: Image format, MIME type, size, and extracted data quality checks.

### Anomaly Detection (`/anomaly`)
- **Detect**: Compares recent 7-day expenses against 90-day historical averages per category.
- If deviation > threshold, stores anomaly with severity (low/medium/high/critical).
- **Weekly report**: Aggregate of current week vs previous week with insights.
- Deduplication: Skips anomalies already recorded for same expense.

---

## Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (required) | JWT signing secret |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB` | `intellimoney` | Database name |
| `REDIS_URL` | (empty) | Optional Redis for caching |
| `GROQ_API_KEY` | (required for Copilot) | Groq API key |
| `GROQ_MODEL` | `llama3-8b-8192` | LLM model |
| `BANK_ENCRYPTION_KEY` | (required) | Fernet key for bank data |
| `CORS_ORIGINS` | localhost origins | Allowed CORS origins |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `SMTP_HOST` | (empty) | SMTP server for emails |
| `SMTP_USER` | (empty) | SMTP username |
| `SMTP_PASSWORD` | (empty) | SMTP password |
| `SMTP_FROM_EMAIL` | (empty) | From address |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 (24h) | JWT access token TTL |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | 10080 (7d) | JWT refresh token TTL |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, React Router 7, Axios, Lucide Icons |
| State Management | Custom pub/sub stores (no Redux/Zustand) |
| Bundling | Webpack 5 with code splitting (React.lazy) |
| Styling | Tailwind CSS 3 + custom CSS (`.page`, `.panel`, glass UI) |
| Backend | Python 3.12, FastAPI, Motor (async MongoDB) |
| LLM | Groq (via langchain-groq) |
| ML | scikit-learn (expense classifier) + sentence-transformers (RAG) |
| OCR | Tesseract + OpenCV |
| Database | MongoDB 7 |
| Cache | Redis 7 (optional) |
| Auth | JWT (access + refresh tokens), bcrypt |
| Rate Limiting | In-memory (10 req/min per IP on auth) |
| Container | Docker, docker-compose |
| Proxy | Nginx (in Docker) |
