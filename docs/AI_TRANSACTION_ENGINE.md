# AI Transaction Intelligence Engine (V1.5)

## Overview

The AI Transaction Intelligence Engine transforms raw `bank_transactions` (from the Financial Data Synchronization Engine) into enriched `financial_transactions` via a 9-stage processing pipeline. It is the central intelligence layer — all future financial modules (Budget Engine, Dashboard, Financial Health Engine, LangChain Copilot) will consume `financial_transactions` instead of raw bank data.

## Architecture

```
bank_transactions (raw provider data)
        │
        ▼
┌───────────────────────────────────────────────────┐
│              ProcessingPipeline                    │
│                                                    │
│  1. Validation          — Validate bank tx input   │
│  2. Merchant Normalize  — Clean + match merchant   │
│  3. Income/Expense Type — DEBIT/CREDIT analysis    │
│  4. Category Predict    — Merchant → ML → Keyword  │
│  5. Recurring Detect    — Subscriptions + utils    │
│  6. Confidence Score    — 5-factor weighted calc   │
│  7. Review Status       — auto_approved / approved │
│                          / review_required          │
│  8. Build Model         — Construct FinancialTx    │
│  9. Bulk Persist        — Dedup via unique index   │
└───────────────────────────┬───────────────────────┘
                            │
                            ▼
                financial_transactions (enriched)
                            │
                            ├── GET /financial-transactions
                            ├── GET /financial-transactions/{id}
                            ├── PUT /financial-transactions/{id}
                            ├── POST /intelligence/process
                            ├── GET /intelligence/review
                            ├── PATCH /intelligence/review/{id}
                            └── POST /intelligence/feedback/{id}
```

## AI Pipeline (9 Stages)

### 1. Validation (`app/ai/validation_service.py`)
- Validates bank transaction existence, description, amount
- Validates assigned category is in `CATEGORIES` list
- Validates tags start with `#`
- Validates confidence score range [0.0, 1.0]
- Raises `ValidationException` on failure

### 2. Merchant Normalization (`app/infrastructure/bank_integration/merchant/`)
- **Cleaning**: Strips whitespace, removes payment suffixes (`/UPI`, `/DC`, `/CC`), extracts UPI merchant names, extracts card-location patterns, removes special characters, lowercases
- **3-tier alias matching** (sorted by priority):
  - `exact` → confidence 1.0 (e.g., "netflix" matches "Netflix")
  - `contains` → confidence 0.85 (e.g., "SWIGGY BLR IN" matches "Swiggy")
  - `regex` → confidence 0.85 (e.g., pattern matching)
