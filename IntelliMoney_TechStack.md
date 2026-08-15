# IntelliMoney — Minimal Tech Stack

**Version:** 2.0

**Purpose:** Keep IntelliMoney technically simple, reliable, interview-friendly and easy to maintain while preserving every approved core feature, including the Setu AA Sandbox demonstration and Clerk authentication.

---

## 1. Core Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js | UI and client-side application |
| Styling | Tailwind CSS | Responsive UI and design system |
| Authentication | Clerk | Authentication, sessions and user identity |
| Backend | FastAPI | REST API and business logic |
| Language | Python | Backend + ML |
| Database | MongoDB | User and financial data |
| ML | scikit-learn | Expense categorization |
| Data Processing | Pandas + NumPy | ML preprocessing and financial calculations |
| NLP | TF-IDF | Expense-description features |
| Classifier | Logistic Regression | Expense category prediction |
| AI | Groq | Financial Copilot LLM |
| AI Orchestration | LangChain | Groq/Copilot integration |
| Account Aggregator | Setu AA Sandbox | Demonstration financial-data integration |
| OCR | Existing OCR library | Receipt data extraction |
| Charts | Existing chart library | Financial visualizations |
| Containers | Docker Compose | Simple local environment |
| Testing | Pytest + existing frontend tests | Verification |
| Version Control | Git + GitHub | Source control |

**Authentication is Clerk-only.**

Do not introduce:

- custom JWT;
- password hashing;
- local password authentication;
- another identity provider;
- a parallel authentication system.

---

## 2. Architecture

```text
React + Tailwind
       ↓
Clerk Authentication
       ↓
    FastAPI
       ↓
    Services
       ↓
  Repositories
       ↓
    MongoDB
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
       Financial Data
              ↓
         Normalization
              ↓
        ML Categorizer
              ↓
       Budgets / Health
              ↓
          Dashboard
```

### AI

```text
AI Copilot
    ↓
FastAPI
    ↓
Financial Context
    ↓
LangChain
    ↓
Groq
```

Keep this as a **modular monolith**.

Do not introduce microservices.

---

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
- business logic;
- financial calculations;
- ML integration;
- Copilot integration;
- OCR processing;
- Setu AA integration;
- notifications.

Use:

```text
Router
  ↓
Service
  ↓
Repository
  ↓
MongoDB
```

Do not create unnecessary layers or abstractions.

---

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

## 8. ML Stack

### Expense Categorization

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
```

Use:

- Pandas;
- NumPy;
- scikit-learn;
- TF-IDF;
- Logistic Regression.

Keep the existing rule/keyword fallback so missing ML artifacts do not break expense creation.

### ML training

```text
Labeled Dataset
 ↓
Preprocessing
 ↓
Train/Test Split
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Evaluation
 ↓
Saved Model
```

The model is trained separately, not on every API request.

Do not introduce new ML models without a clear product requirement.

---

## 9. Financial Intelligence

Do **not** use an LLM for deterministic financial calculations.

### Financial Health

Use Python-based deterministic calculations for:

- savings rate;
- debt ratio;
- budget adherence;
- emergency fund;
- cash flow;
- goal completion;
- expense stability;
- income stability;
- investment habit;
- financial trend.

Output:

```text
Score
Grade
Risk
Factor Contributions
Recommendations
Trend
```

### Budget Intelligence

Use deterministic calculations for:

- budget usage;
- remaining budget;
- overspending;
- category performance;
- recommendations.

### Anomaly Detection

Use lightweight statistical/rule-based logic.

Do not add another complex ML framework.

AA-imported transactions may participate in these calculations after normalization.

---

## 10. Groq + LangChain

### Purpose

Groq is the **only LLM provider**.

It is used for natural-language generation where appropriate, primarily the AI Financial Copilot.

```text
User Question
 ↓
FastAPI
 ↓
Retrieve relevant financial data
 ↓
Structured context
 ↓
LangChain
 ↓
Groq
 ↓
Natural-language response
```

### Rules

- Groq API key stays on the backend.
- Never expose the key in React.
- Do not use OpenAI.
- Do not add another LLM provider.
- Do not create multiple LLM abstraction providers unless genuinely required.
- Do not let the LLM invent financial numbers.
- Do not let the LLM replace deterministic calculations.
- Backend calculations remain the source of truth.

---

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

Use:

```text
Pytest
```

Test:

- Clerk authentication;
- authorization;
- expenses;
- categorization;
- budgets;
- financial health;
- goals;
- reports;
- recurring expenses;
- subscriptions;
- anomalies;
- notifications;
- Copilot;
- OCR;
- AA consent flow;
- AA notification flow;
- AA data-fetch flow;
- AA data normalization.

### Frontend

Use the project's existing testing setup.

Verify:

- routes;
- Clerk authentication state;
- forms;
- API integration;
- loading states;
- error states;
- responsive layouts;
- AA connection UI;
- consent states.

---

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
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
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

The tech-stack cleanup/refactor must preserve:

1. Clerk authentication
2. Expense management
3. ML expense categorization
4. Budgets
5. Budget Intelligence
6. Financial Health Score
7. Financial Health history/trends
8. Dashboard
9. Reports
10. Recurring expenses
11. Subscriptions
12. Anomaly detection
13. Goals
14. Receipt/OCR
15. AI Financial Copilot
16. Notifications
17. Setu AA Sandbox demonstration
18. Responsive UI

---

## 18. Explicitly Avoid

Do **not** introduce:

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
- unnecessary AI agents;
- unnecessary ML models;
- unnecessary third-party APIs;
- production banking integrations;
- UPI;
- payment processing;
- direct bank credentials;
- live bank synchronization.

---

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

ML
scikit-learn
Pandas
NumPy
TF-IDF
Logistic Regression

AI
LangChain + Groq

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

**No JWT.**

### LLM rule

```text
Groq
```

**No OpenAI. No second LLM provider.**

### AA rule

```text
Setu AA Sandbox
```

**Sandbox/demo integration only.**

---

## 21. Non-Negotiable Rule

**Simplify the implementation, not the product's core functionality.**

Any refactor, dependency removal, architecture change or UI redesign must first verify that the existing core feature continues to work end-to-end:

```text
Frontend
 ↓
Clerk
 ↓
API
 ↓
Service
 ↓
Database / ML / AI / AA Sandbox
 ↓
Response
 ↓
Frontend
```

No core feature should be removed merely to make the codebase smaller.

The final IntelliMoney stack should remain:

**small + explainable + secure + reliable + sandbox-integrated + interview-friendly.**