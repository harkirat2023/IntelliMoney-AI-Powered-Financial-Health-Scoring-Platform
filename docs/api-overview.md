# API Overview

All private (non-auth) routes require `Authorization: Bearer <token>`.

All endpoints are prefixed with `/api/v1/`.

## Auth

- `POST /api/v1/auth/register`: create user and return JWT.
- `POST /api/v1/auth/login`: authenticate user and return JWT.
- `GET /api/v1/auth/me`: return current user profile.

## Bank Connection

- `POST /api/v1/bank/connect`: initiate bank connection. Request: `{ provider }`. Returns `consent_url` for redirect.
- `POST /api/v1/bank/consent`: finalize consent after AA redirect. Stores encrypted bank accounts.
- `GET /api/v1/bank/accounts`: list connected bank accounts for current user.
- `GET /api/v1/bank/status`: summary — total accounts, active accounts, providers, last sync.
- `DELETE /api/v1/bank/disconnect/{id}`: revoke consent, disconnect account, and revoke any active application consent.

## Consent Grant (User-Facing)

- `POST /api/v1/consent/grant`: grant read-only import consent for a bank account. Request: `{ bank_account_id, consent_version, consent_duration_days }`. Idempotent — returns existing if already granted.
- `POST /api/v1/consent/revoke`: revoke previously granted import consent. Request: `{ bank_account_id }`. Validates consent exists and is in "granted" state.
- `GET /api/v1/consent/status`: get consent status for a bank account. Query: `?bank_account_id=...`. Returns granted/revoked/expired/not_found.

## Import Preference

- `POST /api/v1/import-preference/`: save or update import type preference for an account. Request: `{ bank_account_id, import_type, import_start_date? }`. Atomic upsert. Validates ownership, date constraints.
- `GET /api/v1/import-preference/`: get saved import preference. Query: `?bank_account_id=...`. Returns 404 if not found.

## Data Sync

- `POST /api/v1/sync/start`: start sync for a specific bank account. Request: `{ bank_account_id }`. Validates consent, fetches transactions via provider adapter, deduplicates, persists. Returns sync_log_id.
- `POST /api/v1/sync/manual`: trigger sync for all active bank accounts. No request body. Returns array of per-account results.
- `GET /api/v1/sync/status`: get sync status for one or all accounts. Query: `?bank_account_id=...` (optional). Returns status (pending/running/completed/failed/never), last synced, latest sync summary.
- `GET /api/v1/sync/history`: get paginated sync log history. Query: `?bank_account_id=...&limit=20&offset=0`. Returns items with fetched/imported/skipped counts, error info, retry info.
- `POST /api/v1/sync/retry`: retry a failed sync. Request: `{ sync_log_id }`. Validates can_retry() (must be failed and retry_count < max_retries). Creates new sync log and executes.

## Expenses

- `POST /api/v1/expenses`: create expense. If category is omitted, the NLP classifier predicts it.
- `GET /api/v1/expenses`: list expenses with optional filters.
- `GET /api/v1/expenses/{id}`: fetch one expense.
- `PUT /api/v1/expenses/{id}`: update expense.
- `DELETE /api/v1/expenses/{id}`: delete expense.

## Budgets

- `POST /api/v1/budgets`: create category budget for month/year.
- `GET /api/v1/budgets`: list budgets.
- `GET /api/v1/budgets/status`: show usage, remaining amount, percentage, and warning state.
- `PUT /api/v1/budgets/{id}`: update limit.
- `DELETE /api/v1/budgets/{id}`: delete budget.

## Alerts

- `GET /api/v1/alerts`: calculate current budget usage, generate threshold alerts at 75%, 90%, and 100%, and return alerts.
- `PATCH /api/v1/alerts/{id}/read`: mark one budget alert as read.

## Analytics and Intelligence

- `GET /api/v1/analytics/summary`: monthly spending and savings summary.
- `GET /api/v1/analytics/monthly-spending`: six-month trend data.
- `GET /api/v1/analytics/category-breakdown`: current-month category totals.
- `GET /api/v1/analytics/recent-expenses`: latest transactions.
- `GET /api/v1/financial-health/score`: weighted financial health score.
- `GET /api/v1/recommendations`: personalized recommendation cards.
- `POST /api/v1/ml/categorize`: expense text category prediction.

