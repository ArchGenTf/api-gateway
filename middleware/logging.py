import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.correlation import get_or_set_correlation_id
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        correlation_id = get_or_set_correlation_id(request)
        # Log request details
        logger.bind(correlation_id=correlation_id).info(
            "request",
            method=request.method,
            path=str(request.url.path),
            query=str(request.url.query),
        )
        response: Response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        logger.bind(correlation_id=correlation_id).info(
            "response",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        # Ensure correlation id header is present in response
        response.headers["X-Correlation-Id"] = correlation_id
        return response


# Helper to add middleware in app creation
def add_logging(app):
    # Configure loguru if not already configured
    try:
        logger.remove(0)
    except ValueError:
        pass
    logger.add("gateway.log", rotation="10 MB", level="INFO", format="{time} | {level} | {message}")
    app.add_middleware(LoggingMiddleware)
