# IntelliMoney — Minimal Tech Stack

**Version:** 3.0

**Purpose:** Keep IntelliMoney technically simple, AI-first, reliable, interview-friendly and easy to maintain while preserving every approved core feature, including the Setu AA Sandbox demonstration and Clerk authentication.

---

## 1. Core Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js | UI and client-side application |
| Styling | Tailwind CSS | Responsive UI and design system |
| Authentication | Clerk | Authentication, sessions and user identity |
| Backend | FastAPI | REST API and business logic |
| Language | Python | Backend and deterministic financial calculations |
| Database | MongoDB | User and financial data |
| AI | Groq | LLM used by the financial agent |
| AI Orchestration | LangChain | Agent orchestration, tool calling and structured outputs |
| Account Aggregator | Setu AA Sandbox | Demonstration financial-data integration |
| OCR | Existing OCR implementation | Receipt extraction |
| Charts | Existing chart library | Financial visualizations |
| Containers | Docker Compose | Simple local environment, if already used |
| Testing | Pytest + existing frontend tests | Verification |
| Version Control | Git + GitHub | Source control |

### Removed from the approved architecture

The old expense-categorization ML stack is intentionally removed:

- scikit-learn expense classifier;
- TF-IDF expense features;
- Logistic Regression expense classifier;
- trained expense-classifier artifact;
- ML training pipeline used solely for expense categorization.

The project should not retain these dependencies or artifacts unless another independently verified feature still requires them.

**Authentication is Clerk-only.**

**LLM is Groq-only.**

**Agent orchestration is LangChain.**

## 2. Architecture

```text
React + Tailwind
       ↓
Clerk Authentication
       ↓
FastAPI
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
Copilot UI
 ↓
FastAPI
 ↓
LangChain Agent
 ↓
Groq
 ↓
User-scoped Financial Tools
 ↓
Deterministic Domain Services
 ↓
Repositories
 ↓
MongoDB
```

### Tool boundary

The agent receives tools, not raw database access.

```text
Agent
 ↓
Typed Tool
 ↓
Service
 ↓
Repository
 ↓
MongoDB
```

### Mutation flow

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

### Financial pipeline

```text
Manual Transactions
       │
       ├──────────────┐
       │              │
Setu AA Sandbox       │
       │              │
       └──────┬───────┘
              ↓
       Normalized Financial Data
              ↓
      Deterministic Domain Services
              ↓
    Budgets / Health / Reports / Dashboard
              ↓
              Copilot
```

### Account Aggregator boundary

```text
FastAPI
  ↓
Account Aggregator Service
  ↓
AA Provider Interface
  ↓
Setu Sandbox Adapter
  ↓
Normalized Transaction
  ↓
Existing Financial Pipeline
```

Keep the application a modular monolith.

Do not introduce microservices.

## 3. Frontend

### React.js

Responsible for:

- pages;
- routing;
- forms;
- dashboard;
- financial visualizations;
- API communication;
- responsive UI;
- Clerk authentication UI/integration;
- Copilot interface;
- Account Aggregator sandbox connection UI.

### Tailwind CSS

Responsible for:

- IntelliMoney visual theme;
- responsive layouts;
- reusable spacing;
- colors;
- typography;
- cards;
- buttons;
- forms.

**Rule:** Use the existing frontend stack where possible. Do not add another UI framework.

---

## 4. Authentication

### Clerk

Clerk is the sole authentication and identity provider.

Responsible for:

- sign up;
- sign in;
- sign out;
- session management;
- authenticated user identity;
- protected frontend routes;
- authentication integration with the backend.

Architecture:

```text
User
 ↓
Clerk
 ↓
Authenticated Session
 ↓
React
 ↓
FastAPI
 ↓
Clerk Identity Validation
 ↓
User Context
 ↓
Protected Service
```

### Explicitly forbidden

Do not implement:

```text
Custom JWT
Password Hashing
Local Password Login
Custom Login Sessions
```

