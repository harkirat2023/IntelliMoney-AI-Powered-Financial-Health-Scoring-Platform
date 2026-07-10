from datetime import datetime
from typing import Literal, TypedDict, Any

from bson import ObjectId


class UserDocument(TypedDict):
    _id: ObjectId
    email: str
    name: str
    hashed_password: str
    monthly_income: float
    created_at: datetime


class ExpenseDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    amount: float
    description: str
    category: str
    payment_method: str
    date: datetime
    created_at: datetime


class BudgetDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    category: str
    limit: float
    month: int
    year: int


class FinancialScoreDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    score: int
    risk_level: Literal["Excellent", "Good", "Moderate", "Needs Attention"]
    savings_rate: float
    budget_adherence: float
    expense_stability: float
    calculated_at: datetime


class RecommendationDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    items: list[dict[str, str]]
    created_at: datetime


class BudgetAlertDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    budget_id: ObjectId
    threshold: int
    percentage: float
    message: str
    created_at: datetime
    read: bool
    email_queued: bool
    email_sent_at: datetime | None


class RecurringExpenseDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    description: str
    amount: float
    category: str
    frequency: Literal["weekly", "biweekly", "monthly", "yearly"]
    start_date: datetime
    end_date: datetime | None
    is_active: bool
    last_generated_date: datetime | None
    next_expected_date: datetime | None
    created_at: datetime
    updated_at: datetime


class SpendingAnomalyDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    category: str
    date: datetime
    amount: float
    average_amount: float
    deviation_percentage: float
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    is_read: bool
    created_at: datetime


class BudgetSuggestionDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    category: str
    current_limit: float
    suggested_limit: float
    average_spending: float
    max_spending: float
    min_spending: float
    confidence: float
    reason: str
    months_analyzed: int
    is_applied: bool
    created_at: datetime


class FinancialReportDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    report_type: Literal["weekly", "monthly"]
    period_start: datetime
    period_end: datetime
    total_spending: float
    total_income: float
    net_savings: float
    savings_rate: float
    category_breakdown: dict[str, float]
    top_expenses: list[dict[str, Any]]
    budget_performance: dict[str, Any]
    health_score: int | None
    insights: list[str]
    recommendations: list[dict[str, str]]
    generated_at: datetime
    is_read: bool


class BankAccountDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    provider: str
    consent_handle: str
    provider_account_id: str
    bank_name: str
    masked_account_number: str
    account_type: str
    account_holder_name: str
    ifsc_code: str
    connection_status: str
    consent_status: str
    consent_token: str
    consent_version: str
    consent_expiry: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ConsentDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId
    consent_status: Literal["granted", "revoked", "expired"]
    consent_version: str
    granted_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ImportPreferenceDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId
    import_type: Literal["import_all", "start_fresh", "from_date"]
    import_start_date: datetime | None
    created_at: datetime
    updated_at: datetime


class BankTransactionDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId
    sync_log_id: ObjectId | None
    provider_account_id: str
    transaction_id: str
    description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    category: str | None
    reference: str | None
    created_at: datetime


class SyncLogDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId
    sync_type: Literal["initial", "manual", "retry"]
    status: Literal["pending", "running", "completed", "failed"]
    started_at: datetime | None
    completed_at: datetime | None
    transactions_fetched: int
    transactions_imported: int
    transactions_skipped: int
    error_message: str | None
    error_category: Literal["consent_expired", "provider_error", "network_error", "none"]
    retry_count: int
    max_retries: int
    created_at: datetime


class FinancialTransactionDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    bank_account_id: ObjectId
    bank_transaction_id: ObjectId
    sync_log_id: ObjectId | None
    provider_account_id: str
    transaction_id: str
    original_description: str
    amount: float
    transaction_type: Literal["DEBIT", "CREDIT"]
    transaction_date: datetime
    original_category: str | None
    reference: str | None
    cleaned_merchant: str
    normalized_merchant: str
    merchant_id: ObjectId | None
    assigned_category: str
    confidence_score: float
    is_income: bool
    is_recurring: bool
    recurring_id: ObjectId | None
    transaction_tags: list[str]
    is_refund: bool
    is_transfer: bool
    review_status: Literal["auto_approved", "approved", "review_required"]
    reviewed_by: ObjectId | None
    reviewed_at: datetime | None
    review_note: str | None
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MerchantDictionaryDocument(TypedDict):
    _id: ObjectId
    merchant_name: str
    display_name: str
    category: str
    subcategory: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MerchantAliasDocument(TypedDict):
    _id: ObjectId
    merchant_id: ObjectId
    alias_pattern: str
    alias_type: Literal["regex", "exact", "contains"]
    priority: int
    created_at: datetime


class CategoryFeedbackDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    financial_transaction_id: ObjectId
    original_description: str
    original_merchant: str
    suggested_category: str
    user_category: str
    feedback_type: Literal["category", "merchant", "income_flag"]
    created_at: datetime


class TransactionTagDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    name: str
    color: str | None
    created_at: datetime


class SubscriptionDocument(TypedDict):
    _id: ObjectId
    user_id: ObjectId
    description: str
    amount: float
    category: str
    frequency: Literal["weekly", "biweekly", "monthly", "yearly"]
    start_date: datetime
    end_date: datetime | None
    is_active: bool
    last_payment_date: datetime | None
    next_payment_date: datetime | None
    total_spent: float
    payment_count: int
    created_at: datetime
    updated_at: datetime
