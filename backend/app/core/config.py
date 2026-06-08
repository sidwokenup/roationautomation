import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Palladium Automation API"
    API_V1_STR: str = "/api/v1"
    
    DEV_MODE: bool = os.getenv("DEV_MODE", "False").lower() == "true"
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # We delay evaluating the default DATABASE_URL so that if DEV_MODE is true, 
    # it immediately defaults to sqlite rather than trying to load a pg string.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    PALLADIUM_API_URL: str = "https://api.palladium.expert"
    PALLADIUM_API_TOKEN: str = os.getenv("PALLADIUM_API_TOKEN", "")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Adjust Database URL for SQLite if DEV_MODE is true
if settings.DEV_MODE:
    settings.DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
elif not settings.DATABASE_URL:
    # If in production but no database URL is provided, fallback to production SQLite
    settings.DATABASE_URL = "sqlite+aiosqlite:///./prod.db"