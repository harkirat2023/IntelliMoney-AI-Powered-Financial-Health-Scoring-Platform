import asyncio
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.routes import auth
from app.core import clerk as clerk_mod
from app.core.clerk import ClerkError
from app.utils.date_utils import utc_now


def run(coro):
    return asyncio.run(coro)


class FakeCursor:
    def __init__(self, items):
        self.items = list(items)

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
    def __init__(self):
        self.items = []

    async def insert_one(self, document):
        stored = dict(document)
        stored["_id"] = stored.get("_id", ObjectId())
        self.items.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    async def find_one(self, query):
        return next((item for item in self.items if matches(item, query)), None)

    async def update_one(self, query, update):
        item = await self.find_one(query)
        if item:
            item.update(update.get("$set", {}))
            return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()


def matches(item, query):
    return all(item.get(key) == expected for key, expected in query.items())


def make_claims(sub="user_new_1", email="aarav@example.com"):
    return {
        "sub": sub,
        "sid": f"session_{sub}",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "claims": {"email_addresses": [{"email_address": email}]},
    }


def make_claims_without_email(sub="user_new_2"):
    return {
        "sub": sub,
        "sid": f"session_{sub}",
        "first_name": "Aarav",
        "last_name": "Sharma",
    }


def bearer(token="clerk-test-token"):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def set_valid_token(monkeypatch, claims=None):
    async def fake_validate(token):
        return claims if claims is not None else make_claims()

    monkeypatch.setattr(auth, "validate_bearer_token", fake_validate)


def set_invalid_token(monkeypatch):
    async def fake_validate(token):
        return None

    monkeypatch.setattr(auth, "validate_bearer_token", fake_validate)


def make_verifier(monkeypatch, parties):
    fake = SimpleNamespace(
        clerk_frontend_api="leading-mako-8560.clerk.accounts.dev",
        clerk_publishable_key="pk_test_ignored",
        clerk_jwt_authorized_parties=parties,
    )
    monkeypatch.setattr(clerk_mod, "get_settings", lambda: fake)
    return clerk_mod.ClerkVerifier()


def test_clerk_sync_new_user_is_marked_new(monkeypatch):
    db = FakeDb()
    set_valid_token(monkeypatch)

    result = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))

    assert result.is_new_user is True
    assert result.is_onboarded is False
    assert result.clerk_user_id == "user_new_1"
    assert result.email == "aarav@example.com"
    assert len(db.users.items) == 1


def make_user_doc(sub="user_new_1", email="aarav@example.com"):
    return {
        "_id": ObjectId(),
        "clerk_user_id": sub,
        "name": "Aarav Sharma",
        "email": email,
        "monthly_income": 0.0,
        "is_verified": True,
        "is_onboarded": False,
        "auth_provider": "clerk",
        "created_at": utc_now(),
    }


def test_clerk_sync_existing_user_is_not_new(monkeypatch):
    db = FakeDb()
    run(db.users.insert_one(make_user_doc()))
    set_valid_token(monkeypatch)

    result = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))

    assert result.is_new_user is False
    assert len(db.users.items) == 1


def test_clerk_sync_duplicate_login_is_idempotent(monkeypatch):
    db = FakeDb()
    set_valid_token(monkeypatch)

    first = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))
    second = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))

    assert first.is_new_user is True
    assert second.is_new_user is False
    assert second.id == first.id
    assert len(db.users.items) == 1


def test_clerk_sync_invalid_token_rejected_without_creating_user(monkeypatch):
    db = FakeDb()
    set_invalid_token(monkeypatch)

    with pytest.raises(HTTPException) as excinfo:
        run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))

    assert excinfo.value.status_code == 401
    assert len(db.users.items) == 0


def test_clerk_sync_missing_credentials_rejected():
    with pytest.raises(HTTPException) as excinfo:
        run(auth.clerk_sync(payload=None, credentials=None, db=FakeDb()))

    assert excinfo.value.status_code == 401


