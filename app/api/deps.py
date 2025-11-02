from sqlalchemy.orm import Session
from app.db import database

def get_db():
    """FastAPI dependency to get a DB session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
