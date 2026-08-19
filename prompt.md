# INTELLIMONEY — AI-FIRST AGENTIC ARCHITECTURE REFACTOR, SIMPLIFICATION & FULL FEATURE INTEGRATION

You are the lead software architect, backend engineer, frontend engineer, AI engineer, LangChain engineer, security engineer and QA engineer responsible for refactoring the existing IntelliMoney repository into a clean AI-first personal finance platform.

This is a MAJOR ARCHITECTURAL SIMPLIFICATION, but it must preserve all approved product capabilities.

Do not begin by rewriting the repository.

First inspect the actual implementation, build a complete architecture/feature map, identify the current flows, identify redundant systems, then implement the refactor incrementally.

==================================================
1. ABSOLUTE SOURCE OF TRUTH
==================================================

ONLY trust these three specification documents in the repository ROOT:

1. IntelliMoney_PRD.md
2. IntelliMoney_TechStack.md
3. IntelliMoney_DESIGN.md

These are the authoritative product/technical/design specifications.

The USER-APPROVED CHANGES IN THIS PROMPT are the new approved modifications to those specifications.

Therefore:

AUTHORITATIVE INPUT =
1. The three root specification files
2. This explicit implementation/change request

Do NOT trust conflicting:
- README files
- old PRDs
- old TODO files
- architecture reports
- old AI prompts
- generated handoff documents
- previous agent reports
- stale comments
- old implementation plans

Do not invent product functionality outside the approved scope.

==================================================
2. PRIMARY PRODUCT DIRECTION
==================================================

The product is being simplified around one central principle:

THE AI COPILOT IS THE PRIMARY INTERACTION LAYER.

Instead of forcing users to manually navigate many independent financial-management pages, the user should be able to tell IntelliMoney what they want in natural language.

Example:

User:
"My monthly income is ₹60,000. I want to spend ₹5,000 on food and ₹5,000 on travel."

The agent should understand this and create a structured plan.

However:

The AI MUST NOT directly mutate data.

The workflow MUST be:

User Request
    ↓
LangChain Agent
    ↓
Reason about request
    ↓
Select required tools
    ↓
Generate proposed actions
    ↓
Show user what WILL change
    ↓
User confirms
    ↓
Execute tools
    ↓
Return results
    ↓
Refresh UI

==================================================
3. CRITICAL SAFETY RULE
==================================================

NO financial action may be executed directly by the LLM.

The LLM can:

- understand intent;
- reason;
- select tools;
- ask clarifying questions;
- prepare structured actions;
- explain results.

The tools perform:

- calculations;
- database reads;
- database writes;
- updates;
- deletes;
- financial computations;
- data imports.

The backend remains the source of truth.

For every write/mutation request:

User
→ Agent understands
→ Agent prepares plan
→ Agent shows plan
→ User confirms
→ Tool executes

Never:

User
→ LLM
→ direct database mutation

==================================================
4. NO ASSUMPTIONS / NO HALLUCINATIONS
==================================================

The agent MUST NOT guess missing financial information.

Examples:

User:
"Make me a budget."

Agent MUST ask:

"What is your monthly income?"

User:
"I want to save aggressively."

Agent MUST ask:

"How much would you like to target for savings?"

User:
"Set aside the rest."

Agent MUST calculate based on actual confirmed income and confirmed budget values.

If critical information is unavailable:

ASK.

Do not:
- invent income;
- invent expense values;
- invent goals;
- invent dates;
- invent account balances;
- invent transactions;
- fabricate database data;
- assume user intent for destructive actions.

==================================================
5. REMOVE THE OLD ML-CENTRIC ARCHITECTURE
==================================================

The user explicitly wants OPTION B:

REMOVE THE EXISTING ML EXPENSE-CATEGORIZATION MODEL.

Therefore, simplify the architecture by removing unnecessary scikit-learn/TF-IDF/Logistic Regression expense categorization.

Do NOT keep the ML pipeline merely because it already exists.

Audit and remove, where no longer used:

- TF-IDF categorization
- Logistic Regression classifier
- expense_classifier.joblib
- ML training pipeline
- ML-specific service layers
- unnecessary scikit-learn dependency
- unnecessary ML dataset/training artifacts
- duplicate rule/model categorization infrastructure

