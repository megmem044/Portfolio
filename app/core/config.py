from pydantic_settings import BaseSettings


# Configuration values are defined in this class
# Environment variables are automatically read
class Settings(BaseSettings):
    # Application name is defined
    app_name: str = "Transaction Categorization API"

    # Database connection URL is defined
    # SQLite is used for simplicity
    database_url: str = "sqlite:///./transactions.db"

    class Config:
        # Environment variables are loaded from a .env file
        env_file = ".env"


# A single settings object is created
# This object is imported wherever configuration is needed
settings = Settings()
