from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DATABASE_URL.startswith("https://"):
            print(f"Warning: Invalid DATABASE_URL '{self.DATABASE_URL}'. Falling back to SQLite.")
            self.DATABASE_URL = "sqlite:///./medanalyzer.db"

settings = Settings()