Do NOT remove deterministic financial calculations.

Financial calculations remain normal backend/business logic.

The AI agent can use a categorization tool where natural-language classification is required.

The final architecture should therefore be:

Groq
+
LangChain Agent
+
Deterministic Financial Tools
+
MongoDB

instead of:

Multiple ML services
+
multiple intelligence engines
+
LLM
+
duplicated business logic.

Do not replace deterministic financial calculations with LLM reasoning.

==================================================
6. NEW AI COPILOT ARCHITECTURE
==================================================

The Copilot must become a TRUE LANGCHAIN AGENT.

Conceptual architecture:

React Copilot UI
        ↓
FastAPI Copilot Endpoint
        ↓
LangChain Agent
        ↓
Groq LLM
        ↓
Tool Registry
        ↓
Financial Tools
        ↓
MongoDB / deterministic services
        ↓
Tool Result
        ↓
Agent
        ↓
Final Response

The LLM is the reasoning/orchestration layer.

Tools are the action/data layer.

MongoDB is the source of truth.

==================================================
7. GROQ ONLY
==================================================

Groq is the ONLY LLM provider.

Do NOT introduce:
- OpenAI
- Gemini
- Anthropic
- multiple LLM providers

Search the repository for old providers and remove obsolete integrations/dependencies.

The final AI stack must be:

LangChain
+
LangChain Agent
+
Groq

No second LLM provider.

==================================================
8. LANGCHAIN AGENT DESIGN
==================================================

Implement a proper LangChain agent using the project's compatible LangChain APIs.

The agent should be able to:

1. Understand user intent.
2. Inspect available user data.
3. Determine missing information.
4. Ask clarifying questions.
5. Plan tool calls.
6. Produce a structured proposed-action response.
7. Wait for user confirmation.
8. Execute approved tool calls.
9. Observe tool results.
10. Continue reasoning where necessary.
11. Return a clear result.

The tool layer MUST be strongly typed and validated.

Never expose raw database access directly to the LLM.

==================================================
9. TOOL ARCHITECTURE
==================================================

Create a clean domain-oriented tool system.

The exact directory structure must follow the repository's existing architecture if a clean equivalent already exists.

Conceptually:

backend/
  app/
    agent/
      agent.py
      prompts.py
      state.py
      tool_registry.py
    tools/
      expenses.py
      budgets.py
      income.py
      goals.py
      recurring.py
      subscriptions.py
      reports.py
      health.py
      budget_intelligence.py
      notifications.py
      aa.py
      accounts.py
      transactions.py

Do NOT blindly create duplicate services if equivalent domain services already exist.

Tools should call deterministic application services.

The agent should NOT directly contain business logic.

==================================================
10. TOOL CATEGORIES
==================================================

The agent must have access to ALL approved financial operations.

### EXPENSE TOOLS

Read:
- get expenses
- get expense by ID
- search expenses
- filter expenses
- summarize spending
- get spending by category
- get spending by date range

Write:
- create expense
- update expense
- delete expense

### BUDGET TOOLS

Read:
- list budgets
- get budget
- get budget usage
- get remaining budget
- compare budget vs actual

Write:
- create budget
- update budget
- delete budget

### INCOME TOOLS

Read:
- get monthly income
- get income history

Write:
- set/update income

### GOAL TOOLS

Read:
- list goals
- get goal
- get progress
- get goal history

Write:
- create goal
- update goal
- delete goal
- update goal progress

### RECURRING EXPENSE TOOLS

Read:
- list recurring expenses
- get upcoming recurring expenses

Write:
- create
- update
- delete

### SUBSCRIPTION TOOLS

Read:
- list subscriptions
- get renewal dates
- get total subscription cost

Write:
- create
- update
- delete

### FINANCIAL HEALTH TOOLS

Read/calculate:
- calculate health score
- get health history
- get trends
- get risk
- get factor contributions
- get recommendations

IMPORTANT:
Financial health calculations must remain deterministic backend calculations.

The LLM only explains/orchestrates them.

### BUDGET INTELLIGENCE TOOLS

Use deterministic backend calculations for:

- budget score
- category analysis
- potential savings
- risk
- trend analysis
- opportunities
- optimization calculations

The Copilot becomes the INTERACTION layer for Budget Intelligence.

Budget Intelligence UI becomes primarily visualization/reporting.

### REPORT TOOLS

Read:
- spending reports
- income reports
- savings reports
- cash-flow reports
- category reports
- date-range reports

### ANOMALY TOOLS

Read:
- detect unusual spending
- list anomalies
- explain anomaly

### NOTIFICATION TOOLS

Read:
- list notifications
- unread notifications

Write:
- mark notification read

### ACCOUNT / BANK TOOLS

The AI agent should be able to operate approved account-management functions such as:

- list connected accounts
- view account state
- check connection status
- check sync state
- check import state
- request approved sync
- review import status

Do NOT expose raw credentials.

### ACCOUNT AGGREGATOR TOOLS

The agent should be able to:

- check AA sandbox connection state
- create sandbox consent
- check consent status
- approve sandbox consent where the demo flow permits
- reject consent
- create data session
- check data-session status
- fetch sandbox data
- import approved sandbox data
- inspect import results

The agent must clearly tell the user when data is SANDBOX/DEMO.

==================================================
11. READ TOOLS VS WRITE TOOLS
==================================================

Categorize tools:

READ-ONLY:
No confirmation required.

WRITE:
Require confirmation.

DESTRUCTIVE:
Require especially clear confirmation.

For example:

User:
"How much did I spend on food?"

Agent:
→ read tools
→ answer immediately.

User:
"Set my food budget to ₹5,000."

Agent:
→ prepare change
→ ask confirmation
→ execute after confirmation.

User:
"Delete all my expenses from July."

Agent:
→ summarize exactly what would be deleted
→ require explicit confirmation
→ execute only after confirmation.

==================================================
12. CONFIRMATION PROTOCOL
==================================================

The confirmation experience must be structured.

Example:

User:
"My monthly income is ₹60,000. I want to spend ₹5,000 on food and ₹5,000 on travel."

Agent:

"I understood:
• Monthly income: ₹60,000
• Food budget: ₹5,000
• Travel budget: ₹5,000

You asked to save the remaining ₹50,000.

Planned changes:
1. Set monthly income to ₹60,000.
2. Create/update Food budget to ₹5,000.
3. Create/update Travel budget to ₹5,000.
4. Set savings target/plan for the remaining amount based on your response.

Would you like me to apply these changes?"

But the agent MUST NOT assume that the remaining ₹50,000 should become a formal savings goal.

It must ask:

"You said you want to save the rest. Should I create a ₹50,000 savings goal/target, or should I only record it as the planned monthly savings amount?"

Then wait for confirmation.

==================================================
13. MULTI-STEP TOOL EXECUTION
==================================================

After confirmation, the agent can execute multiple tools.

Example:

set_income(60000)
create_or_update_budget(food, 5000)
create_or_update_budget(travel, 5000)
create_or_update_savings_plan(...)

Execution should be:

- validated;
- transactional where possible;
- traceable;
- idempotent;
- safe against duplicate execution.

If one operation fails:

Do not claim all operations succeeded.

Report:

- completed operations
- failed operation
- reason
- rollback/transaction behavior where possible

==================================================
14. AGENT MEMORY / CONTEXT
==================================================

The agent must understand the current conversation.

Example:

User:
"My income is 60,000."

Assistant:
"How much do you want for food?"

User:
"5,000."

The agent should retain this context during the conversation.

Do NOT create uncontrolled persistent memory.

Persist financial facts only when the user explicitly confirms a tool action.

The database remains the source of truth.

==================================================
15. DATABASE AS EXTERNAL KNOWLEDGE SOURCE
==================================================

The user explicitly wants the agent to access the WHOLE financial database as an external knowledge base.

Implement this using secure tools.

The agent should be able to retrieve:

- expenses
- budgets
- income
- goals
- recurring expenses
- subscriptions
- financial health
- reports
- notifications
- account state
- AA import state
- transaction history

Do NOT give the LLM direct MongoDB access.

Do NOT expose database connection details.

Use authenticated, user-scoped tools.