Do not keep the old JWT authentication system "just in case."

If legacy JWT/password authentication exists in the repository, remove or migrate it after verifying every dependent route.

### User ownership

The authenticated Clerk user identity must be used to enforce ownership of:

- expenses;
- budgets;
- goals;
- reports;
- financial scores;
- recurring expenses;
- subscriptions;
- anomalies;
- recommendations;
- notifications;
- AA connections/data.

---

## 5. Backend

### FastAPI

Responsible for:

- REST endpoints;
- Clerk authentication integration;
- authorization;
- validation;
- deterministic financial business logic;
- domain services;
- LangChain agent integration;
- tool execution;
- OCR processing;
- Setu AA integration;
- notifications.

Use:

```text
Router
  ↓
Authentication / Authorization
  ↓
Service / Tool
  ↓
Repository
  ↓
MongoDB
```

The LLM must not contain authoritative business logic.

## 6. Database

### MongoDB

Primary collections:

```text
expenses / transactions
budgets
goals
recurring_expenses
subscriptions
financial_scores
recommendations
notifications
```

AA-specific collections may be introduced only when needed:

```text
aa_consents
aa_data_sessions
```

### Authentication data

Clerk is the identity source.

A local user/profile document may exist if required by application functionality, but it must reference the Clerk identity.

Do not store passwords.

Do not create a custom authentication token system.

### Financial ownership

Every user-owned financial record must contain a reference to the authenticated Clerk user.

---

## 7. Account Aggregator — Setu AA Sandbox

### Purpose

Provide an AA-ready architecture and working sandbox/demo integration without implementing production banking connectivity.

Setu's current AA documentation describes three major integration flows:

1. consent;
2. data fetch;
3. notifications.

Its sandbox provides mock financial data for development/testing.

### Architecture

```text
FastAPI
   ↓
Account Aggregator Service
   ↓
AA Provider Interface
   ↓
Setu Sandbox Adapter
   ↓
Setu AA Sandbox
```

The core application must depend on the abstraction/interface, not directly on Setu-specific implementation details.

### Suggested logical structure

```text
backend/
  integrations/
    account_aggregator/
      interface.py
      setu_sandbox.py
      models.py
      mapper.py
      service.py
```

Use the existing repository architecture if an equivalent structure already exists.

### Required flow

```text
Create Consent
      ↓
Consent Pending
      ↓
User Approves / Rejects
      ↓
Notification
      ↓
Approved
      ↓
Create Data Session
      ↓
Data Ready
      ↓
Fetch Financial Data
      ↓
Normalize
      ↓
Import Transactions
```

Setu's documented data flow uses an approved consent to create a data session and subsequently fetch FI data when available.

### Important architectural rule

Do not put Setu API calls inside:

- React components;
- expense services;
- budget services;
- financial-health services;
- ML services.

Use the dedicated integration boundary.

### Normalization

```text
Setu FI Data
    ↓
Setu Mapper
    ↓
Normalized Transaction
    ↓
Existing Expense/Transaction Service
    ↓
Categorization
    ↓
MongoDB
```

The AA integration must reuse the existing transaction-processing pipeline.

Do not build a separate analytics system for AA data.

### Notifications

The backend must expose the required notification endpoint(s) for the sandbox integration.

Setu documents consent and FI-data notifications as part of the AA flow.

### Sandbox only

The implementation must clearly distinguish:

```text
Setu AA Sandbox
```

from:

```text
Production Account Aggregator
```

No production banking integration is required.

---

## 8. AI / Agent Stack

### LangChain Agent

The primary AI architecture is a real tool-using agent:

```text
User Request
    ↓
LangChain Agent
    ↓
Groq
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Tool Result
    ↓
Agent Response
```

The agent must:

- understand intent;
- inspect user-scoped financial data;
- ask clarifying questions;
- generate proposed write actions;
- wait for confirmation;
- execute approved tools;
- explain tool results.

