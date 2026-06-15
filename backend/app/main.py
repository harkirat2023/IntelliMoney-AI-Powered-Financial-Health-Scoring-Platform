from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, auth, budgets, expenses, financial_health, ml, recommendations
from app.core.config import get_settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.services.ml_service import categorizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    categorizer.load()
    yield
    await close_mongo_connection()


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(financial_health.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(ml.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
