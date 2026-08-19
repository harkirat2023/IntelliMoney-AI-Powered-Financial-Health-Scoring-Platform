# IntelliMoney — Product Requirements Document (PRD)

**Version:** 2.0  
**Status:** Final Approved Product Scope  
**Product:** IntelliMoney — AI-Powered Financial Health & Personal Finance Platform

## 1. Product Vision

IntelliMoney is an AI-first personal finance platform where users can understand, manage and act on their finances through a secure **LangChain agent powered by Groq**, while the Dashboard, Financial Health and Goals provide structured visual control surfaces.

**Core principle:**

User intent → Agent understands → Agent reads the user's real financial data through scoped tools → Agent asks for missing information when necessary → Agent proposes changes → User confirms → Tools execute deterministic operations → Dashboard and visual modules reflect the results.

IntelliMoney supports two sources of financial information:

1. Manually entered financial data.
2. Account Aggregator data obtained through the **Setu AA Sandbox/demo environment** for demonstration.

The Account Aggregator implementation is **sandbox/demo only** and must never be represented as production banking connectivity.

### AI-first scope decision

The Copilot is the primary interaction layer for financial actions. Users can still use manual UI flows for Expenses/Spending, Budgets, Goals and other retained visual modules, but the application should not require users to navigate multiple independent management screens for routine actions.

The agent can read the user's complete financial context through authenticated, user-scoped tools and can perform approved write actions through tools. The LLM never receives direct database access and never becomes the source of financial truth.

### Financial intelligence decision

The previous ML-based expense categorization pipeline is removed. The platform no longer requires TF-IDF, Logistic Regression or a trained expense-classifier artifact. Expense categorization and natural-language interpretation are handled through the agent/tool layer, while all authoritative financial calculations remain deterministic backend logic.

### Mutation safety

Any create/update/delete financial action follows:

User request → Agent plan → Proposed changes → User confirmation → Tool execution.

The agent must ask follow-up questions whenever critical information is missing. No financial value, date, goal amount, budget amount or intent may be invented or hallucinated.

## 2. Target User

Individuals who want to:

- track expenses;
- manage budgets;
- monitor income and savings;
- understand financial health;
- set savings goals;
- identify unusual spending;
- track recurring expenses/subscriptions;
- import demonstration financial data through Account Aggregator sandbox flows;
- ask financial questions in natural language.

---

## 3. Product Principles

| Principle | Requirement |
|---|---|
| Simplicity | Prefer one agent + domain tools over multiple overlapping intelligence systems |
| Reliability | Make existing features work before improving them |
| Explainability | Scores, recommendations and proposed actions must be understandable |
| Privacy | Financial data is user-specific and isolated by authenticated Clerk identity |
| Deterministic finance | Financial calculations and database mutations are never delegated to the LLM |
| AI-first interaction | LangChain Agent + Groq are the primary natural-language interaction layer |
| Human confirmation | All write/destructive financial actions require explicit user confirmation |
| No hallucinations | Missing critical information must trigger a clarification question |
| AA-ready | Setu AA Sandbox is supported as a demonstration workflow |
| No production banking | No live bank connectivity is required |
| Clerk authentication | Clerk is the only application authentication system |
| No custom JWT | Do not implement or maintain application-managed JWT authentication |
| Responsive | Mobile, tablet, laptop and desktop |
| Maintainability | Avoid duplicate routes, services, state systems and intelligence engines |

## 4. Core Features

| Feature | Purpose | Implementation |
|---|---|---|
| Authentication | Secure access | Clerk |
| Dashboard | Central structured financial workspace and visual reporting | React + FastAPI |
| Expenses / Spending | Record, review and analyze spending | CRUD + MongoDB + agent tools |
| Budgets | Spending limits and monitoring | CRUD + deterministic calculations + agent tools |
| Financial Health | 0–100 financial score | Weighted deterministic rule-based engine |
| Budget Intelligence | Financial/budget visualization and reporting | Deterministic analytics + Dashboard visualizations |
| Expense Categorization | Classify transactions without the old ML pipeline | Agent/tool-based categorization |
| Reports | Financial analytics | Aggregated APIs + charts + agent read tools |
| Recurring Expenses | Track recurring commitments | CRUD + agent tools |
| Subscriptions | Track subscriptions | CRUD + analysis + agent tools |
| Anomaly Detection | Detect unusual spending | Lightweight statistical/rule logic |
| Goals | Track savings targets | Manual UI + agent tools |
| Receipt/OCR | Extract receipt data | Existing OCR implementation |
| AI Copilot | Primary natural-language financial interface | LangChain Agent + Groq + scoped tools |
| Notifications | Financial alerts | Deterministic backend events |
| Account Aggregator Sandbox | Demonstrate consented financial-data acquisition | Setu AA Sandbox/demo |

