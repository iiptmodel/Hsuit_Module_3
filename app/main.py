"""
Sets environment fallbacks for Windows/HF hub compatibility before
importing heavy libraries that may use the HuggingFace hub.
"""
import os

# Ensure HF hub will not attempt to create symlinks on Windows
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import asyncio
import importlib
import uuid
import contextvars
import json
from fastapi import Response
import logging

# Context variable for request id
REQUEST_ID = contextvars.ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = REQUEST_ID.get() or "-"
        return True

# Optionally preload models on startup when PRELOAD_MODELS=1
import download_models as _download_models

from app.db import models, database
from app.api import api_router
from app.pages import page_router

import logging
from time import time
from fastapi.responses import PlainTextResponse

# Configure logging only once with request id support
if not logging.getLogger().hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)-5s [%(request_id)s] [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

logger = logging.getLogger(__name__)

# Create database tables (for dev only)
models.Base.metadata.create_all(bind=database.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI starting...")
    # If PRELOAD_MODELS is set to '1' (or environment variable not set and we choose to preload),
    # run model downloads and import heavy service modules so models initialize before accepting requests.
    preload = os.environ.get("PRELOAD_MODELS", "1")
    if preload == "1":
        logger.info("Preloading AI models and services before accepting requests...")
        try:
            # Run the potentially blocking downloads in a thread to avoid blocking the event loop
            await asyncio.to_thread(_download_models.check_and_download_models)

            # Import service modules which perform model initialization at import time
            def _import_services():
                importlib.import_module("app.services.tts_service")
                importlib.import_module("app.services.parser_service")
                importlib.import_module("app.services.summarizer_service")
                importlib.import_module("app.services.chat_service")

            await asyncio.to_thread(_import_services)
            logger.info("AI models and services preloaded successfully.")
        except Exception as e:
            logger.exception("Failed to preload AI models: %s", e)
            # Continue startup but warn that some endpoints may fail until models are available
    else:
        logger.info("AI services will be loaded lazily on first request.")
    yield
    logger.info("FastAPI shutting down...")


app = FastAPI(
    title="FastAPI Med Analyzer",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and their response status/time."""
    # Assign a request id for tracing
    req_id = str(uuid.uuid4())
    REQUEST_ID.set(req_id)
    logger.debug("Start request: %s %s", request.method, request.url.path)
    start_time = time()
    try:
        response = await call_next(request)
    except Exception as exc:
        # Log full stack trace then re-raise for FastAPI to handle
        logger.exception("Unhandled exception while processing request %s %s", request.method, request.url.path)
        raise
    elapsed = time() - start_time
    logger.info("%s %s -> %s (%.3fs)", request.method, request.url.path, response.status_code, elapsed)
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Generate an error id to correlate logs and client
    error_id = str(uuid.uuid4())
    REQUEST_ID.set(error_id)
    logger.exception("Unhandled exception during request: %s %s | error_id=%s", request.method, request.url.path, error_id)
    # Return structured JSON error for easier debugging on client side
    return Response(
        content=json.dumps({"detail": "Internal server error", "error_id": error_id}),
        status_code=500,
        media_type="application/json",
    )

# Mount static & media
API_ONLY = os.environ.get("API_ONLY", "0")

# If running in API-only mode (API_ONLY=1), don't serve the web UI/static pages.
if API_ONLY != "1":
    # Mount static & media for web UI
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/media", StaticFiles(directory="media"), name="media")

# Routers (always include API router)
app.include_router(api_router, prefix="/api/v1")

# Include page router only when not running API-only mode
if API_ONLY != "1":
    app.include_router(page_router, tags=["Pages"])


if API_ONLY != "1":
    @app.get("/", include_in_schema=False)
    def read_root():
        """Redirects root to the chat interface."""
        return RedirectResponse("/chat")
else:
    # In API-only deployments we keep root returning a small JSON health/info object
    @app.get("/", include_in_schema=False)
    def read_root_api_only():
        return {"service": "med-analyzer", "mode": "api-only"}
