# IntelliMoney — Whiteboard System Architecture

> **Interview-Ready Architecture Document** — Draw this on a whiteboard in 5 minutes

---

## 1. HIGH-LEVEL ARCHITECTURE (30-second overview)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER                                             │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Tailwind)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Clerk     │  │  Dashboard  │  │  AI Copilot │  │  AA Sandbox │        │
│  │   Auth      │  │  (V2)       │  │  (Chat UI)  │  │  (Demo)     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTPS / REST API
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI + Python)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Auth      │  │  Domain     │  │   Agent     │  │   AA        │        │
│  │  Middleware │  │  Services   │  │  (LangChain)│  │  Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                │                │
│         └────────────────┼────────────────┼────────────────┘                │
│                          ▼                                                │
│              ┌─────────────────────┐                                      │
│              │   Repositories      │                                      │
│              └─────────┬───────────┘                                      │
└────────────────────────┼──────────────────────────────────────────────────┘
                         │ MongoDB Driver
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │expenses │ │budgets  │ │ goals   │ │recurring│ │subscriptions│ ...   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
           ┌───────────────┐           ┌───────────────┐
           │     GROQ      │           │   SETU AA     │
           │   (LLM API)   │           │  SANDBOX API  │
           └───────────────┘           └───────────────┘
```

---

## 2. REQUEST LIFECYCLE (Draw this flow)

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ React   │────▶│  Clerk  │────▶│  API    │────▶│ FastAPI │────▶│  Mongo  │
│Component│     │  Auth   │     │ Client  │     │ Router  │     │   DB    │
└─────────┘     └─────────┘     └─────────┘     └────┬────┘     └─────────┘
                                                     │
                    ┌────────────────────────────────┘
                    ▼
           ┌─────────────────┐
           │  Auth Middleware│  (Validates Clerk JWT)
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Service Layer  │  (Business Logic)
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │ Repository Layer│  (Data Access)
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │     MongoDB     │
           └─────────────────┘
```

---

## 3. AI COPILOT ARCHITECTURE (The "Agentic" Flow)

```
USER MESSAGE
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│                    AGENT COPILOT SERVICE                        │
│  (LangChain Agent Loop - max 8 tool iterations)                │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  SYSTEM     │    │   USER      │    │   TOOL      │        │
│  │  PROMPT     │───▶│   CONTEXT   │───▶│   CALLS     │        │
│  └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                               │                │
│                                               ▼                │
│                                    ┌─────────────────────┐     │
│                                    │  TYPED FINANCIAL    │     │
│                                    │  TOOLS (Read/Calc)  │     │
│                                    │  • get_expenses     │     │
│                                    │  • get_budgets      │     │
│                                    │  • calculate_health │     │
│                                    │  • list_goals       │     │
│                                    │  • detect_anomalies │     │
│                                    │  • get_aa_status    │     │
│                                    │  • categorize       │     │
│                                    │  • propose_actions  │     │
│                                    └──────────┬──────────┘     │
│                                               │                │
│                                               ▼                │
│                                    ┌─────────────────────┐     │
│                                    │  DETERMINISTIC      │     │
│                                    │  DOMAIN SERVICES    │     │
│                                    │  • FinancialHealth  │     │
│                                    │  • BudgetIntelligence│    │
│                                    │  • GoalPlanning     │     │
│                                    │  • AnomalyService   │     │
│                                    └──────────┬──────────┘     │
│                                               │                │
│                                               ▼                │
│                                    ┌─────────────────────┐     │
│                                    │  REPOSITORIES       │     │
│                                    │  • MongoDB          │     │
│                                    └─────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
     │
     ▼
FINAL ANSWER + PROPOSAL (if write action requested)
```

### Agent Tool Categories