## 5. Explicitly Out of Scope

The following remain outside the production product scope:

- Real production bank account integration
- UPI integration
- Live bank transaction synchronization
- Payment processing
- Investment trading
- Credit-card/loan/insurance provider integrations
- Kafka/Kubernetes/microservices
- Multiple LLM providers
- OpenAI dependency
- New ML models without a clear requirement
- Production Account Aggregator deployment
- Production banking credentials
- Direct bank credential collection
- Automatic production bank synchronization

### Account Aggregator exception

**Setu AA Sandbox/mock integration IS IN SCOPE for demonstration.**

This means IntelliMoney may implement:

- AA consent creation;
- consent status handling;
- consent approval/rejection demonstration;
- Setu sandbox notification handling;
- sandbox financial-data fetch;
- mapping sandbox financial data into IntelliMoney's internal transaction model;
- transaction categorization and analysis using existing IntelliMoney logic.

It must NOT be presented as production banking connectivity.

Setu's AA flow is based around consent, data fetching and notifications, and its sandbox provides mock FI data for development.

---

## 6. Minimal Tech Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React.js | UI and client-side application |
| Styling | Tailwind CSS / existing styling | Responsive design |
| Authentication | Clerk | Authentication, sessions and user identity |
| Backend | FastAPI | REST APIs and business logic |
| Language | Python | Backend, deterministic financial calculations and integrations |
| Database | MongoDB | Application and financial data |
| AI | Groq | LLM used by the agent |
| AI Framework | LangChain | Agent orchestration, tool calling and structured outputs |
| Account Aggregator | Setu AA Sandbox | Demonstration financial-data integration |
| OCR | Existing OCR implementation | Receipt extraction |
| Charts | Existing chart library | Financial visualization |
| Containers | Docker/Compose if already used | Local environment |
| Testing | Pytest + existing frontend tests | Verification |
| Source Control | Git/GitHub | Version control |

**Rule:** Do not introduce another library when the current stack already solves the requirement.

The previous scikit-learn / TF-IDF / Logistic Regression expense-classification stack is intentionally removed from the approved architecture.

## 7. Architecture

```text
React + Tailwind
      ↓
Clerk Authentication
      ↓
FastAPI API
      ↓
Agent / Domain Services
      ↓
Repositories
      ↓
MongoDB
```

### AI-first architecture

```text
User
  ↓
AI Copilot UI
  ↓
FastAPI Copilot Endpoint
  ↓
LangChain Agent
  ↓
Groq
  ↓
Scoped Financial Tools
  ↓
Deterministic Domain Services
  ↓
Repositories
  ↓
MongoDB
```

The agent may read the user's complete financial context through user-scoped tools, but never receives direct MongoDB access.

### Tool categories

```text
READ TOOLS
  expenses / budgets / income / goals / reports / health /
  subscriptions / recurring / anomalies / notifications / accounts / AA

WRITE TOOLS
  create / update / delete / import / sync actions

CALCULATION TOOLS
  financial health / budget usage / cash flow /
  savings / goal progress / reports / anomaly calculations
```

### Mutation flow

```text
User Request
    ↓
Agent understands intent
    ↓
Agent asks clarification if required
    ↓
Agent selects tools
    ↓
Proposed Changes
    ↓
User Confirmation
    ↓
Tool Execution
    ↓
Deterministic Backend Result
    ↓
Dashboard / Health / Goals / Reports refresh
```

### Financial intelligence

Manual Data ─────────────┐
                         ↓
Setu AA Sandbox ─────────┤
                         ↓
                  Normalized Financial Data
                         ↓
                  Deterministic Domain Services
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     Budgets       Financial Health    Analytics
        ↓                ↓                ↓
        └────────────────┼────────────────┘
                         ↓
                     Dashboard
                         ↓
                  Agent / Copilot

### Account Aggregator boundary

