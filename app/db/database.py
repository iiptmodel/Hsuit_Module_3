from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create the engine with connection pooling and retry logic
try:
    # Configure engine with proper connection pool settings
    engine_kwargs = {
        "poolclass": QueuePool,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verify connections before using them
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "connect_args": {}
    }
    
    # Add SSL settings for PostgreSQL if using postgres://
    if settings.DATABASE_URL.startswith("postgres://") or settings.DATABASE_URL.startswith("postgresql://"):
        engine_kwargs["connect_args"]["connect_timeout"] = 10
        engine_kwargs["connect_args"]["keepalives"] = 1
        engine_kwargs["connect_args"]["keepalives_idle"] = 30
        engine_kwargs["connect_args"]["keepalives_interval"] = 10
        engine_kwargs["connect_args"]["keepalives_count"] = 5
        # For SSL connections
        engine_kwargs["connect_args"]["sslmode"] = "prefer"
    
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    
    # Test the connection
    with engine.connect() as conn:
        # SQLAlchemy 1.x/2.x require an executable object; use text() to be compatible
        conn.execute(text("SELECT 1"))
    logger.info("Database connection established successfully")
    
except Exception as e:
    logger.warning(
        "Failed to create DB engine with DATABASE_URL=%s; falling back to sqlite. Error: %s",
        settings.DATABASE_URL,
        e,
    )
    engine = create_engine(
        "sqlite:///./dev_fallback.db",
        connect_args={"check_same_thread": False}
    )

# Handle disconnections
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    connection_record.info['pid'] = id(dbapi_conn)

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
