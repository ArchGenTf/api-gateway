import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.status import HTTP_502_BAD_GATEWAY
from config import Settings, get_settings
from utils.correlation import get_correlation_id
from starlette.background import BackgroundTask


async def cleanup(resp, client):
    await resp.aclose()
    await client.aclose()


router = APIRouter()


# Health endpoints
@router.get("/healthz")
async def healthz():
    return JSONResponse(content={"status": "healthy"})


@router.get("/ready")
@router.get("/readyz")
async def readyz():
    return JSONResponse(content={"status": "ready"})


# Proxy endpoint – catches all /api/* routes
@router.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(full_path: str, request: Request):
    settings: Settings = get_settings()
    # Determine target service based on path
    path = f"/api/{full_path}"
    if path.startswith("/api/auth/"):
        base_url = str(settings.AUTH_SERVICE_URL).rstrip("/")
    elif path.startswith("/api/projects"):
        base_url = str(settings.PROJECT_SERVICE_URL).rstrip("/")
    else:
        base_url = str(settings.ARCHITECTURE_SERVICE_URL).rstrip("/")

    # Build the forward URL preserving query parameters
    query = request.url.query
    forward_url = f"{base_url}/{full_path}"
    if query:
        forward_url = f"{forward_url}?{query}"

    # Prepare headers – forward everything except hop‑by‑hop headers
    hop_by_hop = {"host", "connection", "content-length", "transfer-encoding", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "upgrade"}
    headers = {k: v for k, v in request.headers.items() if k.lower() not in hop_by_hop}
    correlation_id = get_correlation_id(request)
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id

    # Read body (may be empty)
    body = await request.body()

    timeout = settings.GATEWAY_REQUEST_TIMEOUT
    client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    try:
        req = client.build_request(request.method, forward_url, headers=headers, content=body)
        resp = await client.send(req, stream=True)
        # Streaming response back to the client, preserving status and headers
        streaming_response = StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=dict(resp.headers),
            background=BackgroundTask(cleanup, resp, client)
        )
        if correlation_id:
            streaming_response.headers["X-Correlation-Id"] = correlation_id
        return streaming_response
    except httpx.RequestError as exc:
        await client.aclose()
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail=str(exc))
