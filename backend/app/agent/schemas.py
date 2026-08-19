"""Agent proposal schemas.

The LLM never mutates the database. When the user requests a financial
action, the agent calls the ``propose_actions`` tool, which stores a
validated, structured proposal in MongoDB. The user confirms the proposal
through a dedicated endpoint, and a deterministic executor applies the
actions by calling the same domain services used by the REST API.

A proposal can only be executed once; execution is idempotent and
transaction-aware (each action reports its own result so partial failures
are surfaced instead of being silently swallowed).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CATEGORIES


class ActionKind(str, Enum):
    SET_INCOME = "set_income"
    CREATE_EXPENSE = "create_expense"
    UPDATE_EXPENSE = "update_expense"
    DELETE_EXPENSE = "delete_expense"
    CREATE_BUDGET = "create_budget"
    UPDATE_BUDGET = "update_budget"
    DELETE_BUDGET = "delete_budget"
    CREATE_GOAL = "create_goal"
    UPDATE_GOAL = "update_goal"
    DELETE_GOAL = "delete_goal"
    CREATE_RECURRING = "create_recurring"
    UPDATE_RECURRING = "update_recurring"
    DELETE_RECURRING = "delete_recurring"
    CREATE_SUBSCRIPTION = "create_subscription"
    UPDATE_SUBSCRIPTION = "update_subscription"
    DELETE_SUBSCRIPTION = "delete_subscription"
    MARK_NOTIFICATION_READ = "mark_notification_read"
    RECALCULATE_HEALTH = "recalculate_health"
    SYNC_ACCOUNT = "sync_account"
    IMPORT_AA_DATA = "import_aa_data"


# Action kinds that are destructive (require an especially clear confirmation).
DESTRUCTIVE_KINDS = {
    ActionKind.DELETE_EXPENSE,
    ActionKind.DELETE_BUDGET,
    ActionKind.DELETE_GOAL,
    ActionKind.DELETE_RECURRING,
    ActionKind.DELETE_SUBSCRIPTION,
}

WRITE_KINDS = set(ActionKind)


class ProposedAction(BaseModel):
    """A single validated change the user is asked to approve."""

    kind: ActionKind
    summary: str = Field(..., min_length=1, max_length=300)
    params: dict[str, Any] = Field(default_factory=dict)
    destructive: bool = False

    @field_validator("params")
    @classmethod
    def _coerce_params(cls, v: dict) -> dict:
        return {k: value for k, value in (v or {}).items() if value is not None}


class ProposalStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ActionExecutionResult(BaseModel):
    index: int
    kind: str
    summary: str
    status: str  # "executed" | "failed"
    message: str = ""
    result: dict[str, Any] = Field(default_factory=dict)


class Proposal(BaseModel):
    id: str
    user_id: str
    session_id: str = ""
    status: ProposalStatus = ProposalStatus.PENDING
    actions: list[ProposedAction] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    execution: list[ActionExecutionResult] = Field(default_factory=list)
    message: str = ""


def validate_params(kind: ActionKind, params: dict) -> list[str]:
    """Validate action params. Returns a list of human-readable errors.

    This is the single validation gate for every proposed mutation. The
    LLM can never bypass it: a proposal that fails validation is rejected
    before it is stored.
    """
    errors: list[str] = []
    amount = params.get("amount")
    if "amount" in params:
        if not isinstance(amount, (int, float)):
            errors.append("amount must be a number")
        elif amount <= 0:
            errors.append("amount must be greater than 0")
    category = params.get("category")
    if "category" in params and category:
        if category not in CATEGORIES:
            errors.append(f"category must be one of {', '.join(CATEGORIES)}")
    limit = params.get("limit")
    if "limit" in params:
        if not isinstance(limit, (int, float)):
            errors.append("limit must be a number")
        elif limit <= 0:
            errors.append("limit must be greater than 0")
    target_amount = params.get("target_amount")
    if "target_amount" in params:
        if not isinstance(target_amount, (int, float)):
            errors.append("target_amount must be a number")
        elif target_amount <= 0:
            errors.append("target_amount must be greater than 0")
    month = params.get("month")
    if month is not None and not (1 <= int(month) <= 12):
        errors.append("month must be between 1 and 12")
    year = params.get("year")
    if year is not None and int(year) < 2000:
        errors.append("year is invalid")
    if kind in (ActionKind.UPDATE_EXPENSE, ActionKind.DELETE_EXPENSE,
                ActionKind.UPDATE_BUDGET, ActionKind.DELETE_BUDGET,
                ActionKind.UPDATE_GOAL, ActionKind.DELETE_GOAL,
                ActionKind.UPDATE_RECURRING, ActionKind.DELETE_RECURRING,
                ActionKind.UPDATE_SUBSCRIPTION, ActionKind.DELETE_SUBSCRIPTION):
        record_id = params.get("expense_id") or params.get("budget_id") or \
            params.get("goal_id") or params.get("recurring_id") or \
            params.get("subscription_id") or params.get("notification_id")
        if not record_id:
            errors.append("the target record id is required")
    return errors