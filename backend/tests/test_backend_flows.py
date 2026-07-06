import asyncio
from datetime import date
from types import SimpleNamespace

from bson import ObjectId
from fastapi import HTTPException

from app.api.deps import get_current_user
from app.api.routes import alerts, auth, budgets, expenses, financial_health, ml
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.schemas.ml import CategorizeRequest
from app.schemas.user import UserCreate, UserLogin
from app.services import analytics_service
from app.services.budget_service import get_budget_status


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

    def find(self, query):
        return FakeCursor([item for item in self.items if matches(item, query)])

    async def update_one(self, query, update):
        item = await self.find_one(query)
        if item:
            item.update(update.get("$set", {}))
            return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)

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


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()
        self.expenses = FakeCollection()
        self.budgets = FakeCollection()
        self.budget_alerts = FakeCollection()
        self.financial_scores = FakeCollection()
        self.recommendations = FakeCollection()


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
        elif actual != expected:
            return False
    return True


def make_user(email="user@example.com"):
    db = FakeDb()
    token = run(
        auth.register(
            UserCreate(
                name="Test User",
                email=email,
                password="password123",
                monthly_income=60000,
            ),
            db,
        )
    )
    user_doc = db.users.items[0]
    return db, token, user_doc


def test_register_login_and_current_user_dependency():
    db, token, user_doc = make_user()

    login_token = run(auth.login(UserLogin(email="user@example.com", password="password123"), db))
    assert login_token.user.email == "user@example.com"
    assert login_token.access_token

    current = run(get_current_user(token.access_token, db))
    assert current["_id"] == user_doc["_id"]

    try:
        run(auth.login(UserLogin(email="user@example.com", password="wrong"), db))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Invalid login should fail")


def test_expense_crud_and_filtering():
    db, _, user = make_user("expense@example.com")

    created = run(
        expenses.create_expense(
            ExpenseCreate(
                amount=320,
                description="uber ride to office",
                payment_method="UPI",
                date=date.today(),
            ),
            user,
            db,
        )
    )
    assert created.category == "Transport"

    listed = run(
        expenses.list_expenses(
            category="Transport",
            min_amount=None,
            max_amount=None,
            current_user=user,
            db=db,
        )
    )
    assert len(listed) == 1

    updated = run(
        expenses.update_expense(
            created.id,
            ExpenseUpdate(amount=400, category="Travel"),
            user,
            db,
        )
    )
    assert updated.amount == 400
    assert updated.category == "Travel"

    run(expenses.delete_expense(created.id, user, db))
    assert run(expenses.list_expenses(min_amount=None, max_amount=None, current_user=user, db=db)) == []


def test_budget_crud_status_and_analytics_summary():
    db, _, user = make_user("budget@example.com")
    today = date.today()

    run(
        expenses.create_expense(
            ExpenseCreate(
                amount=850,
                description="pizza delivery",
                category="Food",
                payment_method="Card",
                date=today,
            ),
            user,
            db,
        )
    )
    budget = run(
        budgets.create_budget(
            BudgetCreate(category="Food", limit=1000, month=today.month, year=today.year),
            user,
            db,
        )
    )

    statuses = run(get_budget_status(db, str(user["_id"])))
    assert statuses[0]["state"] == "warning"
    assert statuses[0]["percentage_used"] == 85

    updated = run(budgets.update_budget(budget.id, BudgetUpdate(limit=2000), user, db))
    assert updated.limit == 2000

    summary = run(analytics_service.get_summary(db, user))
    assert summary["total_spending"] == 850
    assert summary["top_category"] == "Food"

    run(budgets.delete_budget(budget.id, user, db))
    assert run(budgets.list_budgets(user, db)) == []


def test_financial_score_and_ml_endpoint():
    db, _, user = make_user("score@example.com")
    today = date.today()
    run(
        expenses.create_expense(
            ExpenseCreate(
                amount=5000,
                description="amazon headphones order",
                category="Shopping",
                payment_method="Card",
                date=today,
            ),
            user,
            db,
        )
    )

    score = run(financial_health.score(user, db))
    assert 0 <= score.score <= 100
    assert score.risk_level in {"Excellent", "Good", "Moderate", "Needs Attention"}
    assert len(db.financial_scores.items) == 1

    prediction = run(ml.categorize(CategorizeRequest(description="metro card recharge")))
    assert prediction.category == "Transport"
    assert prediction.confidence > 0


def test_budget_alert_thresholds_and_mark_read():
    db, _, user = make_user("alerts@example.com")
    today = date.today()
    budget = run(
        budgets.create_budget(
            BudgetCreate(category="Food", limit=1000, month=today.month, year=today.year),
            user,
            db,
        )
    )

    for amount, expected_threshold in [(750, 75), (150, 90), (100, 100)]:
        run(
            expenses.create_expense(
                ExpenseCreate(
                    amount=amount,
                    description="grocery shopping",
                    category="Food",
                    payment_method="UPI",
                    date=today,
                ),
                user,
                db,
            )
        )
        generated = run(alerts.get_alerts(user, db))
        assert any(alert.budget_id == budget.id and expected_threshold <= alert.percentage for alert in generated)

    generated = run(alerts.get_alerts(user, db))
    assert len(generated) == 3
    assert any("75%" in alert.message for alert in generated)
    assert any("90%" in alert.message for alert in generated)
    assert any("exceeded" in alert.message for alert in generated)
    assert all(not alert.read for alert in generated)

    read = run(alerts.read_alert(generated[0].id, user, db))
    assert read.read is True
