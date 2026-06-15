# IntelliMoney

IntelliMoney is an AI-powered financial health scoring platform for expense tracking, budget monitoring, dashboard analytics, personalized recommendations, and NLP-based expense categorization.

## Tech Stack

- Frontend: React.js, Vite, React Router, Axios, Recharts, Lucide icons
- Backend: Python, FastAPI, Pydantic, JWT authentication
- Database: MongoDB with Motor async driver
- ML/NLP: Scikit-learn, TF-IDF Vectorizer, Logistic Regression, Joblib

## Features

- Secure registration and login with JWT authentication.
- Expense CRUD with filters by category, payment method, date, and amount.
- Automated expense categorization from transaction descriptions.
- Budget creation and current-month budget usage tracking.
- Dashboard with monthly spending, income, estimated savings, category distribution, trends, and recent transactions.
- Financial health scoring from savings rate, budget adherence, spending stability, and discretionary category risk.
- Rule-based personalized recommendations based on spending and budget behavior.

## Project Structure

```text
backend/   FastAPI app, MongoDB access, auth, analytics, recommendations, ML prediction
frontend/  React/Vite dashboard application
ml/        Training data and Logistic Regression + TF-IDF training script
docs/      Extra project documentation
```

## Local Setup

### 1. MongoDB

Use either local MongoDB or MongoDB Atlas. Set the connection string in `backend/.env`.

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The API will run at `http://localhost:8000`.

### 3. Train the NLP Model

From the repository root:

```bash
python ml/train_model.py
```

This writes `backend/app/ml/expense_classifier.joblib`. If the file is absent, the API uses a keyword fallback so development can continue.

### 4. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The app will run at `http://localhost:5173`.

## Core API Routes

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/expenses`
- `GET /api/expenses`
- `PUT /api/expenses/{id}`
- `DELETE /api/expenses/{id}`
- `POST /api/budgets`
- `GET /api/budgets`
- `GET /api/budgets/status`
- `GET /api/analytics/summary`
- `GET /api/analytics/monthly-spending`
- `GET /api/analytics/category-breakdown`
- `GET /api/financial-health/score`
- `GET /api/recommendations`
- `POST /api/ml/categorize`

## Resume-Ready Description

**IntelliMoney - AI-Powered Financial Health Scoring Platform**  
Built a full-stack financial analytics platform using Python, FastAPI, React.js, MongoDB, Scikit-learn, and NLP. Implemented secure JWT authentication, expense tracking, budget monitoring, dashboard insights, financial health scoring, personalized recommendations, and real-time automated expense categorization using a TF-IDF + Logistic Regression model.