```text
IntelliMoney
     ↓
AA Service Interface
     ↓
Setu AA Sandbox Adapter
     ↓
Setu AA Sandbox
     ↓
Consent / Notification / Data Fetch
     ↓
Normalized Financial Data
     ↓
Existing Transaction Pipeline
```

### Agent knowledge boundary

```text
Clerk User Identity
      ↓
Authenticated Tool Context
      ↓
User-scoped queries
      ↓
MongoDB
```

The agent must never query another user's financial information and must never access secrets directly.

## 8. Customer Journey

### Existing user

```text
Landing Page
 ↓
Sign In
 ↓
Clerk Authentication
 ↓
Account Sync
 ↓
Existing User Detected
 ↓
Dashboard
```

### New user

```text
Landing Page
 ↓
Sign Up
 ↓
Clerk Authentication
 ↓
Account Sync
 ↓
New User Detected
 ↓
Connect Account
 ├── Connect via AA Sandbox
 │      ↓
 │   Optional Import
 │      ↓
 │   Dashboard
 │
 └── Skip for now
        ↓
     Dashboard
```

### AI-first daily flow

```text
Dashboard
 ↓
AI Copilot
 ↓
Natural-language request
 ↓
Agent reads data / asks questions
 ↓
Proposed changes when required
 ↓
User confirms
 ↓
Tools execute
 ↓
Visual modules refresh
```

### Important planning behavior

For a request such as:

> "My monthly income is ₹60,000. I want to spend ₹5,000 on food, ₹5,000 on travel and save the rest."

the agent must extract the known values but must NOT assume whether the remaining ₹50,000 should become a savings goal, a planned savings amount, or another financial object. It must ask the user what they want the remaining amount to represent, then present a proposed plan for confirmation.

## 9. Expense Management

Users can create, edit, delete, search and filter expenses.

| Field | Required |
|---|---|
| Amount | Yes |
| Description/Merchant | Yes |
| Category | Auto-detected or selected |
| Date | Yes |
| Payment Method | Optional |
| Notes | Optional |

Flow:

```text
User Input
    ↓
Validation
    ↓
POST /expenses
    ↓
Service
    ↓
Categorization
    ↓
MongoDB
    ↓
Response
    ↓
UI
```

Imported AA transactions must pass through the same normalization and categorization pipeline rather than creating a second financial-processing system.

---

## 10. Expense Categorization / AI Tool

The previous TF-IDF + Logistic Regression model is removed.

Expense categorization is now handled through an authenticated agent/tool capability.

```text
Transaction Description
        ↓
Agent / Categorization Tool
        ↓
Category + Explanation
        ↓
User-confirmed write when required
        ↓
MongoDB
```

The categorization tool may use Groq structured output where natural-language classification is needed, but it must never invent transactions or financial values.

Manual category selection remains available in the Spending UI.

The categorization layer is not the source of truth for financial calculations.

## 11. Budget Management

Users can create, update, delete and monitor category budgets.

| Usage | Status |
|---:|---|
| 0–74% | Healthy |
| 75–89% | Warning |
| 90–99% | Critical |
| 100%+ | Exceeded |

Budget Intelligence explains:

- overspending;
- under-budget categories;
- budget adherence;
- practical reductions.

---

## 12. Financial Health Score

A deterministic 0–100 score.

It must:

- never be random;
- never depend on Groq;
- never depend on an LLM;
- use actual available financial data;
- explicitly handle unavailable data.

| Factor | Weight |
|---|---:|
| Savings Rate | 20% |
| Debt Ratio | 15% |
| Budget Adherence | 15% |
| Emergency Fund | 10% |
| Cash Flow | 10% |
| Goal Completion | 10% |
| Expense Stability | 10% |
| Income Stability | 5% |
| Investment Habit | 5% |
| Financial Trend | 10% |
| **Total** | **100%** |

Inputs may include:

- income;
- expenses;
- savings;
- budgets;
- debt;
- EMI;
- recurring costs;
- goals;
- financial trends;
- imported AA financial data where available.

No missing value may be silently invented.

---

## 13. Financial Health History

Store historical calculations so users can view:

- current score;
- previous scores;
- monthly trends;
- factor changes.

Use a simple historical record.

Do not build event sourcing.

---

## 14. Goals

Keep Goals simple.

| Field | Description |
|---|---|
| Name | Goal name |
| Target Amount | Desired amount |
| Current Amount | Amount saved |
| Monthly Contribution | Planned contribution |
| Target Date | Expected completion |
| Category | Goal type |
| Priority | Low/Medium/High |
| Notes | Optional |

