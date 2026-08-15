# IntelliMoney — Product Requirements Document (PRD)

**Version:** 2.0  
**Status:** Final Approved Product Scope  
**Product:** IntelliMoney — AI-Powered Financial Health & Personal Finance Platform

## 1. Product Vision

IntelliMoney is a personal financial analytics platform that lets users manage financial data, understand spending, create budgets and goals, evaluate financial health, detect unusual spending, track recurring expenses and subscriptions, connect to a **Setu Account Aggregator Sandbox demonstration flow**, and receive AI-powered financial guidance.

**Core principle:**

Enter/manage financial data → IntelliMoney organizes it → analyzes it → explains it → recommends practical actions.

IntelliMoney supports two sources of financial information:

1. Manually entered/demo financial data.
2. Account Aggregator data obtained through the **Setu AA Sandbox/mock environment** for demonstration.

The Account Aggregator implementation is **sandbox/demo only**. It must not be represented as a production banking integration.

### Scope decision

Production banking connectivity, UPI integration, live bank synchronization and payment processing are outside the product scope.

However, IntelliMoney will include an **AA-ready integration architecture using Setu AA Sandbox/mock data** so the complete consent → approval/rejection → data-ready → data-fetch demonstration flow can be shown without depending on real bank accounts.

The AA integration must be isolated behind a dedicated service/provider boundary so that it can later be replaced or extended without rewriting the core financial modules.

Authentication is handled entirely by **Clerk**.

IntelliMoney does **not** implement its own JWT authentication, password hashing, login credential storage or parallel authentication mechanism.

---

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
| Simplicity | Minimum technology and architecture required |
| Reliability | Make existing features work before improving them |
| Explainability | Scores/recommendations must be understandable |
| Privacy | Financial data is user-specific |
| Deterministic finance | Financial calculations do not depend on an LLM |
| AI where useful | Groq + LangChain power the Copilot |
| AA-ready | Setu AA Sandbox is supported for demonstration |
| No production banking | No live bank connectivity is required |
| Clerk authentication | Clerk is the only application authentication system |
| No custom JWT | Do not implement or maintain application-managed JWT authentication |
| Responsive | Mobile, tablet, laptop and desktop |
| Maintainability | Avoid duplicate services/routes/state systems |

---

## 4. Core Features

| Feature | Purpose | Implementation |
|---|---|---|
| Authentication | Secure access | Clerk |
| Dashboard | Financial overview | React + FastAPI |
| Expenses | Record/analyze spending | CRUD + MongoDB |
| Budgets | Spending limits | CRUD + deterministic calculations |
| Financial Health | 0–100 financial score | Weighted rule-based engine |
| Budget Intelligence | Budget analysis | Rule-based financial analysis |
| Expense Categorization | Automatic classification | TF-IDF + Logistic Regression + rule fallback |
| Reports | Financial analytics | Aggregated APIs + charts |
| Recurring Expenses | Track recurring commitments | Recurring expense service |
| Subscriptions | Track subscriptions | CRUD + analysis |
| Anomaly Detection | Detect unusual spending | Lightweight statistical/rule logic |
| Goals | Track savings targets | CRUD + progress calculations |
| Receipt/OCR | Extract receipt data | Existing OCR implementation |
| AI Copilot | Natural-language financial help | LangChain + Groq |
| Notifications | Financial alerts | In-app alert logic |
| Account Aggregator Sandbox | Demonstrate consented financial-data acquisition | Setu AA Sandbox/mock integration |
| Demo Data | Easy demonstration | Existing synthetic/demo dataset |

---

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
| Frontend | React.js | UI |
| Styling | Tailwind CSS / existing styling | Responsive design |
| Authentication | Clerk | User authentication and identity |
| Charts | Existing chart library | Visualization |
| Backend | FastAPI | REST APIs/business logic |
| Language | Python | Backend + ML |
| Database | MongoDB | Application data |
| ML | scikit-learn | Expense categorization |
| Data Processing | Pandas + NumPy | ML/financial calculations |
| NLP | TF-IDF | Transaction text features |
| Classifier | Logistic Regression | Category prediction |
| AI | Groq | Copilot LLM |
| AI Framework | LangChain | LLM orchestration |
| Account Aggregator | Setu AA Sandbox | Demonstration financial-data integration |
| OCR | Existing implementation | Receipt extraction |
| Containers | Docker/Compose if already used | Local environment |
| Source Control | Git/GitHub | Version control |
| Testing | Pytest + existing frontend tests | Verification |

**Rule:** Do not introduce another library when the current stack already solves the requirement.