```
┌────────────────────────────────────────────────────────────────┐
│                      AGENT TOOLS                                │
├─────────────────────────┬───────────────────────────────────────┤
│      READ TOOLS         │           CALCULATION TOOLS           │
│  (Execute immediately)  │   (Execute immediately)               │
├─────────────────────────┼───────────────────────────────────────┤
│ • get_income            │ • calculate_health                    │
│ • get_expenses          │ • get_health_factors                  │
│ • search_expenses       │ • get_budget_intelligence             │
│ • summarize_spending    │ • get_spending_report                 │
│ • get_spending_by_*     │ • get_cashflow_report                 │
│ • list_budgets          │ • detect_anomalies                    │
│ • get_budget_usage      │ • calculate_remaining (deterministic) │
│ • list_goals            │ • categorize (deterministic)          │
│ • get_goal_progress     │                                       │
│ • list_recurring_expenses│                                        │
│ • list_subscriptions    │                                       │
│ • list_notifications    │                                       │
│ • list_accounts         │                                       │
│ • get_aa_status         │                                       │
├─────────────────────────┼───────────────────────────────────────┤
│      WRITE TOOL         │                                       │
│  (Requires confirmation)│                                       │
├─────────────────────────┼───────────────────────────────────────┤
│ • propose_actions       │  Stores proposal → User confirms →   │
│                         │  Backend executes via separate API    │
└─────────────────────────┴───────────────────────────────────────┘
```

### Mutation Flow (Critical for Interview)

```
USER: "Create a budget for food: ₹5000"

     │
     ▼
┌──────────────────────────────────────────┐
│  AGENT UNDERSTANDS INTENT                │
│  → Calls propose_actions tool            │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  PROPOSE_ACTIONS TOOL                    │
│  • Validates params                      │
│  • Checks ownership                      │
│  • Stores Proposal in MongoDB            │
│  • Returns proposal_id                   │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  AGENT RETURNS TO USER                   │
│  "I'll create a food budget of ₹5000.    │
│   Confirm to proceed?"                   │
└──────────────────────────────────────────┘
     │
     ▼
USER: "Yes, confirm"

     │
     ▼
┌──────────────────────────────────────────┐
│  FRONTEND CALLS: POST /copilot/proposals/│
│  {proposal_id}/confirm                   │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  BACKEND EXECUTES PROPOSAL               │
│  • Validates ownership again             │
│  • Calls domain service                  │
│  • Updates MongoDB                       │
│  • Marks proposal EXECUTED               │
└──────────────────────────────────────────┘
     │
     ▼
UI REFRESHES → Dashboard shows new budget
```

---

## 4. FINANCIAL DATA PIPELINE (The "Money Flow")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FINANCIAL DATA SOURCES                               │
├─────────────────────────────┬───────────────────────────────────────────────┤
│      MANUAL ENTRY           │         SETU AA SANDBOX (DEMO)                │
│  ┌─────────────────────┐    │  ┌─────────────────────────────────────┐     │
│  │ User adds expense   │    │  │ 1. Create Consent                   │     │
│  │ via UI or Copilot   │    │  │ 2. User Approves (sandbox)          │     │
│  │ • Amount            │    │  │ 3. Create Data Session              │     │
│  │ • Description       │    │  │ 4. Fetch FI Data (mock)             │     │
│  │ • Category (AI)     │    │  │ 5. Normalize → Standard Transaction │     │
│  │ • Date              │    │  │ 6. Import into Expenses Collection  │     │
│  └──────────┬───────────┘    │  └─────────────────────────────────────┘     │
└─────────────┼────────────────┘                    │                       │
              │                                     │                       │
              └──────────────┬──────────────────────┘                       │
                             ▼                                              │
              ┌─────────────────────────────┐                               │
              │   NORMALIZED TRANSACTION    │                               │
              │   (Standard Internal Model) │                               │
              └──────────────┬──────────────┘                               │
                             │                                              │
                             ▼                                              │
              ┌─────────────────────────────┐                               │
              │  DETERMINISTIC DOMAIN       │                               │
              │  SERVICES (Source of Truth) │                               │
              │  • Categorization           │                               │
              │  • Budget Calculations      │                               │
              │  • Financial Health (0-100) │                               │
              │  • Cash Flow                │                               │
              │  • Anomaly Detection        │                               │
              │  • Goal Progress            │                               │
              └──────────────┬──────────────┘                               │
                             │                                              │
              ┌──────────────┼──────────────┐                               │
              ▼              ▼              ▼                               │
       ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
       │Budgets   │  │Financial │  │ Reports  │                            │
       │          │  │Health    │  │/Analytics│                            │
       └──────────┘  └──────────┘  └──────────┘                            │
              │              │              │                               │
              └──────────────┼──────────────┘                               │
                             ▼                                              │
                    ┌──────────────────┐                                    │
                    │   AI COPILOT     │                                    │
                    │  (Reads results, │                                    │
                    │   explains,     │                                    │
                    │   proposes)     │                                    │
                    └──────────────────┘                                    │
                             │                                              │
                             ▼                                              │
                    ┌──────────────────┐                                    │
                    │   DASHBOARD UI   │                                    │
                    │  (Visualizes all)│                                    │
                    └──────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. DATABASE SCHEMA (Key Collections)