## AI Transaction Intelligence (V1.5)

- `POST /api/v1/intelligence/process`: process pending bank transactions through the 9-stage AI pipeline. Request: `{ bank_account_id?, limit (1-100) }`. Response: `{ total_available, processed, skipped, failed, message? }`.
- `POST /api/v1/intelligence/process-all`: process up to 100 pending bank transactions across all accounts.
- `POST /api/v1/intelligence/reprocess`: reprocess pending transactions (alias for process). Request: `{ bank_account_id?, limit }`.
- `GET /api/v1/intelligence/status`: pipeline health and queue statistics. Response: `{ is_healthy, pending_transactions, total_processed_all_time, total_in_review_queue }`.
- `GET /api/v1/intelligence/history`: paginated list of processed financial transactions. Query: `?limit=20&offset=0`.
- `GET /api/v1/intelligence/review`: review queue — transactions with `review_status=review_required`. Query: `?limit=20&offset=0`. Response: `{ items: [...], total, limit, offset }`.
- `PATCH /api/v1/intelligence/review/{tx_id}`: submit review decision. Request: `{ review_status, assigned_category?, review_note? }`. Atomic `find_one_and_update` prevents race conditions.
- `POST /api/v1/intelligence/feedback/{tx_id}`: submit feedback on a processed transaction. Request: `{ feedback_type (category|merchant|income_flag), user_category?, user_merchant?, is_income? }`.

## Financial Transactions (V1.5)

- `GET /api/v1/financial-transactions`: list enriched financial transactions. Query: `?limit=50&offset=0&category=Food`. Returns `FinancialTransactionResponse[]` (20 fields including confidence score, review status, merchant info).
- `GET /api/v1/financial-transactions/{id}`: get a single financial transaction by ID.
- `PUT /api/v1/financial-transactions/{id}`: update fields on a financial transaction. Auto-records feedback if `assigned_category` changes.

## Processing (V1.6)

- `POST /api/v1/processing/process`: process pending financial transactions through the 9-stage pipeline. Request: `{ bank_account_id?, limit }`. Response: `{ batch_id, processed, skipped, failed }`.
- `POST /api/v1/processing/process-all`: process all pending financial transactions across accounts.
- `POST /api/v1/processing/reprocess`: reprocess specified transactions. Request: `{ bank_account_id?, limit }`.
- `GET /api/v1/processing/status`: pipeline health and queue statistics.
- `GET /api/v1/processing/history`: paginated list of processing batches.

## Dashboard V2 (V1.8)

- `GET /api/v1/dashboard/summary`: pre-computed dashboard summary for a period. Query: `?period=YYYY-MM`. Response includes total_spending, total_income, net_savings, savings_rate, spending_by_category, monthly_trend, top_merchants, budget_overview.
- `GET /api/v1/dashboard/spending`: spending data for a specific category. Query: `?category=Food&period=YYYY-MM`.
- `GET /api/v1/dashboard/cashflow`: cash flow history. Query: `?months=6` (1-24). Returns monthly income/expense/net_cash_flow.
- `GET /api/v1/dashboard/monthly`: monthly trend data. Query: `?months=6`.
- `GET /api/v1/dashboard/overview`: comprehensive dashboard overview with 22 pre-computed metrics. Query: `?period=YYYY-MM`. Returns spending widget, budget widget, health score, income, savings, activity feed, AI insights.
- `GET /api/v1/dashboard/analytics`: deep analytics data. Query: `?period=YYYY-MM`.
- `GET /api/v1/dashboard/budgets`: budget overview with on_track/warning/over counts. Query: `?period=YYYY-MM`.
- `GET /api/v1/dashboard/insights`: AI insights and budget alerts.
- `GET /api/v1/dashboard/notifications`: user notifications. Query: `?unread_only=false&limit=50&offset=0`.
- `GET /api/v1/dashboard/notifications/unread-count`: unread notification count.
- `POST /api/v1/dashboard/notifications/{id}/read`: mark a notification as read.
- `POST /api/v1/dashboard/notifications/read-all`: mark all notifications as read.
- `GET /api/v1/dashboard/activity`: activity feed (7 activity types).
- `GET /api/v1/dashboard/widgets`: customizable widget data. Query: `?period=YYYY-MM&widget=spending&widget=budget`.