---

## 7. Architecture

```text
React.js
   ↓
Clerk Authentication
   ↓
API Client
   ↓
FastAPI
   ↓
Routers
   ↓
Services
   ↓
Repositories
   ↓
MongoDB
```

### Financial intelligence

```text
Manual Data ─────────────┐
                         │
Setu AA Sandbox ─────────┤
                         ↓
                 Financial Data
                         ↓
                 Normalization
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   ML Categorizer     Budgets       Financial Health
        ↓                ↓                ↓
        └────────────────┼────────────────┘
                         ↓
                    Dashboard
                         ↓
                 Recommendations
```

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
Existing IntelliMoney Financial Pipeline
```

The Setu integration must remain isolated from core financial calculations.

### AI

```text
AI Copilot
    ↓
FastAPI
    ↓
Relevant Financial Data
    ↓
Structured Context
    ↓
LangChain
    ↓
Groq
    ↓
Natural-language Answer
```

---

## 8. Customer Journey

### Manual/demo flow

```text
Landing Page
 ↓
Sign Up / Sign In
 ↓
Clerk Authentication
 ↓
Dashboard
 ↓
Add/manage expenses
 ↓
Create budgets
 ↓
View analytics
 ↓
Check Financial Health
 ↓
Create goals
 ↓
Review recurring/subscriptions
 ↓
Ask AI Copilot
```

### Account Aggregator demonstration flow

```text
Dashboard
 ↓
Connect Financial Data
 ↓
Setu AA Sandbox
 ↓
Create Consent
 ↓
User Consent / Approval
 ↓
Consent Approved
 ↓
Data Session
 ↓
Setu Sandbox Financial Data
 ↓
Normalize Transactions
 ↓
Import into IntelliMoney
 ↓
Categorization / Analytics / Health
```

The AA flow is a demonstration/sandbox workflow and does not require real bank credentials.

---

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

## 10. Expense Categorization / ML

```text
Expense Description
 ↓
Text Cleaning
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Category + Confidence
 ↓
MongoDB
```

Example:

`Swiggy order → Food`

Possible categories:

- Food
- Shopping
- Transport
- Entertainment
- Bills
- Healthcare
- Education
- Travel
- Rent
- Utilities
- Other

If the trained model is unavailable or unsuitable, retain the existing keyword/rule-based fallback so expense creation does not fail.

AA-imported transactions use the same categorization mechanism.

---

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

**Technology:**

```text
React
 ↓
FastAPI
 ↓
Copilot Service
 ↓
LangChain
 ↓
Groq
```

Example questions:

- How much did I spend on food?
- Where am I overspending?
- Can I save ₹10,000 this month?
- Why did my health score decrease?
- Which budget should I reduce?
- How much should I save for my goal?

Preferred flow:

```text
Question
 ↓
Backend retrieves relevant financial data
 ↓
Structured context
 ↓
LangChain
 ↓
Groq
 ↓
Answer
```

### Non-negotiable AI rules

- Groq is the only LLM provider.
- OpenAI must not be introduced.
- No second LLM provider.
- Groq API credentials remain server-side.
- The LLM must not invent transactions.
- The LLM must not become the source of financial calculations.
- Backend calculations remain the source of truth.

---

## 21. Account Aggregator Sandbox Integration

### Purpose

Provide a realistic demonstration of consented financial-data acquisition without implementing production banking connectivity.

### Provider

**Setu AA Sandbox**

Setu's AA platform exposes sandbox/mock financial-data capabilities for FIU development and supports consent, notification and data-fetch flows.

### Required demonstration capabilities

1. Start AA connection.
2. Create consent request.
3. Display/redirect/embed the Setu consent experience where supported.
4. Handle approval/rejection.
5. Receive sandbox notification events.
6. Initiate data session after approved consent.
7. Fetch sandbox financial data.
8. Normalize the returned data.
9. Map it into IntelliMoney transactions.
10. Run existing categorization and financial analytics.

Setu's current documentation describes consent flow, data-fetch flow and notifications as the three major integration areas.

### Architectural rule

Do not place Setu API calls directly inside:

- dashboard components;
- expense components;
- financial-health services;
- budget services;
- ML services.

Use a dedicated AA integration boundary.

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

The exact repository structure must follow the existing project architecture if an equivalent structure already exists.

### Data normalization

```text
Setu Sandbox Data
       ↓
AA Mapper
       ↓
Normalized Transaction
       ↓
Expense Service
       ↓
Categorization
       ↓
MongoDB
       ↓
