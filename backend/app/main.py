import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import logger, setup_logging
from app.core.middleware.error_handler import global_exception_handler
from app.core.middleware.request_id import RequestIDMiddleware
from app.core.middleware.request_logger import RequestLoggerMiddleware
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.infrastructure.cache.redis import cache_client
from app.services.ml_service import categorizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting IntelliMoney backend...")

    async def _run_task(coro, name: str):
        try:
            await coro
            logger.info("%s connected successfully", name)
        except Exception:
            logger.exception("%s failed to connect", name)

    await _run_task(connect_to_mongo(), "MongoDB")
    asyncio.create_task(_run_task(cache_client.connect(), "Redis"))
    categorizer.load()
    logger.info("IntelliMoney backend started successfully")
    yield
    try:
        await cache_client.close()
    except Exception:
        pass
    try:
        await close_mongo_connection()
    except Exception:
        pass
    logger.info("IntelliMoney backend shut down")


setup_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggerMiddleware)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
    }


@app.get("/api/health")
async def health() -> dict:
    from app.db.mongodb import database, connection_error
    db_ping = False
    if database is not None:
        try:
            await database.command("ping")
            db_ping = True
        except Exception:
            pass
    model_ok = categorizer._model is not None
    return {
        "status": "ok" if db_ping else "degraded",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "database": "connected" if db_ping else "disconnected",
        "connection_error": connection_error,
        "ml_model": "loaded" if model_ok else "not_loaded",
    }


@app.get("/api/{path:path}")
async def legacy_redirect(path: str):
    if path == "health":
        return await health()
    return RedirectResponse(url=f"/api/v1/{path}")