Calculate:

- progress %;
- remaining amount;
- required monthly contribution;
- estimated completion;
- status.

Goals should contribute to financial-health insights.

---

## 15. Recurring Expenses

Track:

- rent;
- EMI;
- utilities;
- insurance;
- subscriptions;
- other recurring commitments.

Store:

- amount;
- frequency;
- next due date;
- category;
- active status.

---

## 16. Subscriptions

Track:

- subscription name;
- monthly cost;
- renewal date;
- category;
- active status.

Show total recurring subscription cost.

---

## 17. Anomaly Detection

Identify unusual spending compared with the user's normal pattern using lightweight explainable logic.

Do not introduce a complex anomaly ML platform.

AA-imported transactions may be included in anomaly analysis after normalization.

---

## 18. Reports & Analytics

Provide:

- spending;
- income;
- savings;
- category breakdown;
- monthly trends;
- budget performance;
- cash flow;
- recurring costs;
- financial trends.

Reports must use actual stored data.

---

## 19. Dashboard

Primary information:

- Monthly Spending
- Monthly Income
- Net Savings
- Cash Flow
- Financial Health Score
- Spending by category
- Recent transactions
- Budget overview
- Health trend
- Goal progress
- Recommendations
- Alerts
- Account Aggregator connection/import status where implemented

Avoid duplicate navigation bars and redundant widgets.

---

## 20. AI Financial Copilot

The Copilot is the primary interaction layer for IntelliMoney.

### Technology

```text
React Copilot UI
      ↓
FastAPI
      ↓
LangChain Agent
      ↓
Groq
      ↓
Typed Financial Tools
      ↓
Domain Services / MongoDB
```

### Agent capabilities

The agent can:

- answer questions about the user's finances;
- inspect the user's complete financial context through scoped read tools;
- create, update and delete expenses;
- create, update and delete budgets;
- set or update income;
- create, update and delete goals;
- manage recurring expenses and subscriptions;
- calculate and explain financial health;
- inspect budget intelligence;
- generate reports from real data;
- detect/explain anomalies;
- manage notifications where supported;
- inspect account/sync status;
- initiate and inspect approved AA Sandbox actions;
- import approved AA Sandbox data when the user requests it.

### Read vs write actions

Read-only requests may execute immediately.

Write and destructive requests MUST use:

```text
User Request
 ↓
Agent Plan
 ↓
Proposed Changes
 ↓
User Confirmation
 ↓
Tool Execution
```

### Clarification rule

The agent must ask follow-up questions whenever critical information is missing.

Examples:

- "Make me a budget." → ask monthly income and other critical planning inputs.
- "Save the rest." → ask whether the remainder should be a savings goal, planned savings amount, or another explicit target.
- "Delete that expense." → identify the exact transaction before proposing deletion.

No assumptions or hallucinations are allowed.

### Suggested questions

Show approximately 4–6 dynamic suggestions based on the user's current financial state, such as:

- How much did I spend this month?
- Where am I overspending?
- Create a budget for me.
- How can I reach my savings goal?
- Why did my health score change?
- Analyze my subscriptions.

### External knowledge boundary

The user's full financial database is an external knowledge source exposed only through authenticated, user-scoped tools. The LLM never receives raw MongoDB access.

### AI rules

- Groq is the only LLM provider.
- OpenAI must not be introduced.
- No second LLM provider.
- Groq credentials remain server-side.
- The LLM must not invent transactions, balances, scores or financial values.
- The LLM must not directly mutate the database.
- Tool outputs and deterministic backend calculations are the source of truth.

## 21. Account Aggregator Sandbox Integration

### Purpose

Provide a realistic demonstration of consented financial-data acquisition without implementing production banking connectivity.

### Provider

**Setu AA Sandbox**

### User experience

The AA Sandbox is a dedicated demonstration/integration page, not the primary financial-management workflow.

The user may:

1. Create a sandbox consent.
2. Review/approve/reject the consent in the supported demo flow.
3. Inspect consent state.
4. Create a data session when consent is approved.
5. Inspect data-session state.
6. Optionally fetch/import approved sandbox data.

### Import semantics

AA Sandbox import is optional/manual from the user's perspective.

