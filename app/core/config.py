"""
Application Configuration Settings

This module manages all application configuration using Pydantic Settings.
Configuration can be provided via:
1. Environment variables
2. .env file in project root
3. Default values (as specified below)

Environment Variables:
- DATABASE_URL: Database connection string (default: sqlite:///./medanalyzer.db)
- JWT_SECRET_KEY: Secret key for JWT token generation (REQUIRED)
- ALGORITHM: JWT algorithm (default: HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time (default: 60)
- LOG_LEVEL: Logging verbosity - DEBUG, INFO, WARNING, ERROR (default: INFO)
- LOG_SQL: Enable SQLAlchemy SQL query logging (default: False)
- DEBUG: Enable debug mode for verbose service logs (default: False)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with validation and type checking.
    
    All settings can be overridden via environment variables or .env file.
    """
    
    # ========== DATABASE CONFIGURATION ==========
    DATABASE_URL: str = "sqlite:///./medanalyzer.db"
    """Database connection URL. Supports SQLite, PostgreSQL, MySQL, etc."""
    
    # ========== SECURITY CONFIGURATION ==========
    JWT_SECRET_KEY: str
    """Secret key for JWT token signing. MUST be set via environment variable."""
    
    ALGORITHM: str = "HS256"
    """JWT signing algorithm."""
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    """JWT token expiration time in minutes."""
    
    # ========== LOGGING & DEBUGGING ==========
    LOG_LEVEL: str = "INFO"
    """Logging verbosity level: DEBUG, INFO, WARNING, ERROR, CRITICAL."""
    
    LOG_SQL: bool = False
    """If True, SQLAlchemy will log all SQL queries (verbose!)."""
    
    DEBUG: bool = False
    """If True, enable extra verbose logging in services."""
    
    # ========== AI MODEL CONFIGURATION ==========
    MODEL_NAME: str
    """Ollama model name for medical analysis and chat."""

    # Pydantic configuration
    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **kwargs):
        """
        Initialize settings with validation.
        
        Validates DATABASE_URL and falls back to SQLite if invalid.
        """
        super().__init__(**kwargs)
        
        # Validate DATABASE_URL (catch common mistakes)
        if self.DATABASE_URL.startswith("https://"):
            logger.warning(
                "Invalid DATABASE_URL '%s' (HTTPS not supported). "
                "Falling back to SQLite.",
                self.DATABASE_URL
            )
            self.DATABASE_URL = "sqlite:///./medanalyzer.db"


# Global settings instance
settings = Settings()
