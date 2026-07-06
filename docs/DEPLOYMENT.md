# IntelliMoney Deployment Guide

## 1. Prerequisites

| Dependency | Minimum Version | Required |
|------------|----------------|----------|
| Python | 3.11+ | Yes |
| Node.js | 18+ | Yes |
| MongoDB | 7+ | Yes |
| Docker Desktop | Latest | Optional |
| Git | Any | Yes |

## 2. Environment Setup

### Backend (`backend/.env`)

Create `backend/.env` by copying `backend/.env.example`:

```ini
APP_NAME=IntelliMoney
ENVIRONMENT=development
SECRET_KEY=<generate-a-random-secret>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=intellimoney
REDIS_URL=
LOG_LEVEL=INFO
BANK_ENCRYPTION_KEY=<generate-a-fernet-key>
BANK_CONSENT_REDIRECT_BASE=http://localhost:5173/connect-bank/consent
```

Key variables:

- **SECRET_KEY**: JWT signing secret. Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- **BANK_ENCRYPTION_KEY**: Fernet key for field-level encryption of bank credentials. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- **MONGODB_URL**: Connection string for MongoDB. Supports local (`mongodb://localhost:27017`) or MongoDB Atlas.
- **MONGODB_DB**: Database name (default: `intellimoney`).
- **OPENAI_API_KEY**: Required for AI Copilot features. Set to empty string to disable.
- **UPLOAD_DIR**: Directory for receipt uploads (default: `uploads/receipts`). Created automatically on startup.

### Frontend (`frontend/.env`)

```ini
API_BASE_URL=http://localhost:8080/api/v1
```

This variable controls the base URL for all API requests from the frontend Axios client. The default value points to the backend dev server on port 8080.

## 3. Development Deployment (Local)

### One-Click Startup

Double-click `scripts/start-IntelliMoney.bat`. The script performs seven steps automatically:

1. **Environment Validation**: Checks for Git, Python, Node.js, npm, and Docker. Verifies `backend/.env` exists and `SECRET_KEY` is configured.
2. **Docker Containers**: Runs `docker compose up -d` to start MongoDB and Redis (optional). Waits up to 60 seconds for containers to become healthy.
3. **Backend Setup**: Creates a Python virtual environment (`backend/venv`), installs dependencies from `requirements.txt`, creates the `uploads/receipts` directory, runs database index creation, and starts `uvicorn app.main:app --reload --host 0.0.0.0 --port 8080`.
4. **Frontend Setup**: Installs npm packages (if `node_modules` missing or incomplete) and starts the Webpack dev server on port 5173 via `npm run dev`.
5. **Health Checks**: Verifies backend API, frontend, MongoDB connection, Docker containers, WebSocket endpoint, OpenAI API key, and JWT secret configuration.
6. **Open Browser**: Launches `http://localhost:5173` (or falls back to `http://localhost:8080/docs` if frontend is not ready).
7. **Summary**: Displays a status table of all services and writes results to `logs/startup.log`.

### Manual Startup

**Step 1: Start Infrastructure**

```bash
docker compose up -d
```

This starts MongoDB on port 27017 and Redis on port 6379.

**Step 2: Start Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

The backend API is available at `http://localhost:8080/api/v1` with interactive docs at `http://localhost:8080/docs`.