Every query MUST automatically constrain data to the authenticated user.

A user must never be able to ask the agent to retrieve another user's data.

==================================================
16. NATURAL LANGUAGE FINANCIAL COMMANDS
==================================================

The Copilot should support requests such as:

"How much did I spend this month?"

"How much did I spend on food?"

"Where am I overspending?"

"Set my food budget to ₹5,000."

"Create a goal to save ₹50,000."

"How much can I save this month?"

"My salary is ₹60,000. Help me create a monthly plan."

"Add ₹1,500 for groceries today."

"Delete the ₹2,000 transaction from yesterday."

"What subscriptions renew this month?"

"Why did my financial health score fall?"

"Show my last three months of spending."

"Analyze my recurring expenses."

"Import my approved AA sandbox data."

"Sync my financial data."

"Show me my financial risk."

"Create a budget based on my spending."

For ambiguous or incomplete requests, ASK instead of guessing.

==================================================
17. SUGGESTED QUESTIONS
==================================================

The Copilot UI must show approximately 4–6 suggested questions.

Suggestions should be contextual/dynamic based on the user's available financial data.

Examples:

"How much did I spend this month?"

"Where am I overspending?"

"Create a budget for me"

"How can I reach my savings goal?"

"Why did my health score change?"

"Analyze my subscriptions"

"Plan my ₹60,000 monthly income"

Do not show meaningless static suggestions when the user has no relevant data.

Prefer suggestions based on current financial state.

==================================================
18. COPILOT UI
==================================================

The Copilot should become a primary application experience.

The page should contain:

- conversation history
- user messages
- agent responses
- tool/action plan cards
- confirmation UI
- execution status
- results
- suggested questions
- errors
- retry
- clear conversation if already supported

For proposed write operations, show a structured "Proposed Changes" component.

Example:

PROPOSED CHANGES

Income
₹60,000 / month

Budgets
Food — ₹5,000
Travel — ₹5,000

Savings
Needs clarification

[Confirm Changes]
[Cancel]

Do not hide important proposed operations inside normal conversational text.

==================================================
19. COPILOT SHOULD NOT BECOME A CHAT-ONLY DEMO
==================================================

The agent MUST actually use tools.

A response such as:

"Sure, I can help create that budget."

without calling the budget tool is NOT acceptable.

Likewise:

"Your spending is ₹15,000."

must come from an actual database query/tool result.

The agent must never fabricate tool results.

==================================================
20. SIMPLIFY CORE SIDEBAR
==================================================

Current CORE navigation contains too many independent financial operations.

Replace it with:

CORE

Dashboard
Health Score
Goals
AI Copilot

Remove from the left sidebar:

Expenses
Budgets
Budget Optimizer if it is currently treated as an independent top-level financial module unless explicitly preserved by the approved layout.

Do not delete functionality.

Move it into Dashboard sub-navigation and/or Copilot tools.

==================================================
21. DASHBOARD NAVIGATION
==================================================

Dashboard becomes the detailed structured financial workspace.

Use:

/app/dashboard

with sub-navigation such as:

Overview
Analytics
Spending
Cash Flow
Budgets
Insights
Notifications

Preserve useful dashboard visualizations.

The dashboard is where users can inspect structured data.

Copilot is where users can request and perform actions naturally.

==================================================
22. EXPENSE ROUTE MIGRATION
==================================================

Current independent route:

/app/expenses

Move the functionality to:

/app/dashboard/spending

This is an EXACT ROUTE MIGRATION.

The Spending page should become a polished dashboard subsection.

It should support:
- recent spending
- transactions
- filters
- create expense
- edit expense
- delete expense
- categories
- payment methods
- dates
- totals
- relevant visualizations

Do not simply embed the old page unchanged.

Refactor it to match the Dashboard visual system.

==================================================
23. BUDGET ROUTE MIGRATION
==================================================

Current independent route:

/app/budgets

Move functionality to:

/app/dashboard/budgets

Improve the layout so it naturally belongs inside Dashboard.

It should support:
- budgets
- current usage
- limits
- categories
- create
- edit
- delete
- budget performance
- relevant visualization

Do not remove functionality.

