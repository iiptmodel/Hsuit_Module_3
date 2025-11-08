"""
FastAPI Medical Analyzer Application

This is the main entry point for the Med Analyzer application, which provides:
- Medical report processing (text/image/PDF)
- AI-powered chat interface with medical Q&A
- Text-to-speech conversion for reports
- Integration with Ollama for LLM capabilities

Environment Variables:
- HF_HUB_DISABLE_SYMLINKS: Prevents symlink creation on Windows (set to "1")
- PRELOAD_MODELS: Load AI models during startup (0=lazy, 1=preload) [Default: 0]
- RUN_MIGRATIONS: Run Alembic migrations on startup (0=skip, 1=run) [Default: 0]
- API_ONLY: Run in API-only mode without web UI (0=full, 1=api-only) [Default: 0]
- LOG_LEVEL: Logging verbosity (DEBUG, INFO, WARNING, ERROR) [Default: INFO]
"""

# ============================================================================
# ENVIRONMENT SETUP - Must happen before heavy library imports
# ============================================================================
import os

# Ensure HuggingFace Hub won't attempt to create symlinks on Windows
# This prevents permission errors when downloading models
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

# ============================================================================
# CORE IMPORTS
# ============================================================================
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
from time import time
import asyncio
import importlib
import uuid
import contextvars
import json
import logging

# ============================================================================
# APPLICATION IMPORTS
# ============================================================================
import scripts.download_models as _download_models
from app.db import models, database
from app.core.config import settings

# Note: api_router and page_router are imported INSIDE lifespan()
# to avoid triggering heavy service imports too early during startup

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Context variable to track request IDs across async operations
REQUEST_ID = contextvars.ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    """Injects request_id into every log record for request tracing."""
    
    def filter(self, record):
        record.request_id = REQUEST_ID.get() or "-"
        return True


