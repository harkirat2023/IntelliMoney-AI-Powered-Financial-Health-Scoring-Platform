"""Tests for the AI Copilot agent: proposal flow, executor, and endpoints.

These tests run against an in-memory fake Mongo (same pattern as the rest
of the backend test suite) and do not require a live database or an LLM.
"""

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

from bson import ObjectId

from app.agent.executor import ProposalExecutor
from app.agent.schemas import ActionKind, ProposalStatus, validate_params
from app.agent.tools import build_tools
from app.utils.date_utils import utc_now


def run(coro):
    return asyncio.run(coro)


class FakeCursor:
    def __init__(self, items):
        self.items = list(items)

    def sort(self, key, direction=None):
        return self

    def limit(self, count):
        self.items = self.items[:count]
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self._index]
        self._index += 1
        return item


def matches(item, query):
    for key, expected in query.items():
        actual = item.get(key)
        if isinstance(expected, dict):
            if "$gte" in expected and actual < expected["$gte"]:
                return False
            if "$lte" in expected and actual > expected["$lte"]:
                return False
            if "$lt" in expected and actual >= expected["$lt"]:
                return False
            if "$gt" in expected and actual <= expected["$gt"]:
                return False
        elif actual != expected:
            return False
    return True


class FakeCollection:
    def __init__(self):
        self.items = []

    async def insert_one(self, document):
        stored = dict(document)
        stored["_id"] = stored.get("_id", ObjectId())
        self.items.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    async def find_one(self, query):
        return next((item for item in self.items if matches(item, query)), None)

    def find(self, query):
        return FakeCursor([item for item in self.items if matches(item, query)])

    async def update_one(self, query, update):
        item = await self.find_one(query)
        if item:
            item.update(update.get("$set", {}))
            return SimpleNamespace(matched_count=1, modified_count=1)
        return SimpleNamespace(matched_count=0, modified_count=0)

    async def delete_one(self, query):
        for index, item in enumerate(self.items):
            if matches(item, query):
                self.items.pop(index)
                return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)

    async def count_documents(self, query):
        return sum(1 for item in self.items if matches(item, query))


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()
        self.expenses = FakeCollection()
        self.budgets = FakeCollection()
        self.financial_goals = FakeCollection()
        self.recurring_expenses = FakeCollection()
        self.subscriptions = FakeCollection()
        self.notifications = FakeCollection()
        self.agent_proposals = FakeCollection()
        self.income_history = FakeCollection()
        self.bank_accounts = FakeCollection()
        self.aa_consents = FakeCollection()
        self.aa_data_sessions = FakeCollection()
        self.financial_health = FakeCollection()
        self.budget_intelligence = FakeCollection()
        self.cash_flow_summary = FakeCollection()

    def __getitem__(self, name):
        return getattr(self, name)


def make_user(db, income=60000.0):
    doc = {
        "_id": ObjectId(),
        "clerk_user_id": "user_agent_test",
        "name": "Agent Test",
        "email": "agent@example.com",
        "monthly_income": income,
        "created_at": utc_now(),
    }
    run(db.users.insert_one(doc))
    return str(doc["_id"]), doc


def test_validate_params_rejects_invalid():
    errors = validate_params(ActionKind.CREATE_EXPENSE, {"amount": -1, "category": "Bogus"})
    assert any("amount" in e for e in errors)
    assert any("category" in e for e in errors)
    assert validate_params(ActionKind.DELETE_EXPENSE, {})  # missing record id


def test_propose_and_execute_expense_budget_income():
    db = FakeDb()
    user_id, _ = make_user(db)
    tools, _ = build_tools(db, user_id, session_id="sess-1")
    propose = next(t for t in tools if t.name == "propose_actions")

    out = run(propose.ainvoke({"actions": [
        {"kind": "create_expense", "summary": "Record lunch", "params": {
            "amount": 250, "description": "lunch at cafe", "category": "Food",
        }},
        {"kind": "create_budget", "summary": "Food budget", "params": {
            "category": "Food", "limit": 5000, "month": 8, "year": 2026,
        }},
        {"kind": "set_income", "summary": "Set monthly income", "params": {
            "amount": 75000,
        }},
    ]}))
    assert "Proposal recorded" in out

    stored = db.agent_proposals.items[0]
    assert stored["status"] == ProposalStatus.PENDING.value
    assert len(stored["actions"]) == 3

    # Nothing mutated yet.
    assert db.expenses.items == []
    assert db.budgets.items == []

    proposal_id = str(stored["_id"])
    stored["id"] = proposal_id
    proposal = SimpleNamespace(
        id=proposal_id, user_id=user_id, actions=stored["actions"],
        status=ProposalStatus.PENDING, session_id="sess-1",
    )

    executor = ProposalExecutor(db)
    executed = run(executor.execute(proposal))
    assert executed.status == ProposalStatus.EXECUTED

    assert len(db.expenses.items) == 1
    assert db.expenses.items[0]["category"] == "Food"
    assert len(db.budgets.items) == 1
    assert db.budgets.items[0]["limit"] == 5000
    assert db.users.items[0]["monthly_income"] == 75000
    assert len(db.income_history.items) == 1
    assert db.agent_proposals.items[0]["status"] == ProposalStatus.EXECUTED.value
    assert len(db.agent_proposals.items[0]["execution"]) == 3


