# Contributing to IntelliMoney

## 1. Getting Started

### Clone the Repository

```bash
git clone https://github.com/your-org/IntelliMoney.git
cd IntelliMoney
```

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and populate the required variables:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your own `SECRET_KEY` and `BANK_ENCRYPTION_KEY`.

Run the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```ini
API_BASE_URL=http://localhost:8080/api/v1
```

Run the frontend:

```bash
npm run dev
```

The application is now accessible at `http://localhost:5173` with the API at `http://localhost:8080/api/v1`.

## 2. Project Structure

```
IntelliMoney/
├── backend/
│   ├── app/
│   │   ├── ai/                    # AI Intelligence Pipeline services
│   │   ├── api/
│   │   │   ├── routes/            # Route handlers (one per module)
│   │   │   └── v1/
│   │   │       ├── router.py      # Aggregates all route modules
│   │   │       └── websocket.py   # WebSocket endpoint
│   │   ├── budget_intelligence/   # Budget Intelligence V2 module
│   │   │   ├── models/            # Domain models (Pydantic)
│   │   │   ├── repositories/      # Data access layer
│   │   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   └── services/          # Business logic
│   │   ├── copilot/               # AI Copilot module
│   │   │   ├── services/          # LLM, RAG, Memory, Tool services
│   │   │   ├── schemas.py
│   │   │   └── prompts.py
│   │   ├── core/                  # Configuration, security, middleware
│   │   ├── dashboard/             # Dashboard V2 services
│   │   ├── db/                    # MongoDB connection + indexes
│   │   ├── domain/                # Shared domain models + repository interfaces
│   │   ├── infrastructure/        # Caching, encryption, bank integration
│   │   ├── ml/                    # Trained ML model (expense_classifier.joblib)
│   │   ├── services/              # Shared business services
│   │   └── utils/                 # Utility functions
│   ├── tests/                     # Backend integration tests
│   ├── .env                       # Environment configuration
│   ├── requirements.txt
│   └── seed_demo.py               # Demo data seeder
├── frontend/
│   ├── src/
│   │   ├── api/                   # Axios API client modules (one per domain)
│   │   ├── auth/                  # Auth context
│   │   ├── components/            # Reusable UI components
│   │   ├── config/                # Constants and configuration
│   │   ├── dashboard/             # Dashboard V2 pages
│   │   ├── landing/               # Public landing pages
│   │   │   ├── layouts/
│   │   │   ├── pages/
│   │   │   └── sections/
│   │   ├── layouts/               # Module-specific sidebar layouts
│   │   ├── pages/                 # Application pages (organized by module)
│   │   ├── store/                 # Observer-pattern stores
│   │   ├── utils/                 # Utility functions
│   │   ├── App.jsx                # Route definitions
│   │   └── main.jsx               # Entry point
│   ├── .env
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx/default.conf
├── ml/
│   ├── data/
│   │   └── expenses.csv           # Training data
│   └── train_model.py             # ML training script
├── scripts/
│   ├── start-IntelliMoney.bat
│   ├── stop-IntelliMoney.bat
│   └── create_indexes.py
├── docker-compose.yml
├── CHANGELOG.md
└── README.md
```

### Backend Architecture (Layered)

The backend follows a layered architecture:

- **API Layer** (`app/api/routes/`): Route handlers. Each handler receives a request, delegates to a service, and returns a response. No business logic.
- **Domain Layer** (`app/domain/`, `app/*/models/`): Pydantic domain models with `from_mongo()` / `to_mongo()` serialization and business methods.
- **Service Layer** (`app/services/`, `app/*/services/`): Business logic and orchestration. Services depend on repository interfaces.
- **Infrastructure Layer** (`app/infrastructure/`, `app/*/repositories/`): MongoDB implementations of repository interfaces, caching, external integrations.

### Frontend Architecture

