import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - start
        request_id = response.headers.get("X-Request-ID", "")
        logger.info(
            "%s %s %s %.4f",
            request.method,
            request.url.path,
            response.status_code,
            duration,
            extra={"request_id": request_id},
        )
        return response
