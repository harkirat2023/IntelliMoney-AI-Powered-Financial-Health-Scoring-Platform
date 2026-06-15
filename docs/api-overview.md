# API Overview

All private routes require `Authorization: Bearer <token>`.

## Auth

- `POST /api/auth/register`: create user and return JWT.
- `POST /api/auth/login`: authenticate user and return JWT.
- `GET /api/auth/me`: return current user profile.

## Expenses

- `POST /api/expenses`: create expense. If category is omitted, the NLP classifier predicts it.
- `GET /api/expenses`: list expenses with optional filters.
- `GET /api/expenses/{id}`: fetch one expense.
- `PUT /api/expenses/{id}`: update expense.
- `DELETE /api/expenses/{id}`: delete expense.

## Budgets

- `POST /api/budgets`: create category budget for month/year.
- `GET /api/budgets`: list budgets.
- `GET /api/budgets/status`: show usage, remaining amount, percentage, and warning state.
- `PUT /api/budgets/{id}`: update limit.
- `DELETE /api/budgets/{id}`: delete budget.

## Analytics and Intelligence

- `GET /api/analytics/summary`: monthly spending and savings summary.
- `GET /api/analytics/monthly-spending`: six-month trend data.
- `GET /api/analytics/category-breakdown`: current-month category totals.
- `GET /api/analytics/recent-expenses`: latest transactions.
- `GET /api/financial-health/score`: weighted financial health score.
- `GET /api/recommendations`: personalized recommendation cards.
- `POST /api/ml/categorize`: expense text category prediction.