Analytics
```

Do not create a separate financial-data model for every downstream feature unless the existing implementation requires it.

### Security

Setu credentials must be stored in environment variables.

Never:

- commit credentials;
- expose credentials to React;
- log secrets;
- place secrets in frontend code.

### Sandbox-only labeling

The UI and documentation should clearly identify the feature as:

**Account Aggregator Sandbox / Demo**

It must not claim:

- production bank connectivity;
- live bank synchronization;
- live financial institution access;
- production AA certification.

---

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

Follow existing repository routes; do not duplicate pages.

```text
/
 /login
 /register
 /app/dashboard
 /app/expenses
 /app/budgets
 /app/reports
 /app/recurring
 /app/subscriptions
 /app/anomaly
 /app/health
 /app/budget-intelligence
 /app/goals
 /app/receipts
 /app/copilot
 /app/account-aggregator
```

The exact AA route should follow the existing repository routing conventions if an equivalent route already exists.

---

## 28. UI Requirements

Use the existing IntelliMoney landing-page theme:

- light/clean background;
- green primary accent;
- subtle gradients;
- dark navy text;
- rounded cards;
- restrained shadows;
- consistent spacing.

Every page must work on:

- mobile;
- tablet;
- laptop;
- desktop.

Avoid:

- horizontal overflow;
- duplicate navigation;
- blank pages;
- broken charts;
- fake financial data;
- misleading production banking claims.

---

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
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY / equivalent frontend Clerk configuration
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

- Clerk authentication;
- protected routes;
- user authorization;
- expense CRUD;
- categorization;
- budgets;
- health score;
- goals;
- reports;
- recurring expenses;
- subscriptions;
- anomaly detection;
- notifications;
- Copilot;
- OCR;
- AA consent creation;
- AA approval/rejection handling;
- AA sandbox notification handling;
- AA sandbox data fetch;
- AA data normalization;
- imported transaction creation;
- all routes;
- API calls;
- loading/error states;
- responsive layouts.

### Critical integration flow

```text
Clerk Authentication
 ↓
Account Aggregator Sandbox / Manual Expense
 ↓
Expense / Transaction
 ↓
Categorization
 ↓
Budget Update
 ↓
Financial Health
 ↓
Dashboard
 ↓
Recommendation / Alert
```

---

## 33. Definition of Done

- Clerk registration/login works.
- No custom JWT authentication remains.
- Protected routes work.
- User-level authorization works.
- Expense CRUD works.
- Categorization works with ML/fallback.
- Budgets and thresholds work.
- Health score is deterministic and 0–100.
- Health history works.
- Goals work and affect insights.
- Recurring/subscription features work.
- Reports use real stored data.
- Anomaly detection works.
- Copilot works with Groq.
- Groq is the only LLM provider.
- OCR works where implemented.
- Notifications work.
- Setu AA Sandbox demonstration flow works where credentials/configuration are available.
- AA consent states are handled correctly.
- AA sandbox data can be normalized into IntelliMoney financial data.
- AA credentials are never exposed to the frontend.
- No production banking integration is claimed.
- No UPI integration exists.
- No payment processing exists.
- No critical runtime/build errors.
- No broken imports/API mismatches.
- No exposed secrets.
- All pages are responsive.
- Project remains understandable and interview-friendly.

---

## 34. Final Product Scope

```text
Clerk Authentication
        ↓
Expense Management
        ↓
Setu AA Sandbox / Demo Data Import
        ↓
ML Expense Categorization
        ↓
Budget Management
        ↓
Budget Intelligence
        ↓
Financial Health
        ↓
Reports & Analytics
        ↓
Recurring Expenses
        ↓
Subscriptions
        ↓
Anomaly Detection
        ↓
Goals
        ↓
Receipt/OCR
        ↓
AI Financial Copilot
        ↓
Notifications
```

### Final rules

1. **Clerk is the only authentication provider.**
2. **Do not implement JWT authentication.**
3. **Setu AA Sandbox is the only Account Aggregator integration required.**
4. **AA integration is sandbox/demo-ready, not production banking integration.**
5. **Groq is the only LLM provider.**
6. **Do not add OpenAI.**
7. **Do not add another LLM provider.**
8. **Financial calculations remain deterministic.**
9. **Existing ML remains TF-IDF + Logistic Regression unless a clearly justified requirement changes it.**
10. **Do not introduce microservices, Kafka, Kubernetes or unnecessary infrastructure.**
11. **Do not invent features outside this PRD.**
12. **The three specification documents are the source of truth.**
13. **The goal is to make IntelliMoney reliable, secure, maintainable, demonstrable and interview-friendly.**