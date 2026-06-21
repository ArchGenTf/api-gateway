from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from config import Settings


def add_cors(app: FastAPI, settings: Settings) -> None:
    # Combine dev origins and production origin
    origins = settings.ALLOWED_ORIGINS.split(",") + [settings.PRODUCTION_ORIGIN]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex="https?://.*",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Correlation-Id"],
        max_age=86400,
    )