### No direct database access

The agent never receives a MongoDB client, connection string, collection handle or unrestricted query mechanism.

### No hallucinated financial data

Financial values must come from tools/backend calculations.

### Expense categorization

The former TF-IDF + Logistic Regression categorizer is removed. Expense categorization is now an agent/tool capability. Manual category selection remains available.

## 9. Financial Intelligence

### Financial Health

Use deterministic Python/domain services for:

- savings rate;
- debt ratio;
- budget adherence;
- emergency fund;
- cash flow;
- goal completion;
- expense stability;
- income stability;
- investment habit where data exists;
- financial trend.

The LLM can explain these results but cannot become their source of truth.

### Budget Intelligence

Use deterministic calculations for:

- budget usage;
- remaining budget;
- overspending;
- category performance;
- savings opportunities;
- trend analysis;
- optimization calculations.

Budget Intelligence is primarily a visualization/reporting module. The Copilot is the natural-language interaction layer.

### Anomaly Detection

Use lightweight explainable statistical/rule-based logic. Do not introduce a new anomaly ML platform.

### Deterministic finance rule

Authoritative numbers must originate from backend calculations or database queries, not from model arithmetic or model memory.

## 10. Groq + LangChain

### Groq

Groq is the ONLY LLM provider.

### LangChain Agent

Use LangChain to orchestrate the financial agent and tool calls.

```text
User
 ↓
Copilot
 ↓
LangChain Agent
 ↓
Groq
 ↓
Typed Financial Tools
 ↓
Deterministic Domain Services
```

### Tool classes

Read tools:
- expenses;
- budgets;
- income;
- goals;
- recurring;
- subscriptions;
- reports;
- health;
- anomaly;
- notifications;
- accounts;
- AA state/import.

Write tools:
- create/update/delete operations;
- approved import/sync operations.

Destructive tools:
- delete expense;
- delete budget;
- delete goal;
- delete recurring/subscription records;
- other irreversible operations.

### Confirmation

All write/destructive operations follow:

```text
Request
 ↓
Agent Plan
 ↓
Proposed Changes
 ↓
User Confirmation
 ↓
Tool Execution
```

### Clarification

The agent must ask questions when required information is missing.

No assumptions or hallucinations are allowed.

### Security

- Groq API key remains backend-only.
- Never expose Groq credentials to React.
- Do not use OpenAI.
- Do not add another LLM provider.
- Do not let the LLM mutate MongoDB directly.

## 11. OCR

Use the existing OCR implementation only for receipt extraction.

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

Do not add a separate document-processing platform.

---

## 12. Charts

Use the existing chart library.

Charts should cover only useful financial information:

- spending trends;
- category spending;
- budget usage;
- financial health trends;
- goal progress.

Do not add multiple chart libraries.

---

## 13. Testing

### Backend

Use Pytest to test:

- Clerk authentication;
- authorization;
- user ownership;
- expense CRUD;
- budget CRUD;
- income updates;
- health calculations;
- goals;
- recurring expenses;
- subscriptions;
- reports;
- anomalies;
- notifications;
- Copilot tools;
- agent confirmation flow;
- clarification behavior;
- multi-tool execution;
- partial failure handling;
- OCR;
- AA consent;
- AA data session;
- AA import;
- AA ownership.

### Frontend

Verify:

- routes;
- Clerk authentication state;
- dashboard sub-routes;
- forms;
- API integration;
- Copilot UI;
- proposed-action confirmation UI;
- loading/error states;
- responsive layouts;
- AA Sandbox flow.

### Agent test principle

Never mark an agent feature as passing merely because the LLM returns a plausible sentence. Verify that the correct tool was invoked and that the resulting state/data is correct.

## 14. Docker

Docker Compose may be used only to simplify local development.

Required services should remain minimal:

```text
MongoDB
Backend
Frontend
```

Setu AA Sandbox and Groq remain external services.

