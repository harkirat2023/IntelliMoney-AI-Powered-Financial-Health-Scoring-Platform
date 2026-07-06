import asyncio
from datetime import date, datetime
from types import SimpleNamespace

from bson import ObjectId
from fastapi import HTTPException

from app.api.deps import get_current_user
from app.api.routes import auth, budget_intelligence_v2
from app.schemas.user import UserCreate, UserLogin


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

    def to_list(self, length=None):
        items = self.items[:length] if length else self.items
        return _fake_async_list(items)

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self._index]
        self._index += 1
        return item


async def _fake_async_list(items):
    return items


class FakeCollection:
    def __init__(self, items=None):
        self.items = items or []

    async def insert_one(self, document):
        stored = dict(document)
        stored["_id"] = stored.get("_id", ObjectId())
        self.items.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    async def insert_many(self, documents, ordered=False):
        ids = []
        for doc in documents:
            result = await self.insert_one(doc)
            ids.append(result.inserted_id)
        return SimpleNamespace(inserted_ids=ids)

    async def find_one(self, query, **kwargs):
        items = list(self.items)
        sort = kwargs.get("sort")
        if sort:
            for key, direction in reversed(sort):
                items.sort(key=lambda item, k=key: item.get(k, 0), reverse=direction < 0)
        return next((item for item in items if matches(item, query)), None)

    def find(self, query):
        return FakeCursor([item for item in self.items if matches(item, query)])

    async def update_one(self, query, update, upsert=False):
        item = await self.find_one(query)
        if item:
            item.update(update.get("$set", {}))
            return SimpleNamespace(modified_count=1)
        elif upsert:
            new_item = dict(query)
            new_item.update(update.get("$set", {}))
            new_item["_id"] = ObjectId()
            self.items.append(new_item)
            return SimpleNamespace(modified_count=1, upserted_id=new_item["_id"])
        return SimpleNamespace(modified_count=0)

    async def find_one_and_update(self, query, update, upsert=False, **kwargs):
        item = await self.find_one(query)
        if item:
            item.update(update.get("$set", {}))
            return item
        elif upsert:
            new_item = dict(query)
            new_item.update(update.get("$set", {}))
            new_item["_id"] = ObjectId()
            self.items.append(new_item)
            return new_item
        return None

    async def delete_one(self, query):
        for index, item in enumerate(self.items):
            if matches(item, query):
                self.items.pop(index)
                return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)

    async def delete_many(self, query):
        before = len(self.items)
        self.items = [item for item in self.items if not matches(item, query)]
        return SimpleNamespace(deleted_count=before - len(self.items))

    def aggregate(self, pipeline):
        return FakeCursor(self._aggregate(pipeline))

    def _aggregate(self, pipeline):
        data = list(self.items)
        for stage in pipeline:
            if "$match" in stage:
                data = [d for d in data if matches(d, stage["$match"])]
            elif "$sort" in stage:
                for key, order in stage["$sort"].items():
                    data.sort(key=lambda d, k=key: d.get(k, 0), reverse=order < 0)
            elif "$group" in stage:
                grouped = {}
                for d in data:
                    key_parts = {}
                    for k, v in stage["$group"]["_id"].items():
                        if isinstance(v, dict) and "$month" in v:
                            val = d.get("transaction_date")
                            key_parts[k] = val.month if hasattr(val, "month") else 1
                        elif isinstance(v, dict) and "$year" in v:
                            val = d.get("transaction_date")
                            key_parts[k] = val.year if hasattr(val, "year") else 2026
                        else:
                            key_parts[k] = d.get(v, "")
                    group_key = tuple(key_parts.items())
                    if group_key not in grouped:
                        grouped[group_key] = {"_id": key_parts, "total": 0, "count": 0}
                    grouped[group_key]["total"] += d.get(stage["$group"].get("total", {}).get("$sum", "amount"), 0)
                    grouped[group_key]["count"] += 1
                data = list(grouped.values())
            elif "$limit" in stage:
                data = data[:stage["$limit"]]
            elif "$skip" in stage:
                data = data[stage["$skip"]:]
        return data


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()
        self.budget_intelligence = FakeCollection()
        self.budget_recommendations = FakeCollection()
        self.budget_predictions = FakeCollection()
        self.budget_opportunities = FakeCollection()
        self.budget_risk = FakeCollection()
        self.budget_usage = FakeCollection()
        self.financial_transactions = FakeCollection()
        self.financial_health = FakeCollection()
        self.subscriptions = FakeCollection()
        self.recurring_expenses = FakeCollection()
        self.budgets = FakeCollection()

    def __getitem__(self, key):
        return getattr(self, key, FakeCollection())


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
            if "$in" in expected and actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


def make_user(email="bi_test@example.com"):
    db = FakeDb()
    token = run(
        auth.register(
            UserCreate(
                name="BI Test User",
                email=email,
                password="password123",
                monthly_income=80000,
            ),
            db,
        )
    )
    user_doc = db.users.items[0]
    return db, token, user_doc


def seed_budget_usage(db, user_id, categories=None):
    if categories is None:
        categories = [
            {"category": "Food", "limit": 15000, "spent": 12000, "percentage_used": 80, "state": "warning"},
            {"category": "Shopping", "limit": 10000, "spent": 8500, "percentage_used": 85, "state": "warning"},
            {"category": "Bills", "limit": 8000, "spent": 7500, "percentage_used": 93.75, "state": "warning"},
            {"category": "Entertainment", "limit": 5000, "spent": 6200, "percentage_used": 124, "state": "over"},
            {"category": "Transport", "limit": 4000, "spent": 2800, "percentage_used": 70, "state": "safe"},
            {"category": "Groceries", "limit": 8000, "spent": 6000, "percentage_used": 75, "state": "safe"},
        ]
    for c in categories:
        run(db.budget_usage.insert_one({"user_id": user_id, **c}))


