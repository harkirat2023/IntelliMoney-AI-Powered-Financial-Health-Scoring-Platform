from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get("X-Request-ID", "")
    if isinstance(exc, AppException):
        logger.warning(
            "%s %s -> %s: %s",
            request.method,
            request.url.path,
            exc.code,
            exc.detail,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.detail,
                    "request_id": request_id,
                }
            },
        )
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        },
    )