**Step 3: Start Frontend**

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:5173`.

### Demo Data

```bash
cd backend
python -m seed_demo
```

This creates a demo user (`demo@example.com` / `password123`) with 6 sample expenses across Food, Transport, Entertainment, Shopping, and Rent categories, plus monthly budgets for each category.

## 4. Production Deployment (Docker Compose)

### Services

The `docker-compose.yml` defines five services:

| Service | Image / Build | Port | Purpose |
|---------|---------------|------|---------|
| mongodb | `mongo:7` | 27017 | Primary database |
| redis | `redis:7-alpine` | 6379 | Optional caching layer |
| backend | `docker/Dockerfile.backend` | 8080 | FastAPI application server |
| frontend | `docker/Dockerfile.frontend` | 80 | Nginx-served SPA |
| nginx | (included in frontend) | 80 | Reverse proxy |

### Environment-Specific Configuration

Create separate `.env` files per environment:

- `backend/.env.production`
- `backend/.env.staging`

Set `ENVIRONMENT=production` and configure appropriate database URLs, secrets, and CORS origins.

### SSL/TLS Setup via Nginx

Extend `docker/nginx/default.conf` with SSL termination:

```nginx
server {
    listen 443 ssl;
    server_name intellimoney.example.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location /api/ {
        proxy_pass http://backend:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://backend:8080/api/v1/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name intellimoney.example.com;
    return 301 https://$host$request_uri;
}
```

Mount certificate files via Docker volumes or use a reverse proxy like Traefik or Caddy for automated certificate management.

## 5. Docker Configuration

### Dockerfile.backend

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Dockerfile.frontend

Uses a multi-stage build:

- **Build Stage**: `node:20-alpine` installs dependencies with `npm ci` and runs `npm run build` to produce the `dist/` directory.
- **Serve Stage**: `nginx:alpine` copies the built assets into `/usr/share/nginx/html` and applies the Nginx configuration.

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Nginx Configuration (`docker/nginx/default.conf`)

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://backend:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
    }

    location /ws {
        proxy_pass http://backend:8080/api/v1/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Requests to `/api/*` are proxied to the backend service; all other requests serve the frontend SPA (with client-side routing fallback to `index.html`). WebSocket connections at `/ws` are upgraded and forwarded to the backend.

## 6. One-Click Startup Scripts

### `scripts/start-IntelliMoney.bat`

A 7-step automated startup script for Windows:

1. **Validate Environment**: Checks Git, Python, Node.js, npm, Docker; verifies `backend/.env` exists and `SECRET_KEY` is set.
2. **Start Docker**: Runs `docker compose up -d` and waits for all containers to become healthy.
3. **Setup Backend**: Creates Python venv, installs dependencies, creates `uploads/receipts` directory, runs index creation, starts `uvicorn` on port 8080.
4. **Setup Frontend**: Installs npm packages if needed, starts Webpack dev server on port 5173.
5. **Health Checks**: Verifies backend (`/api/health`), frontend (HTTP 200), MongoDB connection, Docker containers, WebSocket availability, OpenAI API key, and JWT secret.
6. **Open Browser**: Launches `http://localhost:5173`.
7. **Print Summary**: Displays service status table with URLs.

Logs are written to `logs/startup.log` with timestamps at each step.

### `scripts/stop-IntelliMoney.bat`

Gracefully stops all services:

1. Kills the backend (by window title `IntelliMoney Backend`, then by `uvicorn` process name).
2. Kills the frontend (by window title `IntelliMoney Frontend`, then by `node.exe` instances).
3. Runs `docker compose down` to stop MongoDB and Redis containers.
4. Cleans up lingering processes on ports 8080 and 5173.
5. Writes a shutdown timestamp to `logs/startup.log`.

## 7. Database Setup

MongoDB indexes are created automatically at application startup in `backend/app/db/mongodb.py`. The `connect_to_mongo()` function, called during the FastAPI lifespan, creates indexes across 35+ collections covering all modules:

| Collection | Indexes |
|------------|---------|
| users | email (unique) |
| expenses | (user_id, date), etc. |
| budgets | (user_id, category, month, year) unique |
| budget_alerts | (user_id, created_at), (user_id, budget_id, threshold) unique |
| financial_scores | (user_id, calculated_at) |
| recommendations | (user_id, created_at) |
| spending_anomalies | (user_id, created_at), (user_id, is_read) |
| budget_suggestions | (user_id, is_applied) |
| financial_reports | (user_id, generated_at), (user_id, report_type) |
| recurring_expenses | (user_id, is_active), (user_id, next_expected_date) |
| subscriptions | (user_id, is_active), (user_id, next_payment_date) |
| bank_accounts | (user_id, connection_status), (consent_handle) unique, (consent_expiry) TTL |
| consents | (user_id, bank_account_id), (consent_status, expires_at) |
| import_preferences | (user_id, bank_account_id) unique |
| bank_transactions | (user_id, bank_account_id, transaction_date), (provider_account_id, transaction_id) unique |
| sync_logs | (user_id, bank_account_id, created_at), (user_id, status) |
| financial_transactions | 7 indexes including (user_id, transaction_date), (bank_transaction_id) unique |
| merchant_dictionary | (merchant_name) unique |
| merchant_aliases | (alias_type, priority) |
| category_feedback | (user_id, created_at), (suggested_category) |
| transaction_tags | (user_id, name) unique |
| budget_usage | (user_id, budget_id, month, year) unique |
| dashboard_metrics | (user_id, period) unique |
| financial_metrics | (user_id, period) unique |
| cash_flow_summary | (user_id, year, month) unique |
| monthly_summary | (user_id, period) unique |
| processing_batches | (batch_id) unique, (created_at) TTL |
| notifications | (user_id, created_at), (user_id, read) |
| financial_health | (user_id, period) unique |
| financial_health_history | (user_id, period) unique |
| financial_health_factors | (user_id, period) |
| financial_risk_profile | (user_id, period) unique |
| health_recommendations | (user_id, priority, created_at), (user_id, dismissed) |
| budget_intelligence | (user_id, period) unique |
| budget_recommendations | (user_id, created_at), (user_id, dismissed) |
| budget_predictions | (user_id, period, category) unique |
| budget_opportunities | (user_id, dismissed) |
| budget_risk | (user_id, period) unique |
| chat_sessions | (user_id, updated_at) |
| chat_messages | (session_id, created_at), (user_id, created_at) |
| conversation_memory | (user_id, session_id) unique |
| conversation_summary | (user_id, session_id) unique |
| ai_feedback | (user_id, created_at), (session_id, message_id) |
| financial_goals | (user_id, created_at), (user_id, status) |
| goal_progress | (goal_id, period) unique |
| goal_recommendations | (user_id, created_at), (user_id, dismissed) |
| goal_predictions | (goal_id) unique |
| goal_notifications | (user_id, created_at) |
| receipts | (user_id, created_at), (user_id, status) |
| receipt_processing_logs | (receipt_id, created_at) |

To manually create indexes without starting the application:

```bash
cd scripts
python create_indexes.py
```

## 8. ML Model Training

### Training Script

Run `ml/train_model.py` to train the expense classifier:

```bash
python ml/train_model.py
```

The script:

1. Reads training data from `ml/data/expenses.csv` (columns: `description`, `category`).
2. Splits data into 80% training / 20% test sets with stratified sampling.
3. Builds a scikit-learn pipeline: `TfidfVectorizer(ngram_range=(1,2))` + `LogisticRegression(max_iter=1000)`.
4. Prints a classification report with precision, recall, and F1-score.
5. Saves the trained model to `backend/app/ml/expense_classifier.joblib`.

### Output

The model file is placed at `backend/app/ml/expense_classifier.joblib`. The backend loads this file at startup in `app/services/ml_service.py`. If the file does not exist, the system falls back to keyword-based classification.

### Scheduled Training

CI/CD pipelines (GitHub Actions) can trigger model retraining on new data. The model can also be retrained manually at any time; the running backend will pick up the new model on the next restart.

## 9. Troubleshooting

### Backend fails to start

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB not running | Start MongoDB or check `MONGODB_URL` in `.env` |
| `ModuleNotFoundError: No module named 'app'` | Wrong working directory | Run `uvicorn` from the `backend/` directory |
| `ImportError: No module named 'fastapi'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `ValueError: Invalid Fernet key` | `BANK_ENCRYPTION_KEY` is invalid | Generate a valid key with `cryptography.fernet` |

### Frontend fails to start

| Symptom | Cause | Fix |
|---------|-------|-----|
| `'npm' is not recognized` | Node.js not installed | Install Node.js 18+ |
| `Module not found: Error: Can't resolve 'react'` | Dependencies not installed | Run `npm install` |
| `ECONNREFUSED` in browser console | Backend not reachable | Ensure backend runs on port 8080 and `API_BASE_URL` is correct |
| Blank page with no errors | Webpack build failure | Check terminal for build errors, run `npm run build` to see full output |

### Docker issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `docker: command not found` | Docker Desktop not installed | Install Docker Desktop and ensure it is in PATH |
| `Cannot connect to the Docker daemon` | Docker Desktop not running | Start Docker Desktop manually |
| Port conflict on 27017 | Local MongoDB already running | Stop local MongoDB or change the Docker port mapping |
| Container exits immediately | Missing `.env` file | Ensure `backend/.env` exists with required variables |

### Database issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Duplicate key error` on insert | Index constraint violation | Drop the collection and restart, or use upsert operations |
| `Authentication failed` | Wrong MongoDB credentials | Check `MONGODB_URL` includes username/password if required |
| Slow queries | Missing indexes | Indexes are auto-created on startup; verify in MongoDB shell with `db.collection.getIndexes()` |

### ML model issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| All expenses categorized as "Other" | Model not trained or not found | Run `python ml/train_model.py` from the project root |
| `FileNotFoundError: ml/data/expenses.csv` | Training data missing | Create the CSV with `description` and `category` columns |
| Low accuracy | Insufficient training data | Add more labeled expense descriptions to the CSV and retrain |

### Port conflicts

| Port | Service | Default Use |
|------|---------|-------------|
| 8080 | Backend API | Command: `netstat -ano | findstr :8080` to identify the process |
| 5173 | Frontend dev server | Command: `netstat -ano | findstr :5173` to identify the process |
| 27017 | MongoDB | Stop local MongoDB service before starting Docker containers |
| 6379 | Redis | Optional; disable by leaving `REDIS_URL` empty in `.env` |
