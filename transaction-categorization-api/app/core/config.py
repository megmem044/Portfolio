"""Load application settings from defaults and an optional .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


# Configuration values are defined in this class
# Environment variables are automatically read
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Transaction Categorization API"
    database_url: str = "sqlite:///./transactions.db"


settings = Settings()