## Financial Health V2 (V1.9)

- `POST /api/v1/health/calculate`: calculate current financial health score (10-factor weighted formula). Returns score, risk_level, factors.
- `POST /api/v1/health/recalculate`: force recalculation of health score.
- `GET /api/v1/health/current`: get current health score and breakdown.
- `GET /api/v1/health/history`: get health score history. Query: `?limit=36`.
- `GET /api/v1/health/trends`: get health trend analysis. Query: `?months=12`.
- `GET /api/v1/health/breakdown`: get detailed factor breakdown.
- `GET /api/v1/health/recommendations`: get personalized health recommendations.
- `GET /api/v1/health/risk`: get risk assessment with category-level scoring.

## Budget Intelligence V2 (V1.10)

- `POST /api/v1/budget-intelligence/generate`: generate budget intelligence data. Returns budget_score, categories, potential_savings.
- `POST /api/v1/budget-intelligence/recalculate`: force recalculation.
- `GET /api/v1/budget-intelligence/current`: get current budget intelligence data.
- `GET /api/v1/budget-intelligence/recommendations`: get ML-based budget recommendations.
- `GET /api/v1/budget-intelligence/optimization`: get budget optimization report.
- `GET /api/v1/budget-intelligence/trends`: get category spending predictions and trends.
- `GET /api/v1/budget-intelligence/risk`: get budget risk assessment (volatility, overspending).
- `GET /api/v1/budget-intelligence/opportunities`: get savings opportunities with actionable steps.

## AI Copilot V2 (V1.11)

- `POST /api/v1/copilot/chat`: send a message to the AI copilot. Request: `{ message, session_id? }`. Response: `{ reply, session_id, tools_used, confidence }`.
- `GET /api/v1/copilot/sessions`: list chat sessions for the current user.
- `GET /api/v1/copilot/sessions/{id}`: get session history with all messages.
- `DELETE /api/v1/copilot/sessions`: delete all sessions and history.
- `POST /api/v1/copilot/feedback`: submit feedback on a copilot response. Request: `{ session_id, message_id, rating, feedback_text? }`.
- `GET /api/v1/copilot/suggestions`: get suggested questions for the copilot.
- `GET /api/v1/copilot/settings`: get copilot configuration (model, temperature, max_tokens).

## Goal Planning V2 (V1.12)

- `POST /api/v1/goals`: create a new financial goal. Request: `{ goal_type, target_amount, target_date, name, description? }`. 10 goal types supported.
- `PUT /api/v1/goals/{id}`: update an existing goal.
- `DELETE /api/v1/goals/{id}`: delete a goal.
- `GET /api/v1/goals`: list goals. Query: `?status=active`.
- `GET /api/v1/goals/{id}`: get a single goal with progress.
- `POST /api/v1/goals/analyze`: analyze feasibility of a proposed goal. Request: `{ goal_type, target_amount, target_date, monthly_contribution? }`. Returns feasibility score, recommendations.
- `POST /api/v1/goals/recalculate`: recalculate progress and predictions for all goals.
- `GET /api/v1/goals/recommendations`: get AI-generated goal recommendations.
- `GET /api/v1/goals/progress`: get progress overview for all goals.

## Receipt OCR V2 (V1.13)

- `POST /api/v1/receipts/upload`: upload a receipt image. Multipart: `file`. Returns receipt with ID and status.
- `POST /api/v1/receipts/{id}/process`: process an uploaded receipt through OCR. Extracts merchant, amount, date, time, currency. Auto-categorizes and creates expense.
- `POST /api/v1/receipts/{id}/confirm`: confirm OCR results and finalize expense creation.
- `GET /api/v1/receipts`: list receipts. Query: `?status=processed`.
- `GET /api/v1/receipts/{id}`: get a single receipt.
- `PATCH /api/v1/receipts/{id}`: update receipt fields before confirmation.
- `DELETE /api/v1/receipts/{id}`: delete a receipt.
- `GET /api/v1/receipts/{id}/image`: serve the original receipt image file.

## WebSocket

- `ws://host/api/v1/ws?token=<jwt>`: WebSocket connection for real-time updates. Supports dashboard.* event types for live push updates.
