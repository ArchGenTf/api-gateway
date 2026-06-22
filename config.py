from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class Settings(BaseSettings):
    # Core settings
    GATEWAY_PORT: int = Field(8080, env="GATEWAY_PORT")
    GATEWAY_REQUEST_TIMEOUT: int = Field(300, env="GATEWAY_REQUEST_TIMEOUT")
    PRODUCTION_ORIGIN: str = Field(..., env="PRODUCTION_ORIGIN")

    # Service URLs
    AUTH_SERVICE_URL: AnyUrl = Field(..., env="AUTH_SERVICE_URL")
    PROJECT_SERVICE_URL: AnyUrl = Field(..., env="PROJECT_SERVICE_URL")
    ARCHITECTURE_SERVICE_URL: AnyUrl = Field(..., env="ARCHITECTURE_SERVICE_URL")

    # CORS allowed origins (dev)
    ALLOWED_ORIGINS: str = Field("http://localhost:3000,http://localhost:5173", env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton for FastAPI to access settings via app.state.settings
def get_settings() -> Settings:
    return Settings()