==================================================
24. REMOVE BUDGETS / EXPENSES FROM SIDEBAR
==================================================

Do NOT keep duplicate links.

Bad:

CORE
Dashboard
Expenses
Budgets
AI Copilot

Correct:

CORE
Dashboard
Health Score
Goals
AI Copilot

Dashboard contains:

Overview
Analytics
Spending
Cash Flow
Budgets
Insights
Notifications

==================================================
25. HEALTH SCORE
==================================================

KEEP Health Score in the left sidebar.

Health Score remains a dedicated visualization/reporting module.

Keep:
- overview
- score
- factor contribution
- risk
- history
- trends
- recommendations

Calculations remain deterministic.

The agent can:
- calculate it
- explain it
- compare it
- identify factors
- suggest improvements
- execute approved financial changes

Do not make the score itself LLM-generated.

==================================================
26. GOALS
==================================================

KEEP Goals in the left sidebar.

Users can manage goals in TWO ways:

1. Manually through the Goals UI.
2. Through the AI Copilot.

Both must use the SAME backend goal service.

The agent can:
- create goal
- update goal
- delete goal
- update progress
- explain progress
- recommend actions

Manual UI remains functional.

Do not remove goal pages merely because the agent can perform the same operations.

==================================================
27. BUDGET INTELLIGENCE
==================================================

KEEP Budget Intelligence functionality.

But change its role.

It becomes:

DASHBOARD VISUALIZATION / REPORTING

The user should inspect:

- budget score
- category breakdown
- potential savings
- risk
- trends
- opportunities
- optimization results

The Copilot becomes the interaction layer.

Examples:

User:
"Reduce my food spending."

Agent:
→ calls relevant budget/spending tools
→ analyzes data
→ proposes change
→ asks confirmation
→ executes.

Do not maintain a second conversational AI system just for Budget Intelligence.

==================================================
28. INTEGRATIONS SIDEBAR
==================================================

Replace current integration navigation:

Bank Accounts
AA Sandbox
Data Sync

with:

INTEGRATIONS

Account Aggregator

The agent handles:

- bank accounts
- synchronization
- imports
- connection state
- account status

Do not delete backend capabilities.

They become agent tools / secondary account management where needed.

==================================================
29. SETU AA SANDBOX ROLE
==================================================

AA Sandbox remains a demonstration page.

It is NOT the main user workflow.

The user can open:

Account Aggregator

and see:

SETU AA SANDBOX / DEMO

Clearly display:

"This is sandbox/demo financial data. It is not connected to real bank accounts."

The user can:

- create consent
- approve/reject
- create data session
- inspect sandbox state
- optionally import the resulting transactions

IMPORTANT USER DECISION:

If the user APPROVES the AA consent and the sandbox data is available, the approved sandbox data should be imported into the user's financial system according to the product flow.

Imported data must update the SAME financial sources used by:

Expenses
Budgets
Dashboard
Health Score
Reports
Analytics
Goals where relevant

If the user rejects the consent:
NO financial data should be imported.

If the user does not approve:
NO financial data should be imported.

Do not silently import data without the required user approval.

==================================================
30. AA SANDBOX CURRENT BUG
==================================================

The current live UI shows:

Consent:
APPROVED

Data session:
READY

Then:

Fetch Sandbox Transactions
→ "Failed to fetch sandbox data"

Sync History also shows:

"Active consent not found for this account"

This is a confirmed current functional issue.

Do NOT hide it.

Determine the actual root cause.

Audit:

- AA consent ownership
- consent ID
- consent handle
- data session ID
- user ID
- bank account ID
- provider account ID
- consent_handle persistence
- ObjectId/string conversions
- session ownership
- provider adapter
- mock fallback
- Setu sandbox configuration
- import mapping
- sync-service expectations

Find the exact mismatch.

==================================================
31. AA SANDBOX VS MOCK PROVIDER
==================================================

The current code appears to have both:

SetuSandboxProvider
and
MockBankProvider.

Do NOT blindly remove MockBankProvider.

Determine:

- where it is required for tests
- where it is used for demo fallback
- whether the final AA page accidentally creates Setu consent state but tries to fetch through a separate mock-account identity
- whether IDs are inconsistent

