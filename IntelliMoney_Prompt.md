# IntelliMoney — Agentic AI Repository Audit & Implementation Prompt

You are the lead software architect, senior full-stack engineer, security engineer, ML engineer and QA engineer responsible for auditing and bringing the existing IntelliMoney repository into alignment with the approved product specification.

## CRITICAL SOURCE-OF-TRUTH RULE

The repository root contains exactly three authoritative specification documents:

1. `IntelliMoney_PRD.md`
2. `IntelliMoney_TECHSTACK.md`
3. `IntelliMoney_DESIGN.md`

**ONLY trust these three documents as the product, technical and UI/UX specification.**

Do NOT treat any other repository document as authoritative, including:

- README files;
- old PRDs;
- old architecture documents;
- old implementation plans;
- TODO files;
- handoff documents;
- previous agent instructions;
- comments;
- generated documentation;
- old design documents;
- stale API documentation;
- previous AI-generated recommendations.

If another document conflicts with the three root specification documents, IGNORE the conflicting document.

The actual source code is the implementation to be audited, not the specification.

The three root documents define what the codebase SHOULD become.

---

# 1. PRIMARY OBJECTIVE

Audit the existing IntelliMoney GitHub repository and bring the implementation into alignment with:

```text
IntelliMoney_PRD.md
IntelliMoney_TECHSTACK.md
IntelliMoney_DESIGN.md
```

Do not blindly rewrite the project.

First understand the existing implementation.

Then identify:

- what already works;
- what partially works;
- what is broken;
- what is obsolete;
- what violates the approved tech stack;
- what violates the PRD;
- what violates the design specification;
- what is missing;
- what should be refactored;
- what should be removed.

Then implement the required changes incrementally.

---

# 2. NON-NEGOTIABLE ARCHITECTURE DECISIONS

## Authentication

**Clerk is the ONLY authentication system.**

The final application must NOT use:

- custom JWT;
- application-generated JWT;
- password hashing;
- local password authentication;
- custom login sessions;
- parallel authentication providers.

Remove/migrate legacy JWT/password authentication after tracing every dependency.

Do not keep JWT merely because it already exists.

Use Clerk for:

- sign up;
- sign in;
- sign out;
- session management;
- authenticated identity;
- protected frontend routes;
- backend identity validation;
- user-level authorization.

Every financial resource must be associated with the authenticated Clerk user.

---

# 3. ACCOUNT AGGREGATOR REQUIREMENT

Account Aggregator is now an approved feature, but ONLY in the following form:

**Setu AA Sandbox / mock demonstration integration.**

This is NOT a production banking integration.

Implement an AA-ready architecture supporting the sandbox demonstration flow:

```text
Connect Financial Data
        ↓
Create Consent
        ↓
Consent Pending
        ↓
Approval / Rejection
        ↓
Notification
        ↓
Approved
        ↓
Create Data Session
        ↓
Data Ready
        ↓
Fetch Sandbox Data
        ↓
Normalize
        ↓
Import Transactions
        ↓
Existing IntelliMoney Financial Pipeline
```

Setu-specific API logic must be isolated behind a dedicated Account Aggregator integration boundary.

Do NOT place Setu API calls directly inside React components or core financial services.

Preferred conceptual architecture:

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

If the repository already has an equivalent clean architecture, reuse it instead of blindly creating duplicate directories.

AA sandbox data must feed the existing transaction/categorization/analytics pipeline.

Do NOT create a second financial analytics system for AA data.

Clearly label the feature as:

**Setu AA Sandbox / Demo**

Do not claim production banking connectivity.

---

# 4. LLM REQUIREMENT

**Groq is the ONLY LLM provider.**

The final implementation must:

- use Groq for AI Copilot;
- retain LangChain if already required by the approved architecture;
- keep Groq credentials server-side;
- use backend financial data as the source of truth.

Absolutely do NOT introduce:

- OpenAI;
- Gemini;
- Anthropic;
- multiple LLM providers;
- unnecessary agent frameworks;
- unnecessary AI agents.

Do not allow the LLM to calculate authoritative financial numbers.

Deterministic backend financial calculations remain the source of truth.

---

# 5. ML REQUIREMENT

Preserve the approved ML implementation:

```text
TF-IDF
+
Logistic Regression
+
Rule/Keyword Fallback
```

Do not introduce new ML models unless a clear requirement exists in the three authoritative documents.

Do not replace the existing ML merely because another model might be technically better.

