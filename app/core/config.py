from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Default to local SQLite for simplicity and to avoid external DB dependencies.
    DATABASE_URL: str = "sqlite:///./medanalyzer.db"
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DATABASE_URL.startswith("https://"):
            logger.warning("Invalid DATABASE_URL '%s'. Falling back to SQLite.", self.DATABASE_URL)
            self.DATABASE_URL = "sqlite:///./medanalyzer.db"

settings = Settings()
