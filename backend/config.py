from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env"
    )

    DATABASE_URL: str
    ENV: str
    SALT: str
    JWT_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str | None = None
    FRONTEND_URL: str | None = None

env = Config() #type: ignore