---

# 6. ARCHITECTURE RULE

The project must remain a maintainable modular monolith.

Preferred backend flow:

```text
Router
 ↓
Authentication / Authorization
 ↓
Service
 ↓
Repository
 ↓
MongoDB
```

Do NOT introduce:

- microservices;
- Kafka;
- Kubernetes;
- unnecessary queues;
- Redis without a real requirement;
- PostgreSQL alongside MongoDB;
- duplicate service layers;
- duplicate API systems;
- duplicate state-management systems.

---

# 7. FIRST PHASE — REPOSITORY DISCOVERY

Before modifying code, inspect the entire repository.

Determine:

### Frontend

- framework/version;
- routing;
- components;
- API client;
- authentication;
- state management;
- styling;
- charts;
- forms;
- pages/routes;
- error/loading handling.

### Backend

- FastAPI entry point;
- routers;
- services;
- repositories;
- models;
- schemas;
- authentication;
- authorization;
- middleware;
- database connection;
- ML implementation;
- OCR;
- Copilot;
- notification system;
- existing AA/banking code.

### Database

Identify:

- collections;
- schemas;
- indexes;
- user ownership;
- migration/setup mechanisms.

### Integrations

Find all:

- LLM integrations;
- authentication integrations;
- banking integrations;
- AA integrations;
- external APIs;
- OCR systems.

### Infrastructure

Inspect:

- Docker;
- Compose;
- environment configuration;
- startup scripts;
- deployment configuration;
- CI/CD.

---

# 8. SECOND PHASE — BUILD A GAP ANALYSIS

Create an internal audit before implementation.

Classify every major area as:

```text
COMPLIANT
PARTIALLY COMPLIANT
BROKEN
MISSING
OUT OF SCOPE
LEGACY
```

Audit at minimum:

```text
Authentication
Authorization
Expenses
ML Categorization
Budgets
Budget Intelligence
Financial Health
Health History
Goals
Reports
Recurring Expenses
Subscriptions
Anomaly Detection
OCR
Copilot
Notifications
Account Aggregator
Dashboard
Frontend Routes
Backend APIs
MongoDB
Security
Responsive UI
Loading States
Error States
Testing
Deployment
Environment Variables
Dependencies
Architecture
```

Do not implement until you understand the existing architecture.

---

# 9. THIRD PHASE — AUTHENTICATION MIGRATION

If JWT/password authentication currently exists:

1. Identify all authentication code.
2. Identify every route depending on it.
3. Identify user ID propagation.
4. Identify database ownership logic.
5. Introduce Clerk properly.
6. Migrate frontend authentication.
7. Migrate backend authentication/authorization.
8. Update user ownership.
9. Remove obsolete JWT/password code.
10. Verify every protected endpoint.

Do NOT leave two authentication systems active.

Final state:

```text
Clerk
 ↓
Authenticated User
 ↓
FastAPI
 ↓
Authorization
 ↓
User-Owned Financial Data
```

---

# 10. FOURTH PHASE — ACCOUNT AGGREGATOR IMPLEMENTATION

Implement Setu AA Sandbox only.

Do not implement production banking infrastructure.

Required logical capabilities:

```text
Create Consent
Get Consent Status
Handle Consent Approval
Handle Consent Rejection
Handle Notifications
Create Data Session
Fetch Sandbox Data
Normalize Financial Data
Import Transactions
```

Keep Setu credentials in environment variables.

Never expose:

- Setu secrets;
- backend credentials;
- Groq credentials;
- Clerk secret key

to the frontend.

Trace the complete AA flow end-to-end.

---

# 11. FIFTH PHASE — FINANCIAL PIPELINE

Verify that all transaction sources eventually converge into one pipeline:

```text
Manual Transaction
        │
        ├─────────────┐
        │             │
Setu AA Sandbox      │
        │             │
        └──────┬──────┘
               ↓
        Normalized Data
               ↓
        Categorization
               ↓
        MongoDB
               ↓
        Budgets
               ↓
    Financial Health
               ↓
          Dashboard
               ↓
      Recommendations
```

Do not create duplicated business logic for AA transactions.

---

# 12. SIXTH PHASE — GROQ AUDIT

Search the entire repository for:

```text
openai
OpenAI
OPENAI
gpt
GPT
anthropic
gemini
```

Remove unauthorized LLM dependencies or code paths.

Confirm:

```text
AI Copilot
 ↓
LangChain
 ↓
Groq
```