If the sandbox is intended to use deterministic demo data:
make the flow internally consistent.

If real Setu sandbox credentials are configured:
correctly use the Setu sandbox data flow where supported.

Never claim demo data is live banking data.

==================================================
32. SETU DATA IMPORT SEMANTICS
==================================================

Imported AA transactions MUST become normal financial transactions for the user.

They should flow through the same application services as manual transactions.

Example:

Setu sandbox transaction
→ normalize
→ transaction/expense store
→ categorization
→ budgets
→ dashboard
→ health
→ reports

Do not maintain an isolated "AA analytics" engine.

==================================================
33. AI ACCESS TO AA DATA
==================================================

After AA import, the Copilot should be able to answer:

"How much did I spend after importing my account?"

"What changed in my spending?"

"Which categories increased?"

"How does my financial health look?"

"Show me my imported transactions."

These answers must come from actual database/tool results.

==================================================
34. CORE FUNCTIONALITY MUST REMAIN
==================================================

The simplification must NOT remove:

- Dashboard
- Spending
- Budgets
- Health Score
- Goals
- Budget Intelligence
- Copilot
- Reports
- Recurring
- Subscriptions
- Anomaly
- Receipts/OCR
- Notifications
- Account Aggregator
- financial analytics

Only the navigation and interaction model are being simplified.

==================================================
35. ROUTE COMPATIBILITY
==================================================

Preferred new routes:

/app/dashboard
/app/dashboard/overview
/app/dashboard/analytics
/app/dashboard/spending
/app/dashboard/cashflow
/app/dashboard/budgets
/app/dashboard/insights
/app/dashboard/notifications

Existing legacy routes:

/app/expenses
/app/budgets

should redirect to their new equivalents ONLY if backward compatibility is desirable.

Do NOT keep duplicate page implementations.

The new route should own the implementation.

==================================================
36. UI CLEANUP
==================================================

Use IntelliMoney_DESIGN.md as the design source.

Do not create a new design language.

The current screenshots show excessive nested navigation and large empty areas.

Simplify:

- sidebar
- secondary navigation
- page hierarchy
- cards
- spacing
- empty states
- loading states

The Copilot should feel like a central product feature, not an isolated chatbot.

==================================================
37. REMOVE REDUNDANT INTELLIGENCE SYSTEMS
==================================================

Audit and consolidate:

- ML categorization
- old AI services
- duplicate recommendation engines
- duplicate budget intelligence logic
- duplicate Copilot logic
- old agent implementations
- LangGraph if no longer needed
- old OpenAI integrations
- unused vector/search systems
- duplicate tool systems

Do NOT remove deterministic business services.

The final architecture should have a clear separation:

Agent
↓
Tools
↓
Domain Services
↓
Repositories
↓
MongoDB

==================================================
38. DELETE UNUSED FILES
==================================================

Perform a complete dead-code audit.

Delete only files proven unused.

For every deletion:
- search imports
- search dynamic imports
- search routes
- search configuration references
- search build references

Pay particular attention to files associated with:

- old ML
- old AI implementations
- old authentication
- duplicate routes
- duplicate pages
- old budget pages
- old expense pages
- obsolete bank/sync pages if completely superseded

Do not delete features merely because they were moved.

==================================================
39. DEPENDENCY CLEANUP
==================================================

Remove dependencies that become genuinely unused.

Likely candidates MUST be evaluated, not blindly removed:

- scikit-learn
- training-only ML dependencies
- old LLM integrations
- unused LangChain modules
- duplicate AI frameworks

Do not remove LangChain.

Do not remove Groq.

Do not remove MongoDB dependencies.

Do not remove Clerk.

==================================================
40. API CLEANUP
==================================================

Do not create duplicate endpoints merely to support the new UI.

Reuse existing services/endpoints where possible.

If endpoint consolidation is required:
- migrate all consumers
- remove old endpoint only after proving unused
- preserve compatibility where appropriate

Document actual API changes.

==================================================
41. PERFORMANCE
==================================================

Avoid:

- duplicate agent calls
- duplicate tool execution
- repeated database queries
- repeated dashboard loads
- infinite polling
- repeated clerk-sync
- unnecessary full-page reloads

