"""
Database Configuration and Connection Management

This module sets up SQLAlchemy engine, session management, and connection pooling.

Features:
- Automatic connection pooling with health checks
- PostgreSQL connection optimization with keepalives
- Fallback to SQLite on connection failure
- Session management via dependency injection
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE ENGINE SETUP
# ============================================================================

try:
    # Configure connection pool settings for production use
    engine_kwargs = {
        "poolclass": QueuePool,
        "pool_size": 5,              # Number of connections to maintain in pool
        "max_overflow": 10,          # Additional connections when pool is full
        "pool_pre_ping": True,       # Verify connections before use (prevents stale connections)
        "pool_recycle": 3600,        # Recycle connections after 1 hour
        "connect_args": {}
    }
    
    # PostgreSQL-specific optimizations
    if settings.DATABASE_URL.startswith("postgres://") or settings.DATABASE_URL.startswith("postgresql://"):
        logger.info("Configuring PostgreSQL connection with keepalive settings")
        engine_kwargs["connect_args"]["connect_timeout"] = 10
        engine_kwargs["connect_args"]["keepalives"] = 1
        engine_kwargs["connect_args"]["keepalives_idle"] = 30
        engine_kwargs["connect_args"]["keepalives_interval"] = 10
        engine_kwargs["connect_args"]["keepalives_count"] = 5
        engine_kwargs["connect_args"]["sslmode"] = "prefer"  # Prefer SSL when available
    
    # Create the database engine
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_SQL,  # Log SQL queries if enabled in settings
        **engine_kwargs
    )
    
    # Test connection on startup
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    logger.info("✅ Database connection established successfully")
    logger.debug(f"Database URL: {settings.DATABASE_URL}")
    
except Exception as e:
    # Fallback to SQLite if primary database fails
    logger.warning(
        "⚠️  Failed to connect to DATABASE_URL=%s. Error: %s. Falling back to SQLite.",
        settings.DATABASE_URL,
        e,
    )
    engine = create_engine(
        "sqlite:///./dev_fallback.db",
        connect_args={"check_same_thread": False},  # SQLite-specific: allow multi-threading
        echo=settings.LOG_SQL
    )
    logger.info("Using fallback SQLite database: dev_fallback.db")


# ============================================================================
# CONNECTION EVENT HANDLERS
# ============================================================================

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Track connection IDs for debugging and connection lifecycle management."""
    connection_record.info['pid'] = id(dbapi_conn)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# Session factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # Require explicit commits
    autoflush=False,   # Don't auto-flush before queries
    bind=engine
)

# Base class for all SQLAlchemy models
Base = declarative_base()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db():
    """
    FastAPI dependency to provide database sessions.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