def test_propose_requires_confirmation_never_mutates():
    db = FakeDb()
    user_id, _ = make_user(db)
    expense = {"user_id": ObjectId(user_id), "amount": 999, "description": "existing bill",
               "category": "Bills", "date": utc_now(), "created_at": utc_now()}
    inserted = run(db.expenses.insert_one(expense))
    expense_id = str(inserted.inserted_id)

    tools, _ = build_tools(db, user_id, session_id="sess-2")
    propose = next(t for t in tools if t.name == "propose_actions")

    out = run(propose.ainvoke({"actions": [
        {"kind": "delete_expense", "summary": "Delete existing bill",
         "params": {"expense_id": expense_id}},
    ]}))
    assert "Proposal recorded" in out

    # The expense is still there: proposing never mutates.
    assert len(db.expenses.items) == 1
    assert db.agent_proposals.items[0]["status"] == ProposalStatus.PENDING.value

    # Only confirmation actually deletes it.
    from app.agent.executor import ProposalExecutor
    stored = db.agent_proposals.items[0]
    proposal = SimpleNamespace(
        id=str(stored["_id"]), user_id=user_id, actions=stored["actions"],
        status=ProposalStatus.PENDING, session_id="sess-2",
    )
    executed = run(ProposalExecutor(db).execute(proposal))
    assert executed.status == ProposalStatus.EXECUTED
    assert db.expenses.items == []


def test_propose_rejects_unknown_ownership():
    db = FakeDb()
    user_id, _ = make_user(db)
    tools, _ = build_tools(db, user_id, session_id="sess-3")
    propose = next(t for t in tools if t.name == "propose_actions")
    try:
        run(propose.ainvoke({"actions": [
            {"kind": "update_expense", "summary": "Edit missing expense",
             "params": {"expense_id": str(ObjectId()), "amount": 500}},
        ]}))
    except Exception as exc:
        assert "Could not find the record" in str(exc)
    else:
        raise AssertionError("Expected ownership check to fail")


def test_confirm_and_cancel_endpoints():
    from app.api.routes.copilot_v2 import cancel_proposal, confirm_proposal, get_proposal

    db = FakeDb()
    user_id, user_doc = make_user(db)
    tools, _ = build_tools(db, user_id, session_id="sess-4")
    propose = next(t for t in tools if t.name == "propose_actions")
    run(propose.ainvoke({"actions": [
        {"kind": "create_expense", "summary": "Record coffee", "params": {
            "amount": 120, "description": "coffee", "category": "Food",
        }},
    ]}))
    proposal_id = str(db.agent_proposals.items[0]["_id"])

    resp = run(get_proposal(proposal_id, user_doc, db))
    assert resp.status == ProposalStatus.PENDING.value

    confirmed = run(confirm_proposal(proposal_id, None, user_doc, db))
    assert confirmed.status == ProposalStatus.EXECUTED.value
    assert len(db.expenses.items) == 1
    assert db.expenses.items[0]["description"] == "coffee"

    # Second confirm must fail (not pending anymore).
    try:
        run(confirm_proposal(proposal_id, None, user_doc, db))
    except Exception as exc:
        assert "not pending" in str(exc)
    else:
        raise AssertionError("Double-confirm should be rejected")

    # Cancel flow.
    run(propose.ainvoke({"actions": [
        {"kind": "create_budget", "summary": "Travel budget", "params": {
            "category": "Travel", "limit": 2000, "month": 8, "year": 2026,
        }},
    ]}))
    cancel_id = str(db.agent_proposals.items[1]["_id"])
    cancelled = run(cancel_proposal(cancel_id, user_doc, db))
    assert cancelled.status == ProposalStatus.CANCELLED.value
    assert db.budgets.items == []


def test_executor_reports_partial_failure():
    db = FakeDb()
    user_id, _ = make_user(db)
    stored_id = str(ObjectId())
    proposal = SimpleNamespace(
        id=str(ObjectId()), user_id=user_id, session_id="s",
        status=ProposalStatus.PENDING,
        actions=[
            {"kind": "create_expense", "summary": "Ok action", "params": {
                "amount": 100, "description": "ok", "category": "Food",
            }},
            {"kind": "delete_expense", "summary": "Missing target",
             "params": {"expense_id": stored_id}},
        ],
    )
    executor = ProposalExecutor(db)
    executed = run(executor.execute(proposal))
    assert executed.status == ProposalStatus.PARTIALLY_FAILED
    assert len(executed.execution) == 2
    statuses = {r.status for r in executed.execution}
    assert statuses == {"executed", "failed"}
    assert len(db.expenses.items) == 1


def test_budget_tools_report_period_status():
    db = FakeDb()
    user_id, _ = make_user(db)
    run(db.budgets.insert_one({
        "_id": ObjectId(), "user_id": ObjectId(user_id),
        "category": "Food", "limit": 1000, "month": 8, "year": 2026,
    }))
    run(db.expenses.insert_one({
        "_id": ObjectId(), "user_id": ObjectId(user_id),
        "amount": 900, "category": "Food", "description": "groceries",
        "date": datetime(2026, 8, 5, tzinfo=timezone.utc),
    }))
    tools, _ = build_tools(db, user_id, session_id="sess-1")
    usage = next(t for t in tools if t.name == "get_budget_usage")
    compare = next(t for t in tools if t.name == "compare_budget_actual")
    remaining = next(t for t in tools if t.name == "get_remaining_budget")

    out = run(usage.ainvoke({"period": "2026-08"}))
    assert '"state": "warning"' in out and '"spent": 900' in out

    out = run(compare.ainvoke({"period": "2026-08"}))
    assert '"warning": 1' in out and '"over": 0' in out

    out = run(remaining.ainvoke({"period": "2026-08"}))
    assert '"remaining": 100' in out