Cache or memoize where appropriate, but do not introduce unnecessary infrastructure.

==================================================
42. AGENT SECURITY
==================================================

Every tool receives the authenticated Clerk user context.

The agent cannot:

- query another user's data
- execute another user's action
- access secrets
- access raw MongoDB
- access raw Setu credentials
- access Groq credentials

Tool interfaces must enforce user ownership.

Do not trust user-provided user IDs.

==================================================
43. AGENT TOOL VALIDATION
==================================================

Each tool must validate:

- input schema
- amount ranges
- dates
- IDs
- ownership
- required values
- conflicting records

Example:

create_budget(category="food", limit=-5000)

must be rejected by tool validation.

The LLM must never bypass tool validation.

==================================================
44. FINANCIAL CALCULATION RULE
==================================================

Never ask Groq to calculate authoritative financial numbers.

For example:

User:
"I earn ₹60,000 and spend ₹5,000 on food and ₹5,000 on travel. What remains?"

The agent can understand the request, but the backend calculation/tool should calculate:

₹50,000

not the LLM.

LLM:
reasoning/orchestration/explanation

Backend:
truth/calculation/mutation

==================================================
45. TESTING REQUIREMENTS
==================================================

Add agent/tool tests.

Test:

1. Tool schema validation
2. User ownership
3. Read tools
4. Write tools
5. Confirmation flow
6. Cancel flow
7. Missing-information flow
8. Multi-tool execution
9. Partial failure
10. Duplicate execution prevention
11. Conversation context
12. Financial calculation correctness
13. No-hallucination behavior

Example:

User:
"Make me a budget."

Expected:
Agent asks for income.

User:
"My income is ₹60,000."

Expected:
Agent asks remaining critical information rather than guessing.

User:
"Food ₹5,000, Travel ₹5,000."

Expected:
Agent proposes changes and asks confirmation.

User confirms.

Expected:
Tools execute.

==================================================
46. AA TESTING
==================================================

Test:

Create consent
→ approve
→ create data session
→ fetch/import
→ verify transactions
→ verify dashboard
→ verify budgets
→ verify health
→ reject
→ verify no import

Test ownership:

User A cannot access User B's consent/session/import.

==================================================
47. FRONTEND TESTING
==================================================

Test:

/app/dashboard
/app/dashboard/spending
/app/dashboard/budgets
/app/health
/app/goals
/app/copilot
/app/budget-intelligence
/app/aa-sandbox

Direct refresh MUST work.

No Vercel 404.

No blank page.

No redirect loops.

==================================================
48. MANUAL USER FLOW
==================================================

EXPECTED FINAL USER EXPERIENCE:

NEW USER

Landing
→ Sign Up
→ Clerk
→ Account sync
→ Connect Account

Connect Account:
[Connect Account]
[Skip for now]

Skip:
→ Dashboard

Connect:
→ Setu AA Sandbox
→ consent
→ approve
→ data session
→ import
→ Dashboard

EXISTING USER

Login
→ Clerk
→ account sync
→ Dashboard

DASHBOARD

Overview
Analytics
Spending
Cash Flow
Budgets
Insights
Notifications

SIDEBAR

CORE
Dashboard
Health Score
Goals
AI Copilot

INTEGRATIONS
Account Aggregator

No Expenses item in sidebar.
No Budgets item in sidebar.
No Bank Accounts item in sidebar.
No Data Sync item in sidebar.

==================================================
49. FINAL AGENT EXPERIENCE
==================================================

Examples:

User:
"How much did I spend on food this month?"

Agent:
→ read spending tool
→ answer with real database result.

User:
"I spend too much on subscriptions."

Agent:
→ inspect subscriptions
→ summarize
→ suggest actions.

User:
"Cancel my Netflix subscription."

Agent:
→ identify subscription
→ show proposed deletion
→ ask confirmation
→ execute delete tool.

User:
"My monthly income is ₹60,000."

Agent:
→ record/prepare income update
→ show proposed change
→ ask confirmation.

User:
"I want food ₹5,000, travel ₹5,000 and save the rest."

