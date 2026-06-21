import uuid
from fastapi import Request

CORRELATION_HEADER = "X-Correlation-Id"

def get_or_set_correlation_id(request: Request) -> str:
    """Return existing correlation ID from request headers or state, otherwise generate a new one.
    The ID is stored in ``request.state.correlation_id`` for later middleware access.
    """
    # Prefer header if client sent one
    header_value = request.headers.get(CORRELATION_HEADER)
    if header_value:
        request.state.correlation_id = header_value
        return header_value
    # Otherwise generate a new UUID4
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    return correlation_id

def get_correlation_id(request: Request) -> str:
    """Retrieve the correlation ID from request.state if set, else ``None``."""
    return getattr(request.state, "correlation_id", None)
