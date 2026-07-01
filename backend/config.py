from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env"
    )

    DATABASE_URL: str
    ENV: str
    SALT: str
    JWT_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str | None = None
    FRONTEND_URL: str | None = None

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_SECURE: bool = False

    # LiteLLM proxy
    LITELLM_API_KEY: str
    LITELLM_BASE_URL: str = "http://localhost:4000"

env = Config() #type: ignore