- **Pages** (`src/pages/`): Page-level components that compose layouts and sections. One directory per module.
- **Layouts** (`src/layouts/`): Sidebar navigation layouts for module sub-pages.
- **API Clients** (`src/api/`): Axios-based modules with one file per domain.
- **Stores** (`src/store/`): Observer-pattern state management modules (plain JavaScript classes with subscriber lists).
- **Components** (`src/components/`): Shared UI primitives and composition components.

## 3. Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feat/my-feature
   ```

2. Write code following the project's coding standards (see Section 4).

3. Run tests locally:
   ```bash
   cd backend
   pytest tests/ -v
   ```

4. Commit changes with a descriptive message:
   ```bash
   git add .
   git commit -m "feat: add brief description of change"
   ```

5. Push and open a pull request:
   ```bash
   git push origin feat/my-feature
   ```
   Then create a PR on GitHub against the `main` branch.

## 4. Coding Standards

### Python

- **Framework**: FastAPI for REST endpoints. Use `APIRouter` for route grouping.
- **Validation**: Pydantic v2 with `BaseModel` and `Field` validators for all request/response schemas.
- **Database**: Motor (async MongoDB driver) with `AsyncIOMotorClient`. Use `async/await` throughout.
- **Type Hints**: Required for all function signatures, including return types.
- **Exception Handling**: Use the custom exception hierarchy in `app/core/exceptions.py` (AppException, NotFoundException, ValidationException, AuthException, ConflictException, etc.).
- **Configuration**: Pydantic Settings via `app/core/config.py`. Access with `get_settings()`.
- **Repository Pattern**: Abstract repository interfaces in `app/domain/` with Mongo implementations in `app/infrastructure/` or module-specific `repositories/` directories.
- **Dependency Injection**: Use FastAPI `Depends` for auth (`get_current_user` in `app/api/deps.py`) and database access.

### JavaScript (React 19)

- **Framework**: React 19 with JSX. Components are functional with hooks.
- **Routing**: React Router DOM v7 for client-side routing.
- **HTTP Client**: Axios with JWT interceptor (see `src/api/client.js`).
- **State Management**: Observer-pattern stores (not Redux or Zustand). Each store is a plain JavaScript class with `subscribe()`, `notify()`, and state getter/setter methods.
- **Styling**: Tailwind CSS 3 with `clsx` and `tailwind-merge` for conditional class composition.
- **Animations**: Framer Motion for page transitions and micro-interactions.
- **UI Primitives**: Radix UI for accessible accordion, dialog, and navigation menu primitives.

### General

- No comments in code unless they explain a non-obvious design decision. Code should be self-documenting through clear naming and structure.
- Follow existing patterns in the codebase. If a module follows a specific structure, replicate that structure for new additions.
- Use descriptive variable and function names. Prefer verbose names over abbreviations.
- Keep functions small and focused on a single responsibility.

## 5. Testing

### Backend Tests

- **Framework**: `pytest` with `httpx` for async HTTP testing.
- **Location**: All test files reside in `backend/tests/`.
- **Approach**: Integration tests using `FakeCollection` (in-memory mock of MongoDB collection with `insert_one`, `find_one`, `find`, `update_one`, `delete_one`, `count_documents`, and `create_index`) and `FakeCursor` (async iterator with `sort` and `limit`).

Running tests:

```bash
cd backend
pytest tests/ -v
```

Existing test files:

- `test_backend_flows.py`: Integration tests for auth, expenses, budgets, analytics, financial health, ML categorization, alerts, anomaly detection, budget suggestions, reports, subscriptions, and recurring expenses.
- `test_budget_intelligence.py`: Tests for the Budget Intelligence V2 module with 9 integration tests.
- `test_ml_service.py`: Tests for the ML categorization service.

When adding new tests:

1. Create a new test file or extend an existing one in `backend/tests/`.
2. Use the existing `FakeCollection` / `FakeCursor` pattern for mocking MongoDB.
3. Import route handler functions directly and call them with test arguments.
4. Test both success and error cases (404, 409, 422, 401, 403).

## 6. Pull Request Process

1. **Update CHANGELOG.md**: Add an entry under the appropriate version header. Follow the existing format (`### Added`, `### Fixed`, `### Changed`, `### Security` sections).