Agent:
→ knows income if already confirmed
→ if savings amount/goal semantics are ambiguous, ask
→ construct proposed changes
→ confirmation
→ execute tools
→ refresh dashboard.

User:
"Why did my health score go down?"

Agent:
→ health tool
→ factor data
→ explanation
→ suggested actions.

User:
"Import my AA sandbox data."

Agent:
→ inspect AA state
→ if consent not approved, explain next step
→ if approved, import approved sandbox data
→ confirm results.

==================================================
50. DOCUMENTATION RECONCILIATION
==================================================

After implementation:

Update the three authoritative documents ONLY if necessary so that they accurately describe the new approved architecture.

The final documentation must reflect:

- AI-first Copilot
- LangChain Agent
- Groq-only LLM
- tool-based execution
- confirmation-before-write
- no ML expense classification
- simplified sidebar
- Dashboard subroutes
- Goals retained
- Health Score retained
- Budget Intelligence visualization/reporting
- Setu AA Sandbox demonstration
- same transaction pipeline for AA imports

Do not create competing specification documents.

==================================================
51. FINAL CLEANUP RULE
==================================================

The final system should be simpler than the current system.

Target:

BEFORE

Many pages
+
many intelligence engines
+
separate ML
+
separate budget intelligence
+
chatbot
+
multiple financial workflows

AFTER

Dashboard
+
Health Score
+
Goals
+
AI Copilot Agent
+
Budget Intelligence Visualization
+
Setu AA Sandbox

with:

Agent
↓
Tools
↓
Domain Services
↓
MongoDB

The product should feel smaller, clearer and more powerful.

==================================================
52. FINAL REPORT
==================================================

Return:

# INTELLIMONEY AI-FIRST REFACTOR REPORT

## 1. Architecture Before

Describe the major redundant systems.

## 2. Architecture After

Show:

User
↓
Copilot
↓
LangChain Agent
↓
Groq
↓
Tools
↓
Domain Services
↓
MongoDB

## 3. Removed

List:
- ML systems
- dependencies
- obsolete AI systems
- duplicate pages
- duplicate routes
- duplicate services
- obsolete navigation

## 4. New Agent Tools

List every tool.

## 5. Confirmation System

Explain read vs write vs destructive tools.

## 6. User Context

Explain database-backed secure user-scoped knowledge access.

## 7. Sidebar

Show final structure.

## 8. Dashboard

Show final route structure.

## 9. Copilot

Show supported capabilities.

## 10. Setu AA

Explain:
- sandbox purpose
- consent flow
- import flow
- rejection behavior
- demo vs real data
- current bug and fix

## 11. Tests

Backend:
PASS/FAIL

Frontend:
PASS/FAIL

Agent tools:
PASS/FAIL

Agent confirmation:
PASS/FAIL

AA:
PASS/FAIL

Existing user:
PASS/FAIL

New user:
PASS/FAIL

Skip:
PASS/FAIL

## 12. Files Deleted

Every deleted file with reason.

## 13. Files Changed

Every changed file with reason.

## 14. Remaining Issues

Rank:

P0
P1
P2
P3
P4

## 15. Specification Compliance

PRD:
COMPLIANT / NOT COMPLIANT

TECHSTACK:
COMPLIANT / NOT COMPLIANT

DESIGN:
COMPLIANT / NOT COMPLIANT

## 16. Final Status

AI-FIRST ARCHITECTURE:
PASS/FAIL

ML REMOVED:
PASS/FAIL

AGENT + TOOLS:
PASS/FAIL

CONFIRMATION FLOW:
PASS/FAIL

DASHBOARD SIMPLIFIED:
PASS/FAIL

SIDEBAR SIMPLIFIED:
PASS/FAIL

AA SANDBOX:
PASS/FAIL

PRODUCTION READY:
YES/NO

CRITICAL FINAL RULE:

Do not claim completion based only on unit tests.

Actually verify the agent, tools, routes, API calls, AA flow and final user experience.

Do not invent missing functionality.

Do not silently fall back to fabricated data.

Do not allow the LLM to make authoritative financial calculations.

Do not allow the LLM to mutate the database without explicit user confirmation.

The final product must be simpler, more coherent and more agentic than the current implementation.