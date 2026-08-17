"""Account Aggregator (AA) sandbox/demo flow tests.

These tests verify the approved Setu AA Sandbox demonstration flow:

    Create Consent -> Pending -> Approve/Reject -> Notification
    -> Data Session -> Fetch Sandbox Data -> Normalize -> Import

The AA router is a demo/sandbox integration; imported transactions must
converge into the existing bank-transaction pipeline.
"""

import asyncio
from types import SimpleNamespace

from bson import ObjectId
from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.utils.date_utils import utc_now


def run(coro):
    return asyncio.run(coro)


class FakeCursor:
    def __init__(self, items):
        self.items = list(items)

    def sort(self, key, direction=None):
        if isinstance(key, list):
            for field, order in reversed(key):
                self.items.sort(key=lambda item: item.get(field), reverse=order < 0)
        else:
            self.items.sort(key=lambda item: item.get(key), reverse=direction < 0)
        return self

    def limit(self, count):
        self.items = self.items[:count]
        return self

    def skip(self, count):
        self.items = self.items[count:]
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


class FakeCollection:
    def __init__(self, items=None):
        self.items = items or []

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
            return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)

    async def update_many(self, query, update):
        matched = [item for item in self.items if matches(item, query)]
        for item in matched:
            item.update(update.get("$set", {}))
        return SimpleNamespace(modified_count=len(matched))

    async def delete_many(self, query):
        before = len(self.items)
        self.items = [item for item in self.items if not matches(item, query)]
        return SimpleNamespace(deleted_count=before - len(self.items))

    async def count_documents(self, query):
        return len([item for item in self.items if matches(item, query)])

    def __getitem__(self, key):
        return self


def matches(item, query):
    for key, expected in query.items():
        actual = item.get(key)
        if isinstance(expected, dict):
            if "$gte" in expected and actual < expected["$gte"]:
                return False
            if "$lte" in expected and actual > expected["$lte"]:
                return False
        elif actual != expected:
            return False
    return True


class FakeDb:
    def __init__(self):
        self.aa_consents = FakeCollection()
        self.aa_data_sessions = FakeCollection()
        self.bank_transactions = FakeCollection()
        self.bank_accounts = FakeCollection()
        self.users = FakeCollection()

    def __getitem__(self, key):
        return getattr(self, key, FakeCollection())


fake_db = FakeDb()

_AA_USER = {
    "_id": ObjectId(),
    "clerk_user_id": "user_aa_test",
    "name": "AA Test User",
    "email": "aa@test.com",
    "monthly_income": 70000,
    "is_verified": True,
    "is_onboarded": False,
}


def override_get_current_user():
    return dict(_AA_USER)


def _user_id():
    return "user_aa_test"


async def _stub_process_synced(db, user_id, bank_account_id):
    return {
        "categorized": 3,
        "processed": 3,
        "health_recalculated": True,
        "errors": [],
    }


app.dependency_overrides[get_current_user] = override_get_current_user
from app.db.mongodb import get_database  # noqa: E402

app.dependency_overrides[get_database] = lambda: fake_db


def setup_module():
    fake_db.aa_consents.items = []
    fake_db.aa_data_sessions.items = []
    fake_db.bank_transactions.items = []


def test_aa_full_sandbox_flow():
    from app.services import auto_processing_service

    original = auto_processing_service.AutoProcessingService.process_synced
    auto_processing_service.AutoProcessingService.process_synced = _stub_process_synced

    with TestClient(app) as client:
        # 1. Create consent
        res = client.post("/api/v1/aa/consents", json={"provider": "mock"})
        assert res.status_code == 200, res.text
        body = res.json()
        consent_id = body["id"]
        assert body["consent_status"] == "PENDING"
        assert body["sandbox"] is True
        assert "sandbox" in body["label"].lower()

        # 2. Consent status still pending
        status = client.get(f"/api/v1/aa/consents/{consent_id}")
        assert status.status_code == 200
        assert status.json()["consent_status"] == "PENDING"

        # 3. Reject path
        rejected = client.post(f"/api/v1/aa/consents/{consent_id}/reject")
        assert rejected.json()["consent_status"] == "REJECTED"

        # 4. Data session must fail while rejected
        session = client.post("/api/v1/aa/data-sessions", json={"consent_id": consent_id})
        assert session.status_code == 400

        # 5. Approve path (new consent)
        res2 = client.post("/api/v1/aa/consents", json={"provider": "mock"})
        consent2 = res2.json()["id"]
        approved = client.post(f"/api/v1/aa/consents/{consent2}/approve")
        assert approved.json()["consent_status"] in ("APPROVED", "ACTIVE")

        # 6. Create data session
        session = client.post("/api/v1/aa/data-sessions", json={"consent_id": consent2})
        assert session.status_code == 200, session.text
        session_body = session.json()
        assert session_body["data_status"] == "READY"
        session_id = session_body["id"]

        # 7. Fetch sandbox data -> normalize -> import
        fetched = client.post(f"/api/v1/aa/data-sessions/{session_id}/fetch")
        assert fetched.status_code == 200, fetched.text
        fetch_body = fetched.json()
        assert fetch_body["sandbox"] is True
        assert fetch_body["transactions_fetched"] > 0
        assert fetch_body["transactions_imported"] > 0

        # 8. Imported transactions land in the shared bank_transactions pipeline
        assert len(fake_db.bank_transactions.items) > 0
        imported_user = fake_db.bank_transactions.items[0]["user_id"]
        assert imported_user == str(_AA_USER["_id"])

        # 9. Sandbox status endpoint
        st = client.get("/api/v1/aa/status")
        assert st.status_code == 200
        assert st.json()["mode"] == "sandbox"
        assert "not production" in st.json()["message"].lower()

        # 10. Notification endpoint
        notification = client.post("/api/v1/aa/notifications", json={
            "id": "setu-consent-1",
            "type": "CONSENT_APPROVED",
            "data": {},
        })
        assert notification.status_code == 200
        assert notification.json()["received"] is True

    auto_processing_service.AutoProcessingService.process_synced = original


def test_aa_ownership_enforced():
    with TestClient(app) as client:
        other = client.get("/api/v1/aa/consents")
        assert other.status_code == 200
        for item in other.json():
            assert item["id"]

        # Unknown consent id -> 404
        missing = client.get("/api/v1/aa/consents/000000000000000000000000")
        assert missing.status_code == 404