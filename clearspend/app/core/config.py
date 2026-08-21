"""Load application settings from defaults and an optional .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


# Configuration values are defined in this class
# Environment variables are automatically read
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Transaction Categorization API"
    database_url: str = "sqlite:///./transactions.db"
    secret_key: str = "development-only-change-me"
    access_token_minutes: int = 30
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