# Configure logging only once (avoid duplicate handlers)
if not logging.getLogger().hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-5s [%(request_id)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    
    root = logging.getLogger()
    # Set log level from settings (default to INFO if not specified)
    try:
        root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    except Exception:
        root.setLevel(logging.INFO)
    
    root.addHandler(handler)

# Reduce noise from verbose third-party libraries
for noisy_lib in ["urllib3", "watchfiles", "PIL", "rapidocr", "torch"]:
    logging.getLogger(noisy_lib).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

# Create database tables on startup (for development)
# In production, use Alembic migrations instead
models.Base.metadata.create_all(bind=database.engine)
logger.info("Database tables ensured via Base.metadata.create_all()")

# ============================================================================
# MIGRATION UTILITIES
# ============================================================================

def _run_migrations_if_possible():
    """
    Run Alembic database migrations to upgrade schema to latest version.
    
    This function is called during startup if RUN_MIGRATIONS=1 environment variable is set.
    By default, migrations are skipped to speed up startup time.
    
    Note: Requires alembic.ini file in project root.
    """
    try:
        # Import locally to avoid hard dependency
        from alembic import command
        from alembic.config import Config
        
        logger.info("Running Alembic migrations to upgrade schema...")
        cfg = Config("alembic.ini")
        # Ensure migration uses the same database URL as the app
        cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(cfg, "head")
        logger.info("Database migrations applied successfully (upgrade to head)")
    except Exception as e:
        # Non-fatal: migrations may already be applied or alembic not installed
        logger.warning("Skipping migrations due to error: %s", e)


# ============================================================================
# MODEL PRELOADING (OPTIONAL)
# ============================================================================

async def _preload_models_background(app: FastAPI):
    """
    Background task to prepare AI models and services without blocking startup.
    
    This function:
    1. Downloads required models (Kokoro TTS, Docling) if not present
    2. Imports and initializes all service modules
    3. Updates app.state.models_ready flag when complete
    
    Only runs if PRELOAD_MODELS=1 environment variable is set.
    By default (PRELOAD_MODELS=0), models load lazily on first request.
    """
    try:
        logger.info("🔄 Starting background AI model preparation...")
        
        # Run potentially blocking model downloads in worker thread
        await asyncio.to_thread(_download_models.check_and_download_models)

        # Import services to trigger model initialization
        def _import_services():
            importlib.import_module("app.services.tts_service")
            importlib.import_module("app.services.parser_service")
            importlib.import_module("app.services.summarizer_service")
            importlib.import_module("app.services.chat_service")

        await asyncio.to_thread(_import_services)
        
        # Mark models as ready
        app.state.models_ready = True
        logger.info("✅ AI models and services are ready")
    except Exception as e:
        app.state.models_ready = False
        logger.exception("❌ Failed to prepare AI models: %s", e)


# ============================================================================
# APPLICATION LIFESPAN (STARTUP/SHUTDOWN)
# ============================================================================
# ============================================================================
# APPLICATION LIFESPAN (STARTUP/SHUTDOWN)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    
    Startup sequence:
    1. Initialize database tables
    2. Optionally run migrations (RUN_MIGRATIONS=1)
    3. Import and register API/page routers
    4. Optionally preload AI models (PRELOAD_MODELS=1)
    5. Configure logging levels
    
    Shutdown sequence:
    - Clean up resources (if needed)
    """
    # ========== STARTUP ==========
    logger.info("=" * 70)
    logger.info("🚀 FastAPI Med Analyzer - Starting Up")
    logger.info("=" * 70)
    logger.info("📋 Configuration:")
    logger.info(f"   • Database: {settings.DATABASE_URL}")
    logger.info(f"   • Log Level: {settings.LOG_LEVEL}")
    logger.info(f"   • Debug Mode: {settings.DEBUG}")
    logger.info(f"   • API Only: {os.environ.get('API_ONLY', '0') == '1'}")
    logger.info(f"   • Preload Models: {os.environ.get('PRELOAD_MODELS', '0') == '1'}")
    logger.info(f"   • Run Migrations: {os.environ.get('RUN_MIGRATIONS', '0') == '1'}")
    
    # Initialize model readiness flag
    app.state.models_ready = False
    
    # Run database migrations if explicitly enabled
    run_migrations = os.environ.get("RUN_MIGRATIONS", "0")
    if run_migrations == "1":
        logger.info("🔄 Running database migrations...")
        try:
            await asyncio.to_thread(_run_migrations_if_possible)
            logger.info("✅ Database migrations complete")
        except Exception as e:
            logger.warning("⚠️  Migration failed: %s", e)
    else:
        logger.info("⏭️  Skipping migrations (use RUN_MIGRATIONS=1 to enable)")
    
    # Import routers after migrations to avoid premature service imports
    logger.info("📦 Loading API routers...")
    from app.api import api_router
    from app.pages import page_router
    
    # Register API routes
    app.include_router(api_router, prefix="/api/v1")
    if os.environ.get("API_ONLY", "0") != "1":
        app.include_router(page_router, tags=["Pages"])
    logger.info("✅ Routers registered successfully")
    
    # Optionally preload AI models in background
    preload = os.environ.get("PRELOAD_MODELS", "0")
    if preload == "1":
        try:
            asyncio.create_task(_preload_models_background(app))
            logger.info("🔄 AI model preload scheduled (non-blocking)")
        except Exception as e:
            logger.warning("⚠️  Could not schedule model preload: %s", e)
    else:
        logger.info("💤 Lazy loading enabled - models will load on first request")
    
    # Align third-party logger levels with app configuration
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    for lib_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "alembic", "sqlalchemy.engine"):
        logging.getLogger(lib_name).setLevel(level)
    
    logger.info("=" * 70)
    logger.info("✅ Application startup complete - Ready to accept requests")
    logger.info("=" * 70)
    
    # Yield control to uvicorn - app is now running
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("🛑 FastAPI shutting down...")


# ============================================================================
# FASTAPI APPLICATION INSTANCE
# ============================================================================

app = FastAPI(
    title="Med Analyzer API",
    description="Medical report processing and AI-powered chat interface",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/api/v1/health", include_in_schema=False)
def healthcheck():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        - service: Application name
        - ready: Whether AI models are loaded and ready
        - db: Database connectivity status
    """
    db_ok = True
    try:
        # Test database connection with simple query
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    
    return {
        "service": "med-analyzer",
        "ready": getattr(app.state, "models_ready", False),
        "db": db_ok,
    }


# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming HTTP requests with timing and status codes.
    
    Features:
    - Assigns unique request ID for tracing
    - Logs request method, path, status code, and response time
    - Catches and logs unhandled exceptions
    """
    # Generate unique request ID for this request
    req_id = str(uuid.uuid4())
    REQUEST_ID.set(req_id)
    
    logger.debug("→ Incoming: %s %s", request.method, request.url.path)
    start_time = time()
    
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("💥 Unhandled exception during request processing")
        raise
    
    elapsed = time() - start_time
    logger.info("%s %s → %s (%.3fs)", request.method, request.url.path, response.status_code, elapsed)
    return response


# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Provides:
    - Unique error ID for correlation with logs
    - Structured JSON error response
    - Full stack trace in server logs
    """
    error_id = str(uuid.uuid4())
    REQUEST_ID.set(error_id)
    
    logger.exception(
        "💥 Unhandled exception: %s %s | error_id=%s", 
        request.method, 
        request.url.path, 
        error_id
    )
    
    return Response(
        content=json.dumps({
            "detail": "Internal server error",
            "error_id": error_id
        }),
        status_code=500,
        media_type="application/json",
    )


# ============================================================================
# STATIC FILE SERVING (WEB UI)
# ============================================================================

API_ONLY = os.environ.get("API_ONLY", "0")

if API_ONLY != "1":
    # Serve static assets (CSS, JS) and media files (uploaded reports, audio)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/media", StaticFiles(directory="media"), name="media")
    logger.info("📁 Static and media file serving enabled")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

if API_ONLY != "1":
    @app.get("/", include_in_schema=False)
    def read_root():
        """Redirect root URL to the chat interface."""
        return RedirectResponse("/chat")
else:
    @app.get("/", include_in_schema=False)
    def read_root_api_only():
        """API-only mode root endpoint."""
        return {
            "service": "med-analyzer",
            "mode": "api-only",
            "docs": "/docs"
        }

