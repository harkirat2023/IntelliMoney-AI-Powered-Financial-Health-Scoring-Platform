# Financial Processing Engine — Implementation (V1.6)

> **Status:** Implemented | **Version:** V1.6 Sprint  
> **Input:** `financial_transactions` (V1.5 AI-enriched)  
> **Output:** 6 pre-computed collections consumed by Dashboard V2, Budget Engine, Financial Health Engine, Alert System, LangChain Copilot (future)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Processing Pipeline](#2-processing-pipeline)
3. [Folder Structure](#3-folder-structure)
4. [Domain Models](#4-domain-models)
5. [Repository Layer](#5-repository-layer)
6. [Service Layer](#6-service-layer)
7. [Collections](#7-collections)
8. [API Endpoints](#8-api-endpoints)
9. [Event Flow](#9-event-flow)
10. [Error Handling Strategy](#10-error-handling-strategy)
11. [Performance Optimizations](#11-performance-optimizations)
12. [Database Indexes](#12-database-indexes)
13. [Security Considerations](#13-security-considerations)
14. [Future Extension Points](#14-future-extension-points)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        V1.5 AI ENGINE                           │
│  (Enriches bank_transactions → financial_transactions)           │
└──────────────────────┬──────────────────────────────────────────┘
                       │ financial_transactions
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  V1.6 FINANCIAL PROCESSING ENGINE                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FinancialProcessingService                   │    │
│  │  (Single orchestrator — 9 sequential stages)             │    │
│  │                                                          │    │
│  │  1. Validate Transactions                                │    │
│  │  2. Dedup via atomic_claim (findOneAndUpdate)            │    │
│  │  3. Generate Expenses (upsert into expenses)              │    │
│  │  4. Update Budget Usage (upsert into budget_usage)       │    │
│  │  5. Calculate Cash Flow (period-scoped)                  │    │
│  │  6. Calculate Savings (period-scoped)                    │    │
│  │  7. Compute Financial Metrics (period-scoped)            │    │
│  │  8. Aggregate Dashboard (period-scoped)                  │    │
│  │  9. Generate Budget Alerts (reuses existing alerts)      │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────┴──────────────────────────────────┐    │
│  │              Event Publisher (9 event types)             │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT COLLECTIONS                           │
│                                                                  │
│  expenses (reused) │ budget_usage │ dashboard_metrics            │
│  financial_metrics │ cash_flow_summary │ processing_batches      │
│  budget_alerts (reused)                                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOWNSTREAM CONSUMERS                         │
│                                                                  │
│  Dashboard V2 │ Budget Engine │ Financial Health │ Alert System │
│  LangChain Copilot (future) │ Forecasting (future)              │
│  Goal Planner (future)                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **Single orchestrator** (not separate stage classes) | All 9 pipeline stages are methods on `FinancialProcessingService` — reduces file count, keeps pipeline flow visible in one place, avoids over-abstraction before pattern stabilizes |
| **Sequential pipeline** (not parallel) | Simpler error handling, atomic batch status, easier debugging. Parallel execution via `asyncio.gather` wrapper is a future optimization |
| **Atomic claim for dedup** | `findOneAndUpdate` with `{_id, processed_at: null}` eliminates TOCTOU race window — `processed_at` is set BEFORE expense creation |
| **Period-scoped calculations** | Cash flow, savings, dashboard aggregation use ALL transactions for the period (via `find_by_date_range`), not just the current batch — ensures accurate monthly aggregates |
| **Idempotent writes** | All output collections use compound unique keys with `upsert=True` — replay-safe |
| **Repository pattern throughout** | Every collection access goes through a typed repository interface — no direct `db.collection.find()` in new code (except legacy service reuse) |

---

## 2. Processing Pipeline

The pipeline runs as 9 sequential stages inside `FinancialProcessingService.process()`:

### Stage 1 — Validation

**Logic:**
- Fetch each `tx_id` from `financial_transactions`
- Skip if `tx.processed_at` is set and `force=False`
- Skip if `tx.review_status == "review_required"` and `force=False`
- Collect errors per transaction (not batch-level abort)

### Stage 2 — Dedup (Atomic Claim)

**Logic:**
- Call `atomic_claim(tx_id)` on `MongoFinancialTransactionRepository`
- Uses `findOneAndUpdate({_id, processed_at: null}, {$set: {processed_at: utc_now()}})`
- Returns `None` if already claimed by another process — eliminated TOCTOU window
- Claimed transactions proceed to expense generation

### Stage 3 — Expense Generation

**Service:** `ExpenseGenerationService.generate_expenses()`

**Qualifying rules** (ALL must be true):
1. `transaction_type == "DEBIT"`
2. `is_refund == False`
3. `is_transfer == False`
4. `review_status in ("auto_approved", "approved")` OR `force=True`
5. `confidence_score >= 0.70` OR `reviewed_by IS NOT NULL`

**Mapping:**
- `description` ← `normalized_merchant` or `original_description`
- `category` ← `assigned_category`
- `payment_method` ← `tx.payment_method` (falls back to `"Card"`)
- `date` ← `tx.transaction_date` (cast to date)

**Idempotency:** Atomic claim prevents duplicate expense creation — only claimed (unprocessed) transactions generate expenses.

### Stage 4 — Budget Usage

**Service:** `BudgetProcessingService.update_budget_usage()`

**Logic:**
- Queries `budgets` collection for `{user_id, month, year}`
- Queries `expenses` collection for the same period via `month_bounds()`
- For each budget category:
  - `spent = sum(expense.amount)`
  - `percentage_used = round(spent / limit * 100, 2)`
  - `state = "safe" (<80%) | "warning" (80-100%) | "over" (>=100%)`
- Upserts into `budget_usage` on `{user_id, budget_id, month, year}`

### Stage 5 — Cash Flow Calculation

**Service:** `CashFlowService.calculate_cash_flow()`

**Scoping:** Uses ALL financial transactions for the current month period (not just batch), fetched via `find_by_date_range()`

**Logic:**
- Aggregates `CREDIT` transactions by category → `income_by_category`
- Aggregates `DEBIT` (non-refund, non-transfer) by category → `expense_by_category`
- Computes `total_income`, `total_expenses`, `net_cash_flow`
- Upserts into `cash_flow_summary` on `{user_id, year, month}`

### Stage 6 — Savings Calculation

**Service:** `SavingsService.calculate_savings()`

**Scoping:** Uses ALL period transactions.

**Logic:**
- `total_income = sum(CREDIT amounts)`
- `total_expenses = sum(DEBIT amounts for non-refund, non-transfer)`
- `net_savings = total_income - total_expenses`
- `savings_rate = max(min(net_savings / total_income * 100, 100), -100)`
- Trend: compares to previous month's `cash_flow_summary.savings_rate`

### Stage 7 — Financial Metrics

**Service:** `FinancialMetricsService.compute_metrics()`

**Inputs:** Savings rate, budget states, expense stability (optional override)

**Weighted Score (0–100):**
| Factor | Weight |
|--------|--------|
| Savings Rate | 35% |
| Budget Adherence | 30% |
| Expense Stability | 20% |
| Category Risk | 15% |

**Risk Levels:** `Excellent (>=80) | Good (>=65) | Moderate (>=45) | Needs Attention (<45)`

**Computation:**
- Budget adherence: mean of `max(0, 100 - max(0, percentage_used - 100))` across all budgets
- Expense stability: inverse coefficient of variation over 6 months (via `ExpenseRepository.get_by_user()`)
- Category risk: ratio of discretionary (Shopping/Entertainment/Travel) to total spending
- Month-over-month: delta from previous period's score
- Upserts into `financial_metrics` on `{user_id, period}`

### Stage 8 — Dashboard Aggregation

**Service:** `DashboardAggregationService.aggregate()`

**Scoping:** Uses ALL period transactions for spending breakdown, ALL financial transactions for 6-month trend.

**Output structure:**
```json
{
  "period": "2026-07",
  "total_spending": 1250.00,
  "total_income": 5000.00,
  "net_savings": 3750.00,
  "savings_rate": 75.0,
  "expense_count": 42,
  "spending_by_category": [{"category": "Food", "amount": 350.00, "percentage": 28.0}],
  "monthly_trend": [{"month": "Feb", "spending": 1300.0, "income": 5000.0}],
  "top_merchants": [{"merchant": "Amazon", "amount": 150.00, "count": 3}],
  "budget_overview": [{"category": "Food", "limit": 400, "spent": 350, "state": "safe"}]
}
```

**6-Month Trend:** Queries `financial_transactions` for each of the last 6 months (via `MongoFinancialTransactionRepository.find_by_date_range()`), aggregates spending and income per month.

### Stage 9 — Budget Alerts

**Service:** `BudgetAlertService.generate_alerts()`

**Integration:** Reuses existing `budget_alerts` collection.

**Thresholds:** 75%, 90%, 100% of budget limit.

**Logic:**
- For each budget state, find the highest reached threshold
- If alert exists for `{user_id, budget_id, threshold}`, update `percentage` and `message`
- If not, insert new alert with `read=False`, `email_queued=False`
- Alerts are deduplicated at the `{user_id, budget_id, threshold}` level

### Event Publishing

After all stages complete, publishes 9 processing events via the existing `EventBus` singleton:

| Event | Condition |
|-------|-----------|
| `processing.batch.started` | Pipeline begins |
| `processing.batch.completed` | Pipeline ends |
| `processing.expense.created` | Per created expense |
| `processing.budget.updated` | Per updated budget |
| `processing.cashflow.updated` | Cash flow upserted |
| `processing.financial_metrics.updated` | Metrics upserted |
| `processing.dashboard.updated` | Dashboard upserted |

---

## 3. Folder Structure

```
backend/app/processing/
├── __init__.py                              # Package marker
├── models/
│   ├── __init__.py
│   ├── budget_usage.py                      # BudgetUsage domain model
│   ├── cash_flow_summary.py                 # CashFlowSummary domain model
│   ├── dashboard_metrics.py                 # DashboardMetrics domain model
│   ├── financial_metrics.py                 # FinancialMetrics domain model
│   ├── monthly_summary.py                   # MonthlySummary (schema ready, not yet written)
│   └── processing_batch.py                  # ProcessingBatch + ProcessingError + ProcessingSummary
├── repositories/
│   ├── __init__.py
│   ├── budget_usage_repository.py           # Abstract + MongoBudgetUsageRepository
│   ├── cash_flow_repository.py              # Abstract + MongoCashFlowRepository
│   ├── dashboard_metrics_repository.py      # Abstract + MongoDashboardMetricsRepository
│   ├── financial_metrics_repository.py      # Abstract + MongoFinancialMetricsRepository
│   ├── monthly_summary_repository.py        # Abstract + MongoMonthlySummaryRepository
│   └── processing_batch_repository.py       # Abstract + MongoProcessingBatchRepository
├── schemas/
│   ├── __init__.py
│   ├── dashboard.py                         # DashboardSummary, Spending, CashFlow, MonthlyTrend
│   └── processing.py                        # ProcessRequest, ReprocessRequest, ProcessingStatusResponse
└── services/
    ├── __init__.py
    ├── budget_alert_service.py              # Budget alert generation
    ├── budget_processing_service.py         # Budget usage computation
    ├── cash_flow_service.py                 # Cash flow calculation
    ├── dashboard_aggregation_service.py     # Dashboard metric rollup
    ├── dashboard_read_service.py            # Dashboard read-only API backing
    ├── expense_generation_service.py        # Expense creation from transactions
    ├── factory.py                            # Singleton factory
    ├── financial_metrics_service.py         # Health score computation
    ├── financial_processing_service.py      # Main orchestrator (9-stage pipeline)
    └── savings_service.py                   # Savings rate + trend calculation
```

### Modified Existing Files

| File | Change |
|------|--------|
| `backend/app/api/v1/router.py` | Added `processing.router` + `dashboard_v2.router` |
| `backend/app/db/mongodb.py` | 9 new indexes across 6 collections |
| `backend/app/core/config.py` | Added `ProcessingSettings` (max_batch_size, confidence_threshold, alert_cooldown_hours) |
| `backend/app/domain/financial_transactions/repository.py` | Added `atomic_claim()`, `find_unprocessed()`, `update_fields()` to abstract interface |
| `backend/app/infrastructure/database/repositories/intelligence/financial_transaction_repository.py` | Implemented `atomic_claim()`, `find_unprocessed()` |
| `backend/app/infrastructure/messaging/event_bus.py` | Added handler-level try/except isolation |

---

## 4. Domain Models

### BudgetUsage

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str \| None` | MongoDB ObjectId |
| `user_id` | `str` | Owner |
| `budget_id` | `str` | Reference to `budgets` collection |
| `category` | `str` | Budget category |
| `month` / `year` | `int` | Period |
| `limit` | `float` | Budget cap |
| `spent` | `float` | Current spend |
| `remaining` | `float` | `limit - spent` |
| `percentage_used` | `float` | 0–100% |
| `state` | `str` | `safe` / `warning` / `over` |

### CashFlowSummary

| Field | Type | Notes |
|-------|------|-------|
| `user_id` | `str` | Owner |
| `year` / `month` | `int` | Period |
| `total_income` | `float` | Sum of CREDITs |
| `total_expenses` | `float` | Sum of DEBITs (non-refund, non-transfer) |
| `net_cash_flow` | `float` | Income - Expenses |
| `income_by_category` | `list[dict]` | Sorted by amount desc |
| `expense_by_category` | `list[dict]` | Sorted by amount desc |

### DashboardMetrics

| Field | Type | Notes |
|-------|------|-------|
| `user_id` | `str` | Owner |
| `period` | `str` | `YYYY-MM` format |
| `total_spending` | `float` | Monthly total |
| `total_income` | `float` | Monthly income |
| `net_savings` / `savings_rate` | `float` | Derived |
| `expense_count` | `int` | Transaction count |
| `spending_by_category` | `list[dict]` | `{category, amount, percentage}` |
| `monthly_trend` | `list[dict]` | Last 6 months `{month, spending, income}` |
| `top_merchants` | `list[dict]` | Top 10 by amount `{merchant, amount, count}` |
| `budget_overview` | `list[dict]` | `{category, limit, spent, state}` |

### FinancialMetrics

| Field | Type | Notes |
|-------|------|-------|
| `user_id` | `str` | Owner |
| `period` | `str` | `YYYY-MM` |
| `score` | `int` | 0–100 weighted score |
| `risk_level` | `str` | Excellent / Good / Moderate / Needs Attention |
| `savings_rate` | `float` | Passed from savings stage |
| `budget_adherence` | `float` | Average budget compliance |
| `expense_stability` | `float` | Inverse CV of 6-month spending |
| `discretionary_ratio` | `float` | Discretionary / total |
| `month_over_month_change` | `float` | Score delta |
| `trend` | `str` | improving / stable / declining |

### ProcessingBatch

| Field | Type | Notes |
|-------|------|-------|
| `batch_id` | `str` | UUID (uuid4 hex) |
| `user_id` | `str` | Owner |
| `status` | `Literal["pending", "processing", "completed", "failed"]` | Batch lifecycle |
| `total` / `processed` / `failed` | `int` | Counts |
| `errors` | `list[ProcessingError]` | Typed error records |
| `summary` | `ProcessingSummary \| None` | Per-stage counts |
| `created_at` / `completed_at` | `datetime \| None` | Timestamps |

### ProcessingError

| Field | Type |
|-------|------|
| `transaction_id` | `str` |
| `stage` | `str` |
| `message` | `str` |
| `error_type` | `str` (default: "general") |

---

## 5. Repository Layer

### New Repositories

| Repository | Abstract Methods | Mongo Implementation |
|------------|-----------------|---------------------|
| `BudgetUsageRepository` | `upsert()`, `get_by_user_and_period()`, `get_by_user()` | `MongoBudgetUsageRepository` |
| `CashFlowRepository` | `upsert()`, `get_by_user_and_month()`, `get_range()`, `get_by_user()` | `MongoCashFlowRepository` |
| `DashboardMetricsRepository` | `upsert()`, `get_by_user_and_period()`, `get_by_user()` | `MongoDashboardMetricsRepository` |
| `FinancialMetricsRepository` | `upsert()`, `get_latest_by_user()`, `get_by_user_and_period()`, `get_trend()` | `MongoFinancialMetricsRepository` |
| `MonthlySummaryRepository` | `upsert()`, `get_by_user_and_period()` | `MongoMonthlySummaryRepository` |
| `ProcessingBatchRepository` | `create()`, `get_by_batch_id()`, `get_by_user()`, `update_status()` | `MongoProcessingBatchRepository` |

### Extended Repositories

| Repository | New Methods |
|------------|-------------|
| `FinancialTransactionRepository` (abstract) | `atomic_claim()`, `find_unprocessed()`, `update_fields()` |
| `MongoFinancialTransactionRepository` | `atomic_claim()` — `findOneAndUpdate` with `processed_at: null`, `find_unprocessed()` — queries `processed_at: null` sorted by `created_at ASC` |

### Reused Repositories

| Repository | Usage |
|------------|-------|
| `MongoExpenseRepository` | Creating expenses in Stage 3 |
| `MongoFinancialTransactionRepository` | Reading input transactions, atomic claim |

---

## 6. Service Layer

### Service Dependency Graph

```
FinancialProcessingService (orchestrator)
├── ExpenseGenerationService
│   ├── MongoExpenseRepository
│   └── MongoFinancialTransactionRepository (for atomic_claim)
├── BudgetProcessingService
│   ├── db (budgets collection)
│   └── MongoBudgetUsageRepository
├── CashFlowService
│   └── MongoCashFlowRepository
├── SavingsService
│   └── MongoCashFlowRepository (for previous-period comparison)
├── FinancialMetricsService
│   ├── MongoExpenseRepository (for 6-month stability)
│   └── MongoFinancialMetricsRepository
├── DashboardAggregationService
│   ├── MongoFinancialTransactionRepository (for 6-month trend)
│   └── MongoDashboardMetricsRepository
└── BudgetAlertService
    └── db (budget_alerts collection)
```

### FinancialProcessingService.process() Flow

```
process(user_id, tx_ids, force=False) -> dict
│
├── 1. Create ProcessingBatch (status="processing")
├── 2. Publish processing.batch.started
├── 3. Validate & dedup transactions (fetch by ID, check processed_at, review_status)
├── 4. ExpenseGenerationService.generate_expenses(transactions, force)
├── 5. Query ALL period transactions via find_by_date_range()
├── 6. BudgetProcessingService.update_budget_usage(user_id)
├── 7. CashFlowService.calculate_cash_flow(user_id, period_txs)
├── 8. SavingsService.calculate_savings(user_id, period_txs)
├── 9. FinancialMetricsService.compute_metrics(user_id, savings_rate, budget_states)
├── 10. DashboardAggregationService.aggregate(user_id, period_txs, savings_data, budget_states)
├── 11. BudgetAlertService.generate_alerts(user_id, budget_states)
├── 12. Publish processing.batch.completed
└── 13. Update ProcessingBatch (status="completed" or "failed")
```

### Key Service Behaviors

**ExpenseGenerationService:** Uses `atomic_claim()` to set `processed_at` BEFORE creating the expense — eliminates TOCTOU race. Previously unprocessed txs are skipped automatically.

**BudgetProcessingService:** Uses `month_bounds()` from `date_utils.py` for proper datetime range, not string-based date comparison. Queries expenses via direct collection access (legacy pattern — budget service predates expense repository).

**CashFlowService + SavingsService + DashboardAggregationService:** All period-scoped — the orchestrator passes ALL transactions for the current month (via `find_by_date_range`), not just the current batch. This ensures partial-batch processing still produces correct monthly aggregates.

**FinancialMetricsService:** Uses `MongoExpenseRepository.get_by_user()` with `date_from`/`date_to` instead of `_db.expenses.find()` — follows repository pattern.

**DashboardAggregationService:** Uses `MongoFinancialTransactionRepository.find_by_date_range()` instead of `_db.financial_transactions.find()` — follows repository pattern.

**BudgetAlertService:** Reuses existing `budget_alerts` collection. Threshold dedup at `{user_id, budget_id, threshold}` prevents duplicate alerts. Cooldown via compound unique index.

---

## 7. Collections

### Output Collections

#### `budget_usage`

| Field | Type | Index |
|-------|------|-------|
| `user_id` | ObjectId | Compound unique |
| `budget_id` | ObjectId | Compound unique |
| `month` | int | Compound unique |
| `year` | int | Compound unique |
| `category` | string | — |
| `limit` | number | — |
| `spent` | number | — |
| `remaining` | number | — |
| `percentage_used` | number | — |
| `state` | string (`safe`/`warning`/`over`) | Secondary index |
| `updated_at` | date | — |

**Unique index:** `(user_id, budget_id, month, year)`

#### `financial_metrics`

| Field | Type | Index |
|-------|------|-------|
| `user_id` | ObjectId | Compound |
| `period` | string (`YYYY-MM`) | Compound |
| `score` | int (0–100) | — |
| `risk_level` | string | — |
| `savings_rate` | number | — |
| `budget_adherence` | number | — |
| `expense_stability` | number | — |
| `discretionary_ratio` | number | — |
| `month_over_month_change` | number | — |
| `trend` | string | — |
| `calculated_at` | date | Compound |

**Unique index:** `(user_id, period)`

#### `cash_flow_summary`

| Field | Type | Index |
|-------|------|-------|
| `user_id` | ObjectId | Compound unique |
| `year` | int | Compound unique |
| `month` | int | Compound unique |
| `total_income` | number | — |
| `total_expenses` | number | — |
| `net_cash_flow` | number | — |
| `income_by_category` | array | — |
| `expense_by_category` | array | — |
| `updated_at` | date | — |

**Unique index:** `(user_id, year, month)`

#### `dashboard_metrics`

| Field | Type | Index |
|-------|------|-------|
| `user_id` | ObjectId | Compound unique |
| `period` | string | Compound unique |
| `total_spending` | number | — |
| `total_income` | number | — |
| `net_savings` | number | — |
| `savings_rate` | number | — |
| `expense_count` | int | — |
| `spending_by_category` | array | — |
| `monthly_trend` | array | — |
| `top_merchants` | array | — |
| `budget_overview` | array | — |
| `updated_at` | date | Secondary sort |

**Unique index:** `(user_id, period)`

#### `monthly_summary`

| Field | Type | Index |
|-------|------|-------|
| `user_id` | ObjectId | Compound unique |
| `period` | string | Compound unique |
| `month` | int | — |
| `year` | int | — |
| `total_income` | number | — |
| `total_expenses` | number | — |
| `net_savings` | number | — |
| `savings_rate` | number | — |
| `top_categories` | array | — |
| `updated_at` | date | — |

**Unique index:** `(user_id, period)`

#### `processing_batches`

| Field | Type | Index |
|-------|------|-------|
| `batch_id` | string (UUID) | Unique |
| `user_id` | ObjectId | Secondary |
| `status` | string | — |
| `total/processed/failed` | int | — |
| `errors` | array | — |
| `summary` | object | — |
| `created_at` | date | Compound sort |
| `completed_at` | date | — |

**Indexes:** `(batch_id)` unique, `(user_id, created_at)` compound

---

## 8. API Endpoints

### Processing Endpoints

All under prefix `/api/v1/processing`. All JWT-protected.

#### `POST /api/v1/processing/process`

Process specific transactions by ID.

**Request:**
```json
{
  "transaction_ids": ["tx_id_1", "tx_id_2"],
  "force": false
}
```

**Response (202 Accepted):**
```json
{
  "batch_id": "uuid",
  "status": "processing",
  "total": 2,
  "processed": 0,
  "failed": 0,
  "errors": [],
  "summary": null,
  "created_at": "2026-07-05T12:00:00Z",
  "completed_at": null
}
```

**`force=true`** bypasses `processed_at` check and `review_required` guard.

#### `POST /api/v1/processing/process-all`

Process all unprocessed transactions for the current user.

**Query params:** `force` (bool, default false), `limit` (int, max 500, default 100)

**Behavior:**
- Without `force`: uses `find_unprocessed()` — queries `processed_at: null`, sorts by `created_at ASC`
- With `force`: uses `find_by_user()` — all recent transactions regardless of processed state

**Response:** Same as `/process` (202 Accepted).

#### `POST /api/v1/processing/reprocess`

Re-process already-processed transactions (e.g., after category correction).

**Request:**
```json
{
  "transaction_ids": ["tx_id_1"],
  "reason": "category_correction"
}
```

**Behavior:**
- Clears `processed_at` on the financial transaction
- Deletes existing expense (by `transaction_id` lookup)
- Deletes budget usage entries
- Runs full pipeline with `force=True`

#### `GET /api/v1/processing/status?batch_id=uuid`

Poll processing batch status.

**Response:**
```json
{
  "batch_id": "uuid",
  "status": "completed",
  "total": 2,
  "processed": 2,
  "failed": 0,
  "errors": [],
  "summary": {
    "expenses_created": 2,
    "expenses_skipped": 0,
    "budget_usage_updated": 1,
    "dashboard_metrics_updated": 1,
    "financial_metrics_updated": 1,
    "cash_flow_updated": 1,
    "alerts_generated": 1
  },
  "created_at": "2026-07-05T12:00:00Z",
  "completed_at": "2026-07-05T12:00:05Z"
}
```

`status` is `"completed"` if `failed == 0`, `"failed"` otherwise.

#### `GET /api/v1/processing/history`

List recent processing batches.

**Query params:** `limit` (int, default 20, max 100), `offset` (int, default 0)

**Response:** Array of batch summaries (status, counts, timestamps).

### Dashboard Endpoints (V2)

All under prefix `/api/v1/dashboard`. JWT-protected. Backed by pre-computed collections.

#### `GET /api/v1/dashboard/summary?period=2026-07`

Period-scoped dashboard summary.

**Response:** `DashboardSummaryResponse` — total_spending, total_income, net_savings, savings_rate, expense_count, spending_by_category (top categories with percentage), monthly_trend (6 months), top_merchants (top 10), budget_overview.

#### `GET /api/v1/dashboard/spending?category=Food&period=2026-07`

Category-specific spending detail.

**Response:** `{category, amount, percentage, transaction_count}`

#### `GET /api/v1/dashboard/cashflow?months=6`

Monthly cash flow history.

**Query params:** `months` (int, 1–24, default 6)

**Response:** Array of `{year, month, total_income, total_expenses, net_cash_flow, income_by_category[], expense_by_category[]}`

#### `GET /api/v1/dashboard/monthly?months=6`

Monthly trend data for charts.

**Response:** Array of `{month (label), spending, income, savings}`

---

## 9. Event Flow

### Event Types

All events use the `processing.*` namespace and are published via the existing `EventBus` singleton.

| Event | Published By | Payload |
|-------|-------------|---------|
| `processing.batch.started` | `process()` | `{batch_id, tx_count}` |
| `processing.batch.completed` | `process()` | `{batch_id, tx_count}` |
| `processing.expense.created` | `process()` (per expense) | `{expense_id}` |
| `processing.budget.updated` | `process()` (per budget) | `{budget_id, category, state, percentage}` |
| `processing.cashflow.updated` | `process()` | `{year, month, total_income, total_expenses}` |
| `processing.financial_metrics.updated` | `process()` | `{score, risk_level, savings_rate}` |
| `processing.dashboard.updated` | `process()` | `{period}` |

### Event Bus Isolation

Handler failures are isolated — `EventBus.publish()` wraps each handler in `try/except` with `logger.exception()`. One handler failure does not prevent subsequent handlers from executing.

### Duplicate Event Prevention

Events are fire-and-forget with no at-least-once delivery guarantee. Downstream consumers should be idempotent. A future enhancement could add `event_id` (UUID) for dedup at the consumer level.

---

## 10. Error Handling Strategy

### Transaction-Level Errors

Errors are collected at the transaction level, not the batch level. Each processing stage appends to a shared `errors: list[dict]` list with `{transaction_id, stage, message}` structure. The `ProcessingBatch.errors` field uses the typed `ProcessingError` Pydantic model.

### Batch Status

- `status = "completed"` — all transactions succeeded (`failed_count == 0`)
- `status = "failed"` — one or more transactions failed (`failed_count > 0`)
- Partial failures are expected — some transactions may succeed while others fail

### No Retry in Pipeline

The pipeline does not retry failed stages. Failed transactions remain unprocessed (`processed_at` is set ONLY by successful `atomic_claim` during expense generation). A future retry mechanism can re-process failed transactions via the existing `/process` endpoint.

### Logging

Every service uses `logging.getLogger("intellimoney")` for structured logging. Key log points:
- Batch start/completion (with user_id, batch_id, counts)
- Transaction-level errors (with user_id, tx_id, error message)
- Budget alert generation count
- Empty batch (no budgets found, no transactions)

---

## 11. Performance Optimizations

### Period-Scoped Aggregation

Cash flow, savings, and dashboard aggregation use ALL transactions for the current month (fetched via `find_by_date_range`), not just the batch being processed. This ensures:
- Partial batch processing produces correct monthly aggregates
- No need to re-process existing transactions when new ones arrive
- Dashboard always reflects the full picture

### Atomic Claim to Eliminate N+1

The original pattern of `get_by_id` + check `processed_at` + create expense required 2 queries per transaction. `atomic_claim()` collapses this to a single `findOneAndUpdate` with `{processed_at: null}` filter.

### Batch Size Control

- `limit` parameter on `/process-all` (default 100, max 500)
- `transaction_ids` max length 500 on `/process`
- Processing batches have a TTL index (7-day expiry) for automatic cleanup

### Idempotent Upserts

All output collections use compound unique keys with `$set` + `upsert=True`:
- `budget_usage`: `{user_id, budget_id, month, year}`
- `cash_flow_summary`: `{user_id, year, month}`
- `dashboard_metrics`: `{user_id, period}`
- `financial_metrics`: `{user_id, period}`

This ensures replay safety — running the same batch twice produces identical results.

---

## 12. Database Indexes

### New Indexes (created in `mongodb.py`)

```python
# budget_usage
(user_id, budget_id, month, year)  # unique — upsert key
(user_id, state)                    # filter active warnings/overages

# dashboard_metrics
(user_id, period)                   # unique — upsert key
(user_id, updated_at)               # sort by recency

# financial_metrics
(user_id, calculated_at)            # sort by recency

# cash_flow_summary
(user_id, year, month)              # unique — upsert key

# monthly_summary
(user_id, period)                   # unique — upsert key

# processing_batches
(batch_id)                          # unique — lookup by batch_id
(user_id, created_at)               # sort by recency
```

---

## 13. Security Considerations

### Same Authorization Model

All processing and dashboard endpoints reuse the existing `get_current_user` JWT dependency. All operations are scoped to `current_user["_id"]` — users cannot access or process data belonging to other users.

### Atomic Claims Prevent Double Processing

`atomic_claim()` uses MongoDB `findOneAndUpdate` with `{_id, processed_at: null}` — even if two concurrent requests try to process the same transaction, only one will succeed. The `$set` operator is atomic at the document level.

### No Data Exposure

Error responses contain only transaction IDs and stage names — no financial data, merchant names, or category details leak through error messages.

### Backward Compatible

All existing endpoints (auth, sync, intelligence, analytics, expenses, budgets, alerts) remain unchanged. The processing engine is an additive module — no existing routes or models were modified.

---

## 14. Future Extension Points

### MonthlySummary Stage

The `MonthlySummary` model, `MongoMonthlySummaryRepository`, and collection indexes exist but the pipeline does not yet write to `monthly_summary`. This is the next aggregation stage — compute per-month category breakdowns, savings rate, and income summary into a single document.

### Parallel Pipeline Stages

The current sequential model can be optimized with `asyncio.gather()` for independent stages:
- Cash flow, savings, and budget processing can run in parallel (all depend only on period transactions/expenses)
- Metrics depends on savings + budget, dashboard depends on savings + budget + metrics
- A directed acyclic graph (DAG) runner could maximize throughput

### WebSocket Notifications

Subscribe to `processing.*` events in the WebSocket manager for real-time pipeline status updates in the UI.

### Reprocess Cleanup

The current `reprocess()` deletes existing expenses and budget usage entries. Future iterations should also clean up dashboard_metrics, financial_metrics, and cash_flow_summary for the affected period.

### Batch Budget Alert Service

`BudgetAlertService` queries the `budget_alerts` collection directly. A proper repository interface for budget alerts would follow the repository pattern.

### Event Dedup

Add `event_id` (UUID) to all processing events for at-least-once delivery with dedup at the consumer level.

### Downstream Consumers

- **Dashboard V2** — consume `dashboard_metrics` for pre-computed charts
- **Financial Health Engine V2** — consume `financial_metrics` for enhanced scoring
- **Budget Intelligence** — consume `budget_usage` trends for ML-based suggestions
- **LangChain AI Copilot** — consume all collections via LangChain tools
- **Forecasting Engine** — consume `cash_flow_summary` and `monthly_summary` for time-series prediction
- **Goal Planner** — consume `financial_metrics.savings_rate` for goal feasibility analysis