- If the user rejects consent or does not request import, no financial data is imported.
- If the user approves the consent and explicitly proceeds with the available import/fetch action, the returned sandbox data is automatically normalized and inserted into the same financial transaction pipeline used by manual transactions.
- Imported transactions must then participate in dashboard spending, budgets, cash flow, financial health, reports and other downstream calculations.

### Required demonstration capabilities

- AA consent creation;
- consent status handling;
- consent approval/rejection demonstration;
- sandbox notification handling where supported;
- data-session creation;
- data-ready status handling;
- sandbox financial-data fetch;
- mapping sandbox data into IntelliMoney's transaction model;
- transaction import and duplicate prevention.

### Architectural rule

```text
Frontend
  ↓
FastAPI AA Service
  ↓
AA Provider Interface
  ↓
Setu Sandbox Adapter
  ↓
Normalized Transaction
  ↓
Existing Transaction/Financial Pipeline
```

Setu-specific calls must remain behind the provider boundary.

### Sandbox-only labeling

The UI must clearly display:

**Account Aggregator Sandbox / Demo**

It must state that it is not connected to real production bank accounts.

Never claim production banking connectivity.

## 22. Receipt/OCR

If retained:

```text
Receipt Image
 ↓
OCR
 ↓
Merchant / Amount / Date
 ↓
User Confirmation
 ↓
Expense
```

OCR assists the user and must not silently create incorrect expenses.

---

## 23. Notifications

Keep notifications limited to existing financial events:

- 75% budget usage;
- 90% budget usage;
- budget exceeded;
- unusual spending;
- upcoming recurring payment;
- goal milestone;
- relevant AA consent/data status where required.

Use deterministic backend rules.

---

## 24. Authentication

### Authentication provider

**Clerk is the only authentication system.**

There is **NO custom JWT authentication**.

There is:

- no application-generated JWT;
- no custom login/password system;
- no password hashing implementation;
- no local password credential storage;
- no duplicate authentication provider.

### Flow

```text
User
 ↓
Clerk Sign Up / Sign In
 ↓
Clerk Session
 ↓
Authenticated Frontend
 ↓
FastAPI
 ↓
Clerk Identity Validation
 ↓
Authenticated User Context
 ↓
Protected Service
```

The backend must associate financial records with the authenticated Clerk user identity.

### Authorization

All financial endpoints require:

1. authenticated Clerk identity;
2. user-level authorization;
3. ownership checks.

A user must never be able to access another user's financial records by modifying an ID in an API request.

---

## 25. Request Lifecycle

```text
React Component
 ↓
Clerk Authentication
 ↓
API Client
 ↓
HTTP Request
 ↓
FastAPI Router
 ↓
Authentication / Authorization
 ↓
Service
 ↓
Repository
 ↓
MongoDB
 ↓
Response Schema
 ↓
React State
 ↓
UI
```

AA flow:

```text
React
 ↓
FastAPI
 ↓
AA Service
 ↓
Setu Sandbox
 ↓
Notification / Data Fetch
 ↓
AA Mapper
 ↓
Financial Service
 ↓
MongoDB
```

---

## 26. Database

Primary collections:

| Collection | Purpose |
|---|---|
| expenses/transactions | Financial transactions |
| budgets | Budgets |
| goals | Savings goals |
| recurring_expenses | Recurring commitments |
| subscriptions | Subscriptions |
| financial_scores | Score history |
| recommendations | Recommendations |
| notifications | Alerts |
| aa_consents | Sandbox consent tracking, if required |
| aa_data_sessions | Sandbox data-fetch tracking, if required |

### Authentication data

Clerk is the identity provider.

Do not maintain a separate password-based authentication system.

A local user/profile collection may exist only when required by application functionality, and it must reference the Clerk user identity.

### Financial ownership

Every financial document must be associated with the authenticated Clerk user.

---

## 27. Frontend Logical Routes

### Public

```text
/
/login
/register
```

### Primary authenticated routes

```text
/app/dashboard
/app/health
/app/goals
/app/copilot
/app/budget-intelligence
/app/aa-sandbox
```

### Dashboard sub-routes

```text
/app/dashboard/overview
/app/dashboard/analytics
/app/dashboard/spending
/app/dashboard/cashflow
/app/dashboard/budgets
/app/dashboard/insights
/app/dashboard/notifications
```

### Retained feature routes

```text
/app/reports
/app/recurring
/app/subscriptions
/app/anomaly
/app/receipts
```

