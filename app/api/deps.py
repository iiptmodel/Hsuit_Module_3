from sqlalchemy.orm import Session
from app.db import database

def get_db():
    """Dependency to get a DB session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