def test_clerk_sync_uses_client_email_when_token_has_none(monkeypatch):
    db = FakeDb()
    set_valid_token(monkeypatch, make_claims_without_email())
    from app.schemas.user import ClerkSyncRequest

    result = run(
        auth.clerk_sync(
            payload=ClerkSyncRequest(name="Aarav Sharma", email="aarav@example.com"),
            credentials=bearer(),
            db=db,
        )
    )

    assert result.is_new_user is True
    assert result.email == "aarav@example.com"
    assert run(db.users.find_one({"clerk_user_id": "user_new_2"}))["email"] == "aarav@example.com"


def test_clerk_sync_tolerates_missing_email(monkeypatch):
    db = FakeDb()
    set_valid_token(monkeypatch, make_claims_without_email())

    result = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))

    assert result.email is None
    assert len(db.users.items) == 1


def test_complete_onboarding_persists_flag(monkeypatch):
    db = FakeDb()
    set_valid_token(monkeypatch)
    user = run(auth.clerk_sync(payload=None, credentials=bearer(), db=db))
    stored = run(db.users.find_one({"clerk_user_id": "user_new_1"}))

    completed = run(auth.complete_onboarding(current_user=stored, db=db))

    assert completed.is_onboarded is True
    assert run(db.users.find_one({"_id": stored["_id"]}))["is_onboarded"] is True


def test_validate_claims_accepts_authorized_token(monkeypatch):
    verifier = make_verifier(monkeypatch, "https://intellimoney.vercel.app")
    claims = {
        "sub": "user_123",
        "sid": "sess_1",
        "iss": "https://leading-mako-8560.clerk.accounts.dev",
        "azp": "https://intellimoney.vercel.app",
    }
    assert verifier._validate_claims(claims)["sub"] == "user_123"


def test_validate_claims_rejects_unknown_issuer(monkeypatch):
    verifier = make_verifier(monkeypatch, "https://intellimoney.vercel.app")
    claims = {
        "sub": "user_123",
        "sid": "sess_1",
        "iss": "https://other.clerk.accounts.dev",
        "azp": "https://intellimoney.vercel.app",
    }
    with pytest.raises(ClerkError):
        verifier._validate_claims(claims)


def test_validate_claims_rejects_unknown_azp(monkeypatch):
    verifier = make_verifier(monkeypatch, "https://intellimoney.vercel.app")
    claims = {
        "sub": "user_123",
        "sid": "sess_1",
        "iss": "https://leading-mako-8560.clerk.accounts.dev",
        "azp": "https://evil.example.com",
    }
    with pytest.raises(ClerkError):
        verifier._validate_claims(claims)


def test_validate_claims_allows_missing_azp(monkeypatch):
    verifier = make_verifier(monkeypatch, "https://intellimoney.vercel.app")
    claims = {
        "sub": "user_123",
        "sid": "sess_1",
        "iss": "https://leading-mako-8560.clerk.accounts.dev",
    }
    assert verifier._validate_claims(claims)["sub"] == "user_123"


def test_validate_claims_skips_azp_when_allowlist_unconfigured(monkeypatch):
    verifier = make_verifier(monkeypatch, "")
    claims = {
        "sub": "user_123",
        "sid": "sess_1",
        "iss": "https://leading-mako-8560.clerk.accounts.dev",
        "azp": "https://any.example.com",
    }
    assert verifier._validate_claims(claims)["sub"] == "user_123"


def test_validate_claims_requires_subject_and_session(monkeypatch):
    verifier = make_verifier(monkeypatch, "")
    with pytest.raises(ClerkError):
        verifier._validate_claims({"sid": "sess_1"})
    with pytest.raises(ClerkError):
        verifier._validate_claims({"sub": "user_123"})


def test_authorized_parties_are_normalized(monkeypatch):
    verifier = make_verifier(monkeypatch, " https://intellimoney.vercel.app, http://localhost:5173/ ")
    parties = verifier.authorized_parties
    assert "https://intellimoney.vercel.app" in parties
    assert "http://localhost:5173" in parties
    assert "https://leading-mako-8560.clerk.accounts.dev" in parties