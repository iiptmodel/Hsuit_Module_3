from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create the engine with a safe fallback for local development
try:
    engine = create_engine(settings.DATABASE_URL)
except Exception as e:
    logger.warning(
        "Failed to create DB engine with DATABASE_URL=%s; falling back to sqlite. Error: %s",
        settings.DATABASE_URL,
        e,
    )
    engine = create_engine("sqlite:///./dev_fallback.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def get_db():
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
