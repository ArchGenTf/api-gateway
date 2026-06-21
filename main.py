import uvicorn
from fastapi import FastAPI
from config import Settings, get_settings
from router import router as api_router
from middleware.cors import add_cors
from middleware.logging import add_logging


def create_app() -> FastAPI:
    settings: Settings = get_settings()
    app = FastAPI(title="API Gateway", version="0.1.0")
    # Middleware
    add_cors(app, settings)
    add_logging(app)
    # Include router that proxies requests
    app.include_router(api_router)
    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.GATEWAY_PORT), log_level="info")