- **In-memory cache**: 300s TTL with `.total_seconds()` refresh check
- **31 merchants** seeded with alias patterns (Swiggy, Zomato, Uber, Ola, Amazon, Flipkart, Netflix, Spotify, Jio, Airtel, Dominos, McDonald's, BigBasket, Zepto, Blinkit, Myntra, Nykaa, BookMyShow, 1mg, PharmEasy, MakeMyTrip, Goibibo, IRCTC, Google One, Google Play, Apple, Amazon Prime, Disney+ Hotstar, ZEE5, Tata Power, BSES)

### 3. Income/Expense Detection (`app/ai/income_service.py`)
- **DEBIT** transactions: never classified as income
- **CREDIT** transactions classified as:
  - Reversal (skipped — not income): keywords like "reversal", "chargeback", "failed", "returned"
  - Refund (is_refund=true): keywords like "refund", "cashback", "reversal", "return"
  - Transfer (is_transfer=true): keywords like "neft", "imps", "rtgs", "self transfer"
  - Income (is_income=true): default for unmatched CREDIT; salary tagged with `#salary`

### 4. Category Prediction (`app/ai/category_service.py`)
- **Merchant override** (confidence ≥ 0.85): merchant dictionary category takes priority
- **ML prediction**: reuses existing `ExpenseCategorizer` from `app/services/ml_service.py` (TF-IDF + Logistic Regression)
- **Keyword fallback**: shared `CATEGORY_KEYWORD_MAP` in `app/core/constants.py` covers 9 categories (Food, Transport, Shopping, Bills, Entertainment, Health, Education, Travel, Rent)

### 5. Recurring Detection (`app/ai/recurring_service.py`)
- **8 known subscriptions** with exact amounts ±5% tolerance: Netflix (₹649/199/499/799), Spotify (₹119/59), Google One (₹130/65), Amazon Prime (₹1499/299/599), Disney+ Hotstar (₹1499/899/299), Apple (₹99/249), ZEE5 (₹999/299), Sony LIV (₹999/499)
- **6 utility keywords**: electricity, water bill, internet, broadband, mobile recharge, dth, gas, insurance
- **2 rent keywords**: rent, landlord
- Tags: `#subscription`, `#utility`, `#rent`

### 6. Confidence Scoring (`app/ai/confidence_service.py`)
Weighted formula (fixed weights):

| Factor | Weight | Description |
|--------|--------|-------------|
| merchant | 0.40 | Normalized merchant confidence (0–1) |
| ml_probability | 0.35 | ML model confidence (0–1) |
| recurring | 0.10 | 0.85 if recurring, 0 otherwise |
| keyword | 0.10 | Keyword match ratio (0–1) |
| amount_normalcy | 0.05 | Flat 0.5 (reserved for future) |

Score = `min(sum(weight × factor), 1.0)`, rounded to 3 decimal places.

### 7. Review Status Decision

| Threshold | Status |
|-----------|--------|
| ≥ 0.95 | `auto_approved` |
| ≥ 0.70 | `approved` |
| < 0.70 | `review_required` |

### 8. Financial Transaction Model

24 fields on the `FinancialTransaction` domain model (`app/domain/financial_transactions/models.py`):

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str \| None` | MongoDB _id |
| `user_id` | `str` | Owner |
| `bank_account_id` | `str` | Source account |
| `bank_transaction_id` | `str` | Source bank tx (unique index) |
| `sync_log_id` | `str \| None` | Sync log reference |
| `provider_account_id` | `str` | Provider account ID |
| `transaction_id` | `str` | Provider transaction ID |
| `original_description` | `str` | Raw description |
| `amount` | `float` | Transaction amount |
| `transaction_type` | `DEBIT \| CREDIT` | DEBIT or CREDIT |
| `transaction_date` | `datetime` | Transaction date |
| `original_category` | `str \| None` | Provider category |
| `reference` | `str \| None` | Transaction reference |
| `cleaned_merchant` | `str` | Cleaned description |
| `normalized_merchant` | `str` | Matched merchant name |
| `merchant_id` | `str \| None` | Merchant dict ID |
| `assigned_category` | `str` | Predicted category |
| `confidence_score` | `float` | Overall confidence (0–1) |
| `is_income` | `bool` | Income flag |
| `is_recurring` | `bool` | Recurring flag |
| `recurring_id` | `str \| None` | Recurring record ref |
| `transaction_tags` | `list[str]` | Tags (`#subscription`, etc.) |
| `is_refund` | `bool` | Refund flag |
| `is_transfer` | `bool` | Transfer flag |
| `review_status` | `auto_approved \| approved \| review_required` | Review state |
| `reviewed_by` | `str \| None` | Reviewer user ID |
| `reviewed_at` | `datetime \| None` | Review timestamp |
| `review_note` | `str \| None` | Review note |
| `processed_at` | `datetime \| None` | Pipeline timestamp |
| `created_at` | `datetime \| None` | Document created |
| `updated_at` | `datetime \| None` | Document updated |

### 9. Bulk Persist
- `insert_many(ordered=False)` with `BulkWriteError` handling — dedup via unique index on `bank_transaction_id`
- Individual error isolation: each transaction wrapped in try/except — failures never crash the full batch
- Concurrent processing: `asyncio.gather` with semaphore(10) for parallel pipeline execution

## ML Pipeline

The existing ML pipeline (pre-dates V1.5) is reused — NOT duplicated:

```
ml/train_model.py
    │
    ├── Reads expense.csv (training data)
    ├── Trains TfidfVectorizer + LogisticRegression pipeline
    └── Writes expense_classifier.joblib
```

- **Model file**: `backend/app/ml/expense_classifier.joblib`
- **CategoryPredictionService** calls `ExpenseCategorizer.predict()` from `app/services/ml_service.py`
- **Fallback**: keyword-based categorization via `CATEGORY_KEYWORD_MAP` when model is unavailable
- **Feedback learning**: `category_feedback` collection stores user corrections for future retraining

## Manual Review Queue

`GET /intelligence/review` returns transactions with `review_status=review_required`:

```json
{
  "items": [
    {
      "id": "...",
      "original_description": "SWIGGY BLR IN",
      "cleaned_merchant": "swiggy blr in",
      "amount": 450.00,
      "transaction_date": "2026-07-01T...",
      "assigned_category": "Food",
      "confidence_score": 0.627,
      "is_income": false,
      "is_recurring": false
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

Users can:
- **Submit review**: `PATCH /intelligence/review/{tx_id}` — approve/reject category, change category, add note
- **Provide feedback**: `POST /intelligence/feedback/{tx_id}` — flag incorrect category, merchant, or income type
- **Update directly**: `PUT /financial-transactions/{id}` — edit fields (auto-records feedback on category change)

Review submissions are atomic: `find_one_and_update` with `{review_status: "review_required"}` filter prevents TOCTOU race conditions.

## Collections

### `financial_transactions`
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | Indexed |
| `bank_account_id` | ObjectId | Indexed |
| `bank_transaction_id` | ObjectId | **Unique index** — dedup |
| `sync_log_id` | ObjectId \| null | |
| `provider_account_id` | string | |
| `transaction_id` | string | |
| `original_description` | string | |
| `amount` | double | |
| `transaction_type` | string | "DEBIT" \| "CREDIT" |
| `transaction_date` | date | Indexed |
| `original_category` | string \| null | |
| `reference` | string \| null | |
| `cleaned_merchant` | string | |
| `normalized_merchant` | string | |
| `merchant_id` | ObjectId \| null | |
| `assigned_category` | string | Indexed |
| `confidence_score` | double | |
| `is_income` | bool | |
| `is_recurring` | bool | |
| `recurring_id` | ObjectId \| null | |
| `transaction_tags` | string[] | |
| `is_refund` | bool | |
| `is_transfer` | bool | |
| `review_status` | string | Indexed: "auto_approved" \| "approved" \| "review_required" |
| `reviewed_by` | ObjectId \| null | |
| `reviewed_at` | date \| null | |
| `review_note` | string \| null | |
| `processed_at` | date | |
| `created_at` | date | |
| `updated_at` | date | |

**Indexes** (7):
1. `{bank_transaction_id: 1}` — unique
2. `{user_id: 1, transaction_date: -1}` — user query
3. `{user_id: 1, assigned_category: 1}` — category filter
4. `{user_id: 1, review_status: 1}` — review queue
5. `{user_id: 1, transaction_date: 1, created_at: 1}` — pagination
6. `{user_id: 1, bank_account_id: 1}` — account filter
7. `{review_status: 1, confidence_score: 1}` — ML training data export

### `merchant_dictionary`
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `merchant_name` | string | **Unique** |
| `display_name` | string | |
| `category` | string | |
| `is_active` | bool | |
| `created_at` | date | |

### `merchant_aliases`
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `merchant_name` | string | |
| `alias_type` | string | "exact" \| "contains" \| "regex" |
| `pattern` | string | |
| `priority` | int | Sort order |
| `is_active` | bool | |
| `created_at` | date | |

### `category_feedback`
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | Indexed |
| `financial_transaction_id` | ObjectId | |
| `original_description` | string | |
| `original_merchant` | string | |
| `suggested_category` | string | |
| `user_category` | string | User correction |
| `feedback_type` | string | "category" \| "merchant" |
| `created_at` | date | Indexed |

### `transaction_tags`
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | |
| `name` | string | **Unique per user** |
| `color` | string \| null | |
| `created_at` | date | |

## API Endpoints

### Intelligence Pipeline

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/intelligence/process` | Process pending bank transactions (limit: 1–100) |
| `POST` | `/intelligence/process-all` | Process up to 100 pending |
| `POST` | `/intelligence/reprocess` | Reprocess (alias for process) |
| `GET` | `/intelligence/status` | Pipeline health + queue stats |
| `GET` | `/intelligence/history` | Paginated processed transactions |
| `GET` | `/intelligence/review` | Review queue (review_required) |
| `PATCH` | `/intelligence/review/{tx_id}` | Submit review (atomic) |
| `POST` | `/intelligence/feedback/{tx_id}` | Submit feedback |

### Financial Transactions

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/financial-transactions` | List (paginated, filterable by category) |
| `GET` | `/financial-transactions/{id}` | Get by ID |
| `PUT` | `/financial-transactions/{id}` | Update fields (auto-records feedback on category change) |

### Request/Response Schemas

**`POST /intelligence/process`**
```json
// Request
{ "bank_account_id": "str (optional)", "limit": 100 }

// Response
{ "total_available": 50, "processed": 45, "skipped": 3, "failed": 2, "message": "str (optional)" }
```

**`POST /intelligence/feedback/{tx_id}`**
```json
// Request
{
  "feedback_type": "category | merchant | income_flag",
  "user_category": "str (optional)",
  "user_merchant": "str (optional)",
  "is_income": "bool (optional)"
}

// Response
{ "id": "str", "message": "Feedback recorded. Thank you!" }
```

**`PATCH /intelligence/review/{tx_id}`**
```json
// Request
{
  "review_status": "approved | review_required | auto_approved",
  "assigned_category": "str (optional)",
  "review_note": "str (optional)"
}

// Response: FinancialTransaction (full object)
```

## Event Flow

Events are published through the existing `EventBus` infrastructure:

| Event | Publisher | Payload | Consumers (future) |
|-------|-----------|---------|-------------------|
| `ai.pipeline.completed` | `FinancialTransactionService.process_pending` | `{processed_count, failed_count, bank_account_id}` | Dashboard, Budget Engine, Health Engine |
| `ai.feedback.recorded` | `FeedbackLearningService` | `{tx_id, feedback_type, original_category, user_category}` | ML retraining pipeline |
| `ai.review.submitted` | `FinancialTransactionService.submit_review` | `{tx_id, review_status, assigned_category}` | Dashboard, Audit log |

Events include: `event_id` (UUID hex), `user_id`, `event_type`, `timestamp` (UTC), and `payload`.

## Key Design Decisions

1. **Reuse existing ML**: `CategoryPredictionService.predict()` calls the existing `ExpenseCategorizer` — no duplicate ML logic
2. **Merchant override priority**: Merchant dictionary category > ML predicted category > fallback keyword matching
3. **Confidence weights**: Fixed weights (merchant 0.40, ML 0.35, recurring 0.10, keyword 0.10, amount_normalcy 0.05)
4. **Batch error isolation**: `process_batch()` wraps each transaction in try/except — individual failures never crash the full batch
5. **Dedup via unique index**: `bank_transaction_id` unique index + `insert_many(ordered=False)` with `BulkWriteError`
6. **Static merchant seed**: 31 merchants with aliases seeded in `merchant_data.py`
7. **Debit transfers not flagged**: IncomeService only flags transfer on CREDIT type
8. **Recurring detection rule-based**: Known subscription amounts ±5% + utility/rent keywords
9. **Feedback auto-records**: `PUT /financial-transactions/{id}` and `PATCH /intelligence/review/{id}` automatically create feedback on category change
10. **Atomic review**: `find_one_and_update` with status filter prevents race conditions

## File Structure

```
backend/app/
├── ai/                                    # NEW — AI Pipeline
│   ├── __init__.py
│   ├── category_service.py                # CategoryPredictionService
│   ├── confidence_service.py              # ConfidenceService (weighted scoring)
│   ├── feedback_service.py                # FeedbackLearningService
│   ├── financial_transaction_service.py   # FinancialTransactionService (orchestrator)
│   ├── income_service.py                  # IncomeDetectionService
│   ├── merchant_service.py                # MerchantNormalizationService (wrapper)
│   ├── models.py                          # PipelineTransaction DTO
│   ├── pipeline.py                        # ProcessingPipeline (9-stage)
│   ├── recurring_service.py               # RecurringDetectionService
│   └── validation_service.py              # ValidationService
│
├── api/routes/
│   ├── intelligence.py                    # NEW — 8 intelligence endpoints
│   └── financial_transactions.py          # NEW — 3 financial transactions endpoints
│
├── core/
│   ├── constants.py                       # EXTENDED — CONFIDENCE_THRESHOLDS, CATEGORY_KEYWORD_MAP, TRANSACTION_TAGS, MERCHANT_CONFIDENCE_WEIGHTS
│   └── exceptions.py                      # EXTENDED — FinancialTransactionNotFoundException, DuplicateProcessException, InvalidReviewStateException
│
├── domain/financial_transactions/         # NEW — Domain layer
│   ├── __init__.py
│   ├── models.py                          # FinancialTransaction (24 fields) + ReviewStatus
│   └── repository.py                      # Abstract repository (11 methods)
│
├── infrastructure/
│   ├── bank_integration/merchant/          # NEW — Merchant Normalization
│   │   ├── __init__.py
│   │   ├── merchant_data.py               # 31 merchants with aliases
│   │   └── merchant_normalizer.py         # MerchantNormalizer (clean + alias match + cache)
│   └── database/repositories/intelligence/ # NEW — Mongo repositories
│       ├── feedback_repository.py
│       ├── financial_transaction_repository.py
│       └── merchant_repository.py
│
├── models/documents.py                    # EXTENDED — 5 new TypedDicts
├── schemas/
│   ├── ai.py                              # NEW — Pipeline/review/feedback schemas
│   └── financial_transactions.py          # NEW — FinancialTransactionResponse/UpdateRequest
└── services/
    └── intelligence_service.py            # NEW — Service factory (singleton-per-db)
```

## Future Consumers

The `financial_transactions` collection is designed as the single source of truth for downstream modules:

| Consumer | Depends On | Description |
|----------|-----------|-------------|
| **Budget Engine** | `assigned_category`, `amount`, `transaction_date` | Track category spending against budget limits |
| **Dashboard** | All fields | Real-time spending breakdown, trends, insights |
| **Financial Health Engine** | `is_income`, `confidence_score`, `transaction_tags` | Enhanced scoring with AI-verified transactions |
| **LangChain Copilot** | All fields | Natural language queries over enriched data |
| **ML Retraining** | `category_feedback` | Incrementally retrain TF-IDF + Logistic Regression |