Do not introduce:

- Redis;
- Kafka;
- Kubernetes;
- message brokers;
- additional infrastructure

unless an existing core feature genuinely requires them.

---

## 15. Environment Variables

Keep secrets in `.env`.

Examples:

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

Exact Setu configuration names should match the implemented sandbox adapter and current Setu configuration.

Never commit real secrets.

Never expose backend secrets to the frontend.

---

## 16. Development Tools

```text
VS Code
Git
GitHub
Docker
Postman
```

These are development tools, not runtime dependencies.

---

## 17. Core Features That Must Not Break

The AI-first refactor must preserve:

1. Clerk authentication
2. Dashboard
3. Expense / Spending management
4. Budgets
5. Budget Intelligence visualization/reporting
6. Financial Health Score
7. Financial Health history/trends
8. Reports
9. Recurring expenses
10. Subscriptions
11. Anomaly detection
12. Goals
13. Receipt/OCR
14. AI Copilot Agent
15. Notifications
16. Setu AA Sandbox demonstration
17. Responsive UI

Expenses and Budgets move under Dashboard sub-routes; their functionality is not removed.

## 18. Explicitly Avoid

Do NOT introduce:

- custom JWT authentication;
- password hashing;
- local password authentication;
- OpenAI;
- multiple LLM providers;
- microservices;
- Kafka;
- Kubernetes;
- Redis without a real requirement;
- PostgreSQL alongside MongoDB;
- multiple frontend frameworks;
- multiple CSS frameworks;
- unnecessary AI frameworks;
- a second agent framework;
- unnecessary ML models;
- TF-IDF / Logistic Regression expense-classification infrastructure;
- production banking integrations;
- UPI;
- payment processing;
- direct bank credentials;
- live bank synchronization.

## 19. Technology Decision Rule

Before adding any dependency:

```text
Can the current stack solve it?
        ↓
      YES
        ↓
Use current stack

      NO
        ↓
Is the dependency essential to an existing
approved core feature?
        ↓
      YES
        ↓
Add the smallest suitable dependency

       NO
        ↓
Do not add it
```

---

## 20. Final Stack

```text
Frontend
React.js + Tailwind CSS

Authentication
Clerk

Backend
Python + FastAPI

Database
MongoDB

AI
LangChain Agent + Groq

Financial Logic
Deterministic Python/domain services

Account Aggregator
Setu AA Sandbox

OCR
Existing OCR implementation

Charts
Existing chart library

Testing
Pytest + existing frontend tests

Infrastructure
Docker Compose

Development
Git + GitHub + Postman
```

### Authentication rule

```text
Clerk
```

**No custom JWT authentication.**

### LLM rule

```text
LangChain Agent + Groq
```

**No OpenAI. No second LLM provider.**

### Agent rule

The agent is the interaction/orchestration layer. Domain services/tools remain the deterministic source of truth.

### AA rule

```text
Setu AA Sandbox
```

**Sandbox/demo integration only.**

## 21. Non-Negotiable Rule

**Simplify the implementation, not the product's core functionality.**

The target architecture is:

```text
User
 ↓
AI Copilot
 ↓
LangChain Agent
 ↓
Groq
 ↓
User-scoped Tools
 ↓
Deterministic Domain Services
 ↓
Repositories
 ↓
MongoDB
```

Primary navigation:

```text
CORE
- Dashboard
- Health Score
- Goals
- AI Copilot

INTEGRATIONS
- Account Aggregator
```

Dashboard sub-navigation:

```text
Overview
Analytics
Spending
Cash Flow
Budgets
Insights
Notifications
```

Any refactor must preserve end-to-end behavior, enforce Clerk user ownership, keep financial calculations deterministic, require confirmation for financial writes, and keep Setu AA explicitly sandbox/demo-only.

The final IntelliMoney stack should remain:

**small + explainable + secure + reliable + agentic + sandbox-integrated + interview-friendly.**