2. **Update relevant documentation**: If the PR introduces new behavior, update the corresponding design document in `docs/` or add a new one.

3. **Ensure all tests pass**: Run `pytest tests/ -v` from the `backend/` directory and confirm zero failures.

4. **Code review**: At least one maintainer must review and approve the PR. Address all review comments before merging.

5. **Merge**: Use squash merge to maintain a clean commit history on `main`.

## 7. Adding a New Module

This guide describes the end-to-end process for adding a new feature module (e.g., a "Budget Intelligence" or "Receipt OCR" module).

### 7.1 Backend: Domain Models

Create domain models with Pydantic v2 in either:

- `backend/app/domain/<module>/models.py` -- for shared domain models with repository interfaces.
- `backend/app/<module>/models/` -- for module-scoped domain models (e.g., `backend/app/budget_intelligence/models/`).

Each model should include `from_mongo()` and `to_mongo()` classmethods for MongoDB serialization.

### 7.2 Backend: Repository Interface + Mongo Implementation

- Define an abstract repository interface (if using shared domain) or a concrete repository class (if module-scoped).
- Implement MongoDB methods using `motor` with proper index usage.
- Place repositories in `backend/app/<module>/repositories/`.
- Use `update_one(upsert=True)` for atomic upserts and `find_one_and_update` with filter conditions for TOCTOU-safe state transitions.

### 7.3 Backend: Service(s)

- Create service classes in `backend/app/<module>/services/`.
- Services should contain all business logic and orchestration.
- Inject repositories via constructor parameters.
- Publish domain events using the event bus for cross-module communication.

### 7.4 Backend: Route Handler

- Create a route file in `backend/app/api/routes/<module>.py` using `APIRouter(prefix="/...", tags=[...])`.
- Use FastAPI `Depends(get_current_user)` for JWT-protected endpoints.
- Return Pydantic response schemas.

### 7.5 Backend: Register Routes

- Add the route module to `backend/app/api/v1/router.py`:
  ```python
  from app.api.routes import my_module

  router.include_router(my_module.router, tags=["my-module"])
  ```

### 7.6 Backend: Add MongoDB Indexes

- Add `create_index` calls in the `connect_to_mongo()` function in `backend/app/db/mongodb.py`.
- Add unique indexes where appropriate for idempotency.
- Add TTL indexes for automatic document expiration where applicable.

### 7.7 Frontend: Create Pages

- Create a directory `frontend/src/pages/<module>/`.
- Add page components (e.g., OverviewPage, DetailPage, SettingsPage).
- Each page should use the existing UI primitives from `frontend/src/components/`.

### 7.8 Frontend: Add Routes

- Import page components in `frontend/src/App.jsx`.
- Add `<Route>` entries under the protected `/app` route group.
- Use the existing `ProtectedRoute` wrapper for authenticated routes.

### 7.9 Frontend: Create Layout

- Create a layout component in `frontend/src/layouts/<Module>Layout.jsx` with sidebar navigation links.
- Import and add the layout in `App.jsx` as a wrapper for the module's sub-routes.

### 7.10 Frontend: Add API Client

- Create an API client module in `frontend/src/api/<module>.js`.
- Export functions that use the shared `api` Axios instance from `frontend/src/api/client.js`.
- Each function should handle request/response and return parsed data.

### 7.11 Update Documentation

- Update this file (`CONTRIBUTING.md`) if the module introduction pattern changes.
- Update `ARCHITECTURE.md` to reflect new components.
- Update `CHANGELOG.md` with a summary of the added module.