def seed_financial_transactions(db, user_id):
    today = date.today()
    txs = []
    categories_tx = {
        "Food": [(500, "zomato"), (300, "swiggy"), (1200, "restaurant")],
        "Shopping": [(2500, "amazon"), (1800, "myntra"), (1000, "flipkart")],
        "Bills": [(3500, "electricity"), (2000, "water"), (2000, "internet")],
        "Entertainment": [(800, "netflix"), (300, "spotify"), (500, "movie tickets"), (600, "game purchase")],
        "Transport": [(200, "uber"), (150, "metro"), (300, "fuel")],
        "Groceries": [(2500, "big basket"), (1500, "local store"), (2000, "d mart")],
    }
    for cat, entries in categories_tx.items():
        for amount, desc in entries:
            txs.append({
                "user_id": user_id,
                "assigned_category": cat,
                "amount": float(amount),
                "transaction_type": "DEBIT",
                "transaction_date": today,
                "original_description": desc,
            })
    run(db.financial_transactions.insert_many(txs))


def seed_financial_health(db, user_id):
    run(db.financial_health.insert_one({
        "user_id": user_id,
        "period": f"{date.today().year}-{date.today().month:02d}",
        "score": 58,
        "risk_level": "Moderate",
        "savings_rate": 12.5,
        "budget_adherence": 62.0,
        "expense_stability": 55.0,
        "calculated_at": datetime.utcnow(),
    }))


def seed_subscriptions(db, user_id):
    run(db.subscriptions.insert_many([
        {"user_id": user_id, "name": "Netflix", "amount": 799, "active": True},
        {"user_id": user_id, "name": "Spotify", "amount": 199, "active": True},
        {"user_id": user_id, "name": "Old Gym", "amount": 1500, "active": False},
    ]))


class TestBudgetIntelligence:
    def test_generate_and_get_current(self):
        db, _, user = make_user("bi_generate@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)
        seed_financial_health(db, uid)
        seed_subscriptions(db, uid)

        result = run(budget_intelligence_v2.intelligence_generate(user, db))
        assert result.period == f"{date.today().year}-{date.today().month:02d}"
        assert 0 <= result.budget_score <= 100
        assert result.recommendations_count >= 0
        assert result.opportunities_count >= 0
        assert result.message == "Budget intelligence generated successfully."

        current = run(budget_intelligence_v2.intelligence_current(user, db))
        assert current.period == result.period
        assert current.budget_score == result.budget_score
        assert len(current.categories) > 0
        assert current.category_count > 0

    def test_recalculate(self):
        db, _, user = make_user("bi_recalc@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)
        seed_financial_health(db, uid)

        first = run(budget_intelligence_v2.intelligence_generate(user, db))
        second = run(budget_intelligence_v2.intelligence_recalculate(user, db))
        assert second.period == first.period
        assert second.message == "Budget intelligence recalculated successfully."

    def test_get_recommendations(self):
        db, _, user = make_user("bi_recs@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)
        seed_financial_health(db, uid)

        run(budget_intelligence_v2.intelligence_generate(user, db))
        recs = run(budget_intelligence_v2.intelligence_recommendations(user, db))

        assert isinstance(recs, list)
        if recs:
            r = recs[0]
            assert r.id is not None
            assert r.title
            assert r.confidence_score >= 0
            assert r.priority in {"high", "medium", "low"}

    def test_get_optimization(self):
        db, _, user = make_user("bi_opt@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)

        run(budget_intelligence_v2.intelligence_generate(user, db))
        opt = run(budget_intelligence_v2.intelligence_optimization(user, db))
        assert opt.total_budget > 0
        assert len(opt.suggestions) > 0
        assert len(opt.insights) > 0

    def test_get_trends(self):
        db, _, user = make_user("bi_trends@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)

        run(budget_intelligence_v2.intelligence_generate(user, db))
        trends = run(budget_intelligence_v2.intelligence_trends(user, db))
        assert trends.period
        assert isinstance(trends.predictions, list)

    def test_get_risk(self):
        db, _, user = make_user("bi_risk@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)

        run(budget_intelligence_v2.intelligence_generate(user, db))
        risk = run(budget_intelligence_v2.intelligence_risk(user, db))
        assert risk.overall_risk_level in {"low", "medium", "high"}
        assert risk.overall_risk_score >= 0
        assert len(risk.categories) > 0

    def test_get_opportunities(self):
        db, _, user = make_user("bi_opps@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)
        seed_financial_health(db, uid)
        seed_subscriptions(db, uid)

        run(budget_intelligence_v2.intelligence_generate(user, db))
        opps = run(budget_intelligence_v2.intelligence_opportunities(user, db))

        assert isinstance(opps, list)
        if opps:
            o = opps[0]
            assert o.potential_savings >= 0
            assert o.annual_impact >= 0

    def test_generate_idempotent(self):
        db, _, user = make_user("bi_idem@test.com")
        uid = str(user["_id"])

        seed_budget_usage(db, uid)
        seed_financial_transactions(db, uid)

        first = run(budget_intelligence_v2.intelligence_generate(user, db))
        second = run(budget_intelligence_v2.intelligence_generate(user, db))
        assert "already generated" in second.message.lower()

    def test_current_before_generate_returns_404(self):
        db, _, user = make_user("bi_404@test.com")
        try:
            run(budget_intelligence_v2.intelligence_current(user, db))
        except HTTPException as exc:
            assert exc.status_code == 404
        except Exception:
            raise
