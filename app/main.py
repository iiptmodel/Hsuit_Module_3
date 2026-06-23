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
- REQUIRE_OLLAMA: Abort startup if Ollama/model is unavailable (1=enforce, 0=warn) [Default: 1]
- LOG_LEVEL: Logging verbosity (DEBUG, INFO, WARNING, ERROR) [Default: INFO]
"""

# ============================================================================
# ENVIRONMENT SETUP - Must happen before heavy library imports
# ============================================================================
import os

# Load .env into the process environment so os.environ-based flags below
# (RUN_MIGRATIONS, API_ONLY, PRELOAD_MODELS) and tokens (HF_TOKEN) are honored.
# pydantic-settings reads .env for the Settings model but does NOT populate
# os.environ, so this is needed for the flags read via os.environ.get(...).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

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
import json
import logging

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Configure centralized, colorized logging BEFORE the remaining app imports so
# that config validation and other import-time messages are formatted too.
from app.core.logging_config import setup_logging, REQUEST_ID

setup_logging()
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION IMPORTS
# ============================================================================
import scripts.download_models as _download_models
from app.db import models, database
from app.core.config import settings

# Re-apply the configured level now that settings (and thus .env) are loaded.
setup_logging(settings.LOG_LEVEL)

# Note: api_router and page_router are imported INSIDE lifespan()
# to avoid triggering heavy service imports too early during startup

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

# Verification outcomes returned by _verify_ollama_model().
OLLAMA_READY = "ready"              # server reachable and model available
OLLAMA_UNREACHABLE = "unreachable"  # Ollama server could not be contacted
OLLAMA_MODEL_FAILED = "model_failed"  # reachable but model missing and pull failed


def _model_matches(required: str, available: list) -> bool:
    """Tag-aware match: treat 'X', 'X:latest', and any 'X:<tag>' as equivalent.

    Ollama reports models with an explicit tag (e.g. 'name:latest'), while
    MODEL_NAME is usually given without one — a plain ``in`` check would miss it.
    """
    required_base = required.split(":", 1)[0]
    for name in available:
        if name == required or name.split(":", 1)[0] == required_base:
            return True
    return False


async def _verify_ollama_model() -> str:
    """Verify the Ollama server and the required model.

    Returns one of:
        OLLAMA_READY        - server reachable and model available (pulled if needed)
        OLLAMA_UNREACHABLE  - the Ollama server could not be contacted
        OLLAMA_MODEL_FAILED - reachable, but the model is missing and the pull failed
    """
    from app.services.ollama_client import is_ollama_reachable

    required_model = settings.MODEL_NAME

    # 1) Is the server reachable at all? Distinguishes "Ollama down" from
    #    "model missing" so the caller can give an accurate message.
    if not await asyncio.to_thread(is_ollama_reachable):
        return OLLAMA_UNREACHABLE

    try:
        import ollama

        logger.info(f"🔍 Checking for Ollama model: {required_model}")

        def _list_models():
            return [m.model for m in ollama.list().models]

        available = await asyncio.to_thread(_list_models)
        logger.info(f"📋 Available Ollama models: {available}")

        # 2) Already present (tag-aware) — use it.
        if _model_matches(required_model, available):
            logger.info(f"✅ Using Ollama model '{required_model}'")
            return OLLAMA_READY

        # 3) Missing — attempt to pull it.
        logger.warning(f"⚠️  Model '{required_model}' not present in Ollama")
        logger.info(f"📥 Pulling {required_model}... (this may take a while)")

        def _pull_model():
            try:
                ollama.pull(required_model)
                return True
            except Exception as e:
                logger.error(f"❌ Failed to pull model: {e}")
                return False

        if await asyncio.to_thread(_pull_model):
            logger.info(f"✅ Pulled Ollama model '{required_model}'")
            return OLLAMA_READY
        return OLLAMA_MODEL_FAILED

    except Exception as e:
        # Reachable a moment ago, but the API call failed.
        logger.error(f"❌ Error verifying Ollama model: {e}")
        return OLLAMA_MODEL_FAILED


async def _preload_models_background(app: FastAPI):
    """
    Background task to prepare AI models and services without blocking startup.
    
    This function:
    1. Verifies and downloads Ollama model if needed
    2. Downloads required models (Kokoro TTS, Docling) if not present
    3. Imports and initializes all service modules
    4. Updates app.state.models_ready flag when complete
    
    Only runs if PRELOAD_MODELS=1 environment variable is set.
    By default (PRELOAD_MODELS=0), models load lazily on first request.
    """
    try:
        logger.info("🔄 Starting background AI model preparation...")
        
        # Verify Ollama model first
        await _verify_ollama_model()
        
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
    
    # Always verify Ollama model on startup. The LLM path is Ollama-only, so a
    # missing/unreachable Ollama means summaries and chat can't work. By default
    # we fail fast and exit; set REQUIRE_OLLAMA=0 to warn and continue (useful
    # for tests, API-only deployments, or non-LLM development work).
    logger.info("🔍 Verifying Ollama model availability...")
    ollama_status = await _verify_ollama_model()
    if ollama_status != OLLAMA_READY:
        from app.services.ollama_client import _get_ollama_base_url

        if ollama_status == OLLAMA_UNREACHABLE:
            reason = (
                f"Ollama server is not reachable at {_get_ollama_base_url()}. "
                f"Start it with 'ollama serve' and restart this server."
            )
        else:  # OLLAMA_MODEL_FAILED
            reason = (
                f"Model '{settings.MODEL_NAME}' is unavailable and the automatic "
                f"pull failed. Run 'ollama pull {settings.MODEL_NAME}' and restart."
            )

        require_ollama = os.environ.get("REQUIRE_OLLAMA", "1") != "0"
        if require_ollama:
            logger.error("❌ %s", reason)
            logger.error("❌ Aborting startup (set REQUIRE_OLLAMA=0 to start anyway).")
            # Raising before yield makes uvicorn report startup failure and exit.
            raise RuntimeError(f"Ollama not ready: {reason}")
        logger.warning("⚠️  %s", reason)
        logger.warning("⚠️  REQUIRE_OLLAMA=0 — continuing without a working LLM.")

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

    # Ensure media directory exists before mounting
    if not os.path.exists("media"):
        os.makedirs("media")
        logger.info("📁 Created missing 'media' directory for file uploads")

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