### Legacy compatibility

If the repository currently exposes `/app/expenses` or `/app/budgets`, migrate their implementation to the Dashboard sub-routes and optionally redirect legacy URLs to:

```text
/app/expenses → /app/dashboard/spending
/app/budgets → /app/dashboard/budgets
```

Do not maintain duplicate page implementations.

The exact AA route should follow the existing repository routing conventions if an equivalent route already exists.

## 28. UI Requirements

Use the existing IntelliMoney visual language from `IntelliMoney_DESIGN.md`.

### Primary left sidebar

The sidebar must be intentionally small:

```text
CORE
- Dashboard
- Health Score
- Goals
- AI Copilot

INTEGRATIONS
- Account Aggregator
```

Do NOT show Expenses or Budgets as top-level sidebar items.

Bank Accounts, Data Sync and similar operational integration pages should be handled through the Account Aggregator area and/or agent tools unless the approved design explicitly requires a separate page.

### Dashboard navigation

Dashboard contains structured financial workspaces such as:

- Overview
- Analytics
- Spending
- Cash Flow
- Budgets
- Insights
- Notifications

### AI Copilot UI

The Copilot should feel like a first-class application surface and include:

- conversation;
- dynamic suggested questions;
- tool/action plan cards;
- confirmation controls;
- execution status;
- results;
- loading/error states.

### Goals and Health

Goals and Health Score remain dedicated sidebar modules because users need visual, persistent views of progress and financial health.

### Budget Intelligence

Budget Intelligence remains a visual/reporting area, not a second conversational AI system.

### Responsive behavior

Every page must work on:

- mobile;
- tablet;
- laptop;
- desktop.

Avoid:

- duplicated navigation;
- excessive nested navigation;
- large unexplained empty areas;
- blank states without guidance;
- broken charts;
- misleading production banking claims.

## 29. Security

- Clerk authentication
- Clerk identity validation
- User-level authorization
- Input validation
- CORS
- Secrets in environment variables
- No API keys in Git
- Safe error responses
- No sensitive financial data in logs
- Groq key server-side only
- Setu credentials server-side only
- AA webhook validation according to the integration requirements
- User ownership checks on every financial resource

Do not implement custom JWT authentication.

---

## 30. Deployment

Keep deployment simple:

```text
Frontend
   ↓
Backend API
   ↓
MongoDB

Backend
   ↓
Setu AA Sandbox
   ↓
Groq
```

Possible infrastructure:

```text
Vercel
+
Render/Railway
+
MongoDB Atlas
```

No Kubernetes or microservices.

The Setu sandbox integration remains an external development/demo dependency.

---

## 31. Local Startup

The existing startup script should:

- start required services;
- check health;
- start backend/frontend;
- report failures.

Improve the existing startup mechanism rather than creating duplicate startup systems.

Required environment configuration should include only the credentials actually required by the existing implementation, such as:

```text
MONGODB_URL
CLERK_SECRET_KEY
VITE_CLERK_PUBLISHABLE_KEY
GROQ_API_KEY
SETU_CLIENT_ID
SETU_CLIENT_SECRET
SETU_PRODUCT_INSTANCE_ID
SETU_ENVIRONMENT
CORS_ORIGINS
API_BASE_URL
```

Exact Setu environment-variable names should follow the implemented adapter and current Setu sandbox configuration.

Never commit real credentials.

---

## 32. Testing

Verify:

### Authentication

- Clerk sign-up/sign-in;
- protected routes;
- user ownership;
- existing-user → Dashboard;
- new-user → Connect Account;
- new-user Skip → Dashboard;
- no redirect loops;
- no duplicate sync requests.

### Agent

- read-only questions;
- missing-information clarification;
- proposed write actions;
- confirmation/cancel flow;
- tool execution;
- multi-tool plans;
- partial failure handling;
- user ownership;
- no hallucinated results.

### Financial tools

- expense CRUD;
- budget CRUD;
- income updates;
- goals;
- recurring expenses;
- subscriptions;
- reports;
- health calculations;
- anomaly detection;
- notifications.

### AA Sandbox

- consent creation;
- approval/rejection;
- data-session creation;
- data-ready state;
- fetch/import;
- duplicate prevention;
- user ownership;
- downstream transaction propagation.

### Frontend

