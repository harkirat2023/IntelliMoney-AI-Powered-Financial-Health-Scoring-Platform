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
    await connect_to_mongo()
    categorizer.load()
    await cache_client.connect()
    logger.info("IntelliMoney backend started successfully")
    yield
    await cache_client.close()
    await close_mongo_connection()
    logger.info("IntelliMoney backend shut down")


setup_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

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


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/{path:path}")
async def legacy_redirect(path: str):
    if path == "health":
        return await health()
    return RedirectResponse(url=f"/api/v1/{path}")