There must be no fallback to another LLM provider.

---

# 13. SEVENTH PHASE — TECH STACK AUDIT

Compare every dependency against `IntelliMoney_TECHSTACK.md`.

Identify:

- unnecessary dependencies;
- duplicate libraries;
- obsolete libraries;
- unauthorized frameworks;
- unused dependencies;
- conflicting dependencies.

Do not remove a dependency blindly.

First determine whether existing code depends on it.

Then remove only when safe.

Do not add a new library when the current approved stack can solve the requirement.

---

# 14. EIGHTH PHASE — DESIGN AUDIT

Use ONLY `IntelliMoney_DESIGN.md` for visual/UI requirements.

Audit:

- application shell;
- navigation;
- sidebar;
- dashboard;
- expense page;
- budget page;
- financial health;
- goals;
- reports;
- recurring;
- subscriptions;
- anomaly;
- OCR;
- Copilot;
- notifications;
- loading states;
- error states;
- empty states;
- responsive behavior;
- accessibility.

Do not redesign the product by inventing new features.

The design document explicitly prioritizes improving the experience of existing capabilities rather than adding product scope.

---

# 15. NINTH PHASE — API AUDIT

For every frontend API call:

1. Find the endpoint.
2. Verify HTTP method.
3. Verify request schema.
4. Verify authentication requirement.
5. Verify authorization.
6. Verify response schema.
7. Verify error handling.
8. Verify frontend response handling.
9. Test the complete request lifecycle.

Use:

```text
Frontend
 ↓
API
 ↓
FastAPI
 ↓
Service
 ↓
Repository
 ↓
MongoDB
 ↓
Response
 ↓
Frontend
```

Fix endpoint mismatches rather than creating duplicate endpoints.

---

# 16. TENTH PHASE — DATABASE AUDIT

Verify:

- user ownership;
- collection consistency;
- indexes;
- required fields;
- orphaned records;
- AA data ownership;
- financial score history;
- transaction references.

Every user-owned financial record must be isolated by Clerk user identity.

A user must never be able to access another user's data.

---

# 17. SECURITY AUDIT

Verify:

- Clerk authentication;
- authorization;
- input validation;
- CORS;
- secrets;
- error responses;
- logging;
- API credentials;
- Setu credentials;
- Groq credentials;
- Clerk secret;
- MongoDB credentials.

Never expose secrets.

Never log sensitive financial information unnecessarily.

Never trust a user-provided user ID when the authenticated Clerk identity is available.

---

# 18. TESTING STRATEGY

Run progressively:

### Level 1

Syntax/import validation.

### Level 2

Backend tests.

### Level 3

Frontend lint/type checks.

### Level 4

Frontend build.

### Level 5

API integration tests.

### Level 6

Authentication tests.

### Level 7

AA sandbox flow tests.

### Level 8

Critical end-to-end tests.

Critical flow:

```text
Clerk Login
 ↓
Dashboard
 ↓
Add Expense
 ↓
Categorization
 ↓
Budget Update
 ↓
Financial Health
 ↓
Dashboard
```

AA critical flow:

```text
Clerk Login
 ↓
Connect Financial Data
 ↓
Setu Sandbox Consent
 ↓
Approve
 ↓
Data Session
 ↓
Fetch Data
 ↓
Normalize
 ↓
Import Transaction
 ↓
Categorize
 ↓
Budget/Health Update
```

Copilot critical flow:

```text
Clerk Login
 ↓
Copilot
 ↓
Question
 ↓
Backend Financial Context
 ↓
LangChain
 ↓
Groq
 ↓
Answer
```

---

# 19. DO NOT BREAK EXISTING FUNCTIONALITY

Before changing a component/service, identify its consumers.

Never remove code merely because it appears old.

Trace:

```text
Frontend
 ↓
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

before deleting anything.

Do not change business logic unless the authoritative PRD requires it.

---

# 20. DO NOT INVENT REQUIREMENTS

If a feature is not present in:

```text
IntelliMoney_PRD.md
IntelliMoney_TECHSTACK.md
IntelliMoney_DESIGN.md
```

do not add it merely because:

- it sounds useful;
- another project uses it;
- an AI agent recommends it;
- a modern architecture would normally use it;
- a README mentions it;
- a previous developer planned it.

If genuinely necessary for implementation, prefer the smallest solution that remains within the approved scope.

---

# 21. DOCUMENTATION RECONCILIATION

After implementation, update only the three authoritative root documents if implementation details materially require clarification:

```text
IntelliMoney_PRD.md
IntelliMoney_TECHSTACK.md
IntelliMoney_DESIGN.md
```

Do not create competing specification documents.

The final documents and code must agree.

---

# 22. FINAL VALIDATION CHECKLIST

Before declaring completion, verify:

### Authentication

- [ ] Clerk works
- [ ] Sign up works
- [ ] Sign in works
- [ ] Sign out works
- [ ] Protected routes work
- [ ] Backend validates Clerk identity
- [ ] User authorization works
- [ ] No custom JWT remains
- [ ] No password hashing/authentication remains

### Account Aggregator

- [ ] Setu sandbox configured
- [ ] Consent creation works
- [ ] Consent status works
- [ ] Approval/rejection handled
- [ ] Notifications handled
- [ ] Data session works
- [ ] Sandbox data fetch works
- [ ] Data normalization works
- [ ] Imported transactions work
- [ ] Imported transactions use existing ML pipeline
- [ ] Secrets remain server-side
- [ ] UI clearly identifies sandbox/demo mode

### AI

- [ ] Groq works
- [ ] LangChain works where required
- [ ] No OpenAI
- [ ] No second LLM
- [ ] No hallucinated financial facts
- [ ] Backend calculations remain authoritative

### ML

- [ ] TF-IDF works
- [ ] Logistic Regression works
- [ ] Fallback works
- [ ] Expense creation does not fail when ML artifact is unavailable

### Financial Features

- [ ] Expenses
- [ ] Budgets
- [ ] Budget Intelligence
- [ ] Financial Health
- [ ] Health History
- [ ] Goals
- [ ] Reports
- [ ] Recurring Expenses
- [ ] Subscriptions
- [ ] Anomaly Detection
- [ ] OCR
- [ ] Notifications
- [ ] Dashboard

### Frontend

- [ ] No duplicate navigation
- [ ] Responsive
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Charts work
- [ ] Forms work
- [ ] API integration works
- [ ] Accessibility requirements respected

### Engineering

- [ ] No broken imports
- [ ] No broken endpoints
- [ ] No unauthorized dependencies
- [ ] No exposed secrets
- [ ] No unnecessary architecture
- [ ] Backend tests pass
- [ ] Frontend checks pass
- [ ] Build succeeds
- [ ] Critical flows verified

---

# 23. OUTPUT REQUIRED FROM YOU

Do not simply say "implementation complete."

At the end provide a concise implementation report containing:

## A. Repository Audit

```text
Existing Architecture:
Major Problems:
Legacy Systems:
Missing Features:
```

## B. Changes Made

Group by:

```text
Authentication
Account Aggregator
Backend
Frontend
ML
AI
Database
Security
Testing
Infrastructure
```

## C. Removed

List:

- removed JWT code;
- removed password authentication;
- removed unauthorized LLM integrations;
- removed unnecessary dependencies;
- removed obsolete banking code only where safe.

## D. Remaining Issues

Clearly list anything that cannot be completed because of:

- missing credentials;
- unavailable sandbox;
- external-service limitation;
- missing environment variable;
- existing code defect;
- test limitation.

Never claim something works if it was not actually verified.

## E. Verification

Report the actual commands/checks run and their results.

Example:

```text
Backend tests: PASS/FAIL
Frontend typecheck: PASS/FAIL
Frontend build: PASS/FAIL
API tests: PASS/FAIL
Clerk flow: VERIFIED/NOT VERIFIED
Setu Sandbox: VERIFIED/NOT VERIFIED
Groq Copilot: VERIFIED/NOT VERIFIED
```

## F. Final Compliance

Explicitly state whether the repository now complies with:

```text
IntelliMoney_PRD.md
IntelliMoney_TECHSTACK.md
IntelliMoney_DESIGN.md
```

If not, list every remaining discrepancy.

---

# FINAL COMMAND

Start with repository discovery and architecture audit.

Do NOT immediately start rewriting code.

Do NOT trust old repository documentation over the three root specification files.

Do NOT invent features.

Do NOT introduce JWT.

Do NOT introduce OpenAI.

Do NOT introduce another LLM.

Do NOT introduce production banking integration.

Use **Clerk + Groq + LangChain + Setu AA Sandbox + the existing approved ML/financial stack**.

Preserve existing functionality.

Fix the architecture where required.

Implement missing approved functionality.

Test every critical flow.

Only declare completion after actual verification.