- routes;
- dashboard sub-routes;
- Clerk state;
- forms;
- API integration;
- loading/error states;
- responsive layouts;
- Copilot confirmation UI;
- AA Sandbox UI.

### Critical agent flow

```text
User Request
 ↓
Agent
 ↓
Clarification if necessary
 ↓
Tools / Financial Data
 ↓
Proposed Changes
 ↓
User Confirmation
 ↓
Tool Execution
 ↓
Dashboard / Health / Goals refresh
```

## 33. Definition of Done

- Clerk registration/login works.
- No custom JWT authentication remains.
- Existing users go directly to Dashboard after login.
- New users go to Connect Account after signup.
- Skip from Connect Account goes to Dashboard.
- Protected routes work.
- User-level authorization works.
- Copilot is a real LangChain Agent powered by Groq.
- Agent uses scoped tools for financial reads and writes.
- Read-only requests can execute without confirmation.
- Write/destructive requests require explicit confirmation.
- Agent asks follow-up questions when critical information is missing.
- Agent cannot directly access MongoDB.
- Agent cannot access another user's financial data.
- No financial hallucinations are accepted as tool results.
- Expense CRUD works.
- Old TF-IDF/Logistic Regression categorization pipeline is removed.
- Budgets and thresholds work.
- Financial Health is deterministic and 0–100.
- Health history works.
- Goals work manually and through the agent.
- Budget Intelligence remains available as visualization/reporting.
- Reports use real stored data.
- Recurring/subscription features work.
- Anomaly detection works.
- OCR works where implemented.
- Notifications work.
- Setu AA Sandbox demonstration flow works where credentials/configuration are available.
- AA import is optional/manual and only imports when the user proceeds.
- Approved AA imports flow through the same financial pipeline as manual transactions.
- No production banking integration is claimed.
- No UPI integration exists.
- No payment processing exists.
- No critical runtime/build errors.
- No broken imports/API mismatches.
- No exposed secrets.
- All pages are responsive.
- Project remains simple and interview-friendly.

## 34. Final Product Scope

```text
Clerk Authentication
        ↓
Dashboard
        ↓
┌──────────────────────────────────────────────┐
│ AI Copilot Agent                             │
│ LangChain + Groq + Authenticated Tools      │
└──────────────────────────────────────────────┘
        ↓
Financial Domain Tools
        ↓
Expenses / Budgets / Income / Goals /
Recurring / Subscriptions / Reports /
Health / Anomaly / Notifications / AA
        ↓
MongoDB
```

### Primary navigation

```text
CORE
- Dashboard
- Health Score
- Goals
- AI Copilot

INTEGRATIONS
- Account Aggregator
```

### Dashboard workspace

```text
Overview
Analytics
Spending
Cash Flow
Budgets
Insights
Notifications
```

### Final rules

1. **Clerk is the only authentication provider.**
2. **Do not implement application-managed JWT authentication.**
3. **Groq is the only LLM provider.**
4. **LangChain Agent is the primary natural-language interaction layer.**
5. **Financial mutations happen only through validated tools after explicit user confirmation.**
6. **The agent must ask for missing critical information instead of guessing.**
7. **The agent has no direct MongoDB access and cannot cross user boundaries.**
8. **The previous TF-IDF + Logistic Regression expense-classification system is removed.**
9. **Financial calculations remain deterministic backend logic.**
10. **Health Score and Goals remain dedicated visual modules.**
11. **Budget Intelligence becomes primarily a visualization/reporting area, while Copilot is its interaction layer.**
12. **Expenses move to `/app/dashboard/spending`.**
13. **Budgets move to `/app/dashboard/budgets`.**
14. **Expenses and Budgets are removed from the primary left sidebar.**
15. **The primary sidebar contains Dashboard, Health Score, Goals and AI Copilot.**
16. **The Integrations section contains Account Aggregator.**
17. **Setu AA Sandbox remains a demonstration integration, never production banking connectivity.**
18. **AA imports are optional/manual and only occur when the user proceeds with the approved flow.**
19. **AA-imported transactions use the same downstream financial pipeline as manual transactions.**
20. **No OpenAI or second LLM provider.**
21. **No microservices, Kafka or Kubernetes.**
22. **Do not invent features outside this PRD.**
23. **The three specification documents plus these approved AI-first changes are the source of truth.**
24. **The goal is to make IntelliMoney smaller, clearer, safer, more agentic and easier to demonstrate.**