```
MONGODB DATABASE: intellimoney

┌─────────────────────────────────────────────────────────────────────────────┐
│ USER-OWNED COLLECTIONS (all have user_id: ObjectId)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  expenses / transactions                                                    │
│  { _id, user_id, amount, description, category, date,                      │
│    payment_method, notes, source: "manual"|"aa", created_at }              │
│                                                                             │
│  budgets                                                                    │
│  { _id, user_id, category, limit, month, year, created_at }                │
│                                                                             │
│  financial_goals                                                            │
│  { _id, user_id, name, target_amount, current_amount,                      │
│    monthly_contribution, target_date, category, priority, status }         │
│                                                                             │
│  recurring_expenses                                                         │
│  { _id, user_id, name, amount, frequency, next_due_date,                  │
│    category, is_active, created_at }                                        │
│                                                                             │
│  subscriptions                                                              │
│  { _id, user_id, name, monthly_cost, renewal_date, category,               │
│    is_active, created_at }                                                  │
│                                                                             │
│  financial_scores (Health History)                                          │
│  { _id, user_id, score, risk_level, factors: {...}, calculated_at }        │
│                                                                             │
│  notifications                                                              │
│  { _id, user_id, type, title, message, read, created_at }                  │
│                                                                             │
│  agent_proposals (Copilot write confirmations)                             │
│  { _id, user_id, session_id, status, actions: [...], created_at }          │
│                                                                             │
│  AA SANDBOX COLLECTIONS                                                     │
│  aa_consents      { _id, user_id, consent_id, status, created_at }         │
│  aa_data_sessions { _id, user_id, session_id, status, created_at }         │
│                                                                             │
│  USER PROFILE (references Clerk)                                           │
│  users             { _id, clerk_user_id, monthly_income, created_at }      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. AUTHENTICATION FLOW (Clerk Only)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLERK AUTHENTICATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NO CUSTOM JWT • NO PASSWORD HASHING • NO LOCAL AUTH                        │
│                                                                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│  │  USER   │────▶│  CLERK  │────▶│  REACT  │────▶│ FASTAPI │              │
│  │         │     │  SIGN IN│     │  APP    │     │         │              │
│  └─────────┘     └─────────┘     └────┬────┘     └────┬────┘              │
│                                       │             │                     │
│                                       │  Clerk JWT  │                     │
│                                       │  (in header)│                     │
│                                       ▼             ▼                     │
│                              ┌─────────────────────────┐                  │
│                              │   CLERK IDENTITY        │                  │
│                              │   VALIDATION MIDDLEWARE │                  │
│                              │   (FastAPI Dependency)  │                  │
│                              └───────────┬─────────────┘                  │
│                                          │                                 │
│                                          ▼                                 │
│                              ┌─────────────────────────┐                  │
│                              │   USER CONTEXT          │                  │
│                              │   (clerk_user_id)       │                  │
│                              └───────────┬─────────────┘                  │
│                                          │                                 │
│                          ┌───────────────┼───────────────┐                │
│                          ▼               ▼               ▼                │
│                 ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│                 │  EXPENSES   │  │  BUDGETS    │  │  GOALS      │        │
│                 │  (filtered  │  │  (filtered  │  │  (filtered  │        │
│                 │   by user)  │  │   by user)  │  │   by user)  │        │
│                 └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  BACKEND MONGODB QUERIES ALWAYS INCLUDE:                                    │
│  {"user_id": ObjectId(clerk_user_id)}                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. FRONTEND ROUTE ARCHITECTURE

```
PUBLIC ROUTES                    AUTHENTICATED ROUTES (/app/*)
┌─────────────────────┐          ┌──────────────────────────────────────────┐
│ /                   │          │  CORE (Sidebar)                          │
│ /login              │          │  ┌────────────────────────────────────┐  │
│ /register           │          │  │ Dashboard        │ /app/dashboard  │  │
└─────────────────────┘          │  │ Health Score     │ /app/health     │  │
                                 │  │ Goals            │ /app/goals      │  │
                                 │  │ AI Copilot       │ /app/copilot    │  │
                                 │  └────────────────────────────────────┘  │
                                 │  INTEGRATIONS (Sidebar)                  │
                                 │  ┌────────────────────────────────────┐  │
                                 │  │ Account Aggregator │ /app/aa-sandbox│  │
                                 │  └────────────────────────────────────┘  │
                                 │                                           │
                                 │  DASHBOARD WORKSPACES (Sub-nav)          │
                                 │  ┌────────────────────────────────────┐  │
                                 │  │ Overview    │ /app/dashboard       │  │
                                 │  │ Analytics   │ /app/dashboard/analytics│ │
                                 │  │ Spending    │ /app/dashboard/spending  ││
                                 │  │ Cash Flow   │ /app/dashboard/cashflow  ││
                                 │  │ Budgets     │ /app/dashboard/budgets   ││
                                 │  │ Insights    │ /app/dashboard/insights  ││
                                 │  │ Notifications│/app/dashboard/notifications│
                                 │  └────────────────────────────────────┘  │
                                 │                                           │
                                 │  RETAINED FEATURE PAGES                  │
                                 │  /app/reports                            │
                                 │  /app/recurring                          │
                                 │  /app/subscriptions                      │
                                 │  /app/anomaly                            │
                                 │  /app/receipts                           │
                                 │  /app/budget-intelligence                │
                                 └──────────────────────────────────────────┘
```

---

## 8. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION DEPLOYMENT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                              │
│  │ VERCEL  │     │ RENDER  │     │ MONGODB │                              │
│  │ Frontend│     │ Backend │     │  ATLAS  │                              │
│  │(React)  │────▶│(FastAPI)│────▶│ (MongoDB)                              │
│  └─────────┘     └────┬────┘     └─────────┘                              │
│                       │                                                    │
│           ┌───────────┴───────────┐                                       │
│           ▼                       ▼                                       │
│    ┌─────────────┐         ┌─────────────┐                               │
│    │    GROQ     │         │  SETU AA    │                               │
│    │   (LLM)     │         │  SANDBOX    │                               │
│    └─────────────┘         └─────────────┘                               │
│                                                                             │
│  ENVIRONMENT VARIABLES (Backend only):                                     │
│  MONGODB_URL, CLERK_SECRET_KEY, GROQ_API_KEY,                             │
│  SETU_CLIENT_ID, SETU_CLIENT_SECRET, SETU_PRODUCT_INSTANCE_ID,            │
│  SETU_ENVIRONMENT, CORS_ORIGINS, API_BASE_URL                             │
│                                                                             │
│  FRONTEND ENV: VITE_CLERK_PUBLISHABLE_KEY                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. DOCKER COMPOSE (Local Development)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE SERVICES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  services:                                                                  │
│    mongodb:    mongo:7           → Port 27017                              │
│    redis:      redis:7-alpine    → Port 6379 (profile: with-redis)         │
│    backend:    Dockerfile.backend→ Port 8080, depends on mongodb           │
│    seed:       Dockerfile.backend→ Runs seed_demo.py (profile: with-seed)  │
│    frontend:   Dockerfile.frontend→ Port 3002, depends on backend          │
│                                                                             │
│  VOLUMES:                                                                   │
│    mongodb_data, backend_uploads, huggingface_cache                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. KEY ARCHITECTURAL DECISIONS (Interview Talking Points)

| Decision | Rationale |
|----------|-----------|
| **Clerk-only Auth** | No custom JWT, no password hashing, battle-tested |
| **LangChain + Groq** | Single LLM provider, tool-calling agent, structured outputs |
| **Deterministic Finance** | LLM never calculates money; backend owns all math |
| **Agent Proposes → User Confirms** | No accidental mutations, audit trail in `agent_proposals` |
| **Modular Monolith** | Single FastAPI app, clear layer separation, no microservices |
| **Setu AA Sandbox Only** | Demo integration, normalized into same pipeline as manual entry |
| **Removed ML Stack** | No TF-IDF/Logistic Regression; categorization via agent tools |
| **User-scoped Tools** | Agent never gets raw DB access; all queries filtered by user_id |
| **Single Navigation** | One sidebar, dashboard sub-routes, no duplicate nav bars |

---

## 11. WHITEBOARD DRAWING SEQUENCE (5-Minute Interview)

### Minute 1: High-Level Boxes
```
[USER] → [REACT + TAILWIND] → [FASTAPI] → [MONGODB]
                    ↓              ↓
               [CLERK]        [GROQ LLM]
                              [SETU AA]
```

### Minute 2: Request Flow
```
React → Clerk JWT → FastAPI Auth Middleware → Service → Repository → MongoDB
                    ↓
            User Context (clerk_user_id)
```

### Minute 3: AI Agent Loop
```
User Message → System Prompt + Context → LLM (Groq) → Tool Calls → 
→ Domain Services → Repository → MongoDB → Results → LLM → Final Answer
                                    ↓
                              propose_actions (if write)
                                    ↓
                              User Confirms → Backend Executes
```

### Minute 4: Financial Pipeline
```
Manual Entry + AA Sandbox → Normalized Transaction → 
→ Deterministic Services (Health, Budgets, Goals, Anomaly) → 
→ Dashboard + Copilot (reads results)
```

### Minute 5: Key Differentiators
- **No hallucinated money**: LLM only explains, backend calculates
- **Confirmation required**: Every write goes through proposal flow
- **Sandbox only**: AA is demo, not production banking
- **Deterministic health**: 10-factor weighted score, 0-100, no randomness
- **Interview-friendly**: Clean layers, explainable, minimal deps

---

## 12. TECH STACK SUMMARY (One-Liner)

```
Frontend: React + Tailwind + Clerk Auth
Backend:  FastAPI (Python) + LangChain Agent + Groq LLM
Database: MongoDB (user-scoped collections)
AI:       LangChain Tool-Calling Agent → Typed Financial Tools → Deterministic Services
Auth:     Clerk (only)
AA:       Setu AA Sandbox (demo only)
Deploy:   Vercel + Render + MongoDB Atlas
Local:    Docker Compose (MongoDB, Backend, Frontend)
```

---

## 13. QUICK REFERENCE: COMPONENT LOCATIONS

| Component | Backend Path | Frontend Path |
|-----------|-------------|---------------|
| Agent Service | `backend/app/agent/service.py` | - |
| Agent Tools | `backend/app/agent/tools.py` | - |
| Copilot API | `backend/app/api/v1/routes/copilot_v2.py` | `frontend/src/pages/copilot/` |
| Dashboard API | `backend/app/api/v1/routes/dashboard_v2.py` | `frontend/src/dashboard/pages/` |
| Financial Health | `backend/app/health/services/` | `frontend/src/pages/health/` |
| Budget Intelligence | `backend/app/budget_intelligence/` | `frontend/src/pages/budgetIntelligence/` |
| Goals | `backend/app/goal_planning/` | `frontend/src/pages/goals/` |
| AA Sandbox | `backend/app/services/aa_data_service.py` | `frontend/src/pages/AA_Sandbox.jsx` |
| Expenses | `backend/app/services/financial_transaction_service.py` | `frontend/src/dashboard/pages/SpendingPage.jsx` |
| Budgets | `backend/app/services/budget_service.py` | `frontend/src/dashboard/pages/BudgetsPage.jsx` |

---

*Keep this document handy. In an interview, start with the High-Level Architecture (Section 1), then dive into whichever area they ask about.*