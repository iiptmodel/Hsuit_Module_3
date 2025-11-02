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

from app.db import models, database
from app.api import api_router
from app.pages import page_router

import logging
from time import time
from fastapi.responses import PlainTextResponse

# Configure logging only once
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

logger = logging.getLogger(__name__)

# Create database tables (for dev only)
models.Base.metadata.create_all(bind=database.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI starting...")
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
    logger.exception("Unhandled exception during request: %s %s", request.method, request.url.path)
    return PlainTextResponse("Internal server error", status_code=500)

# Mount static & media
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(page_router, tags=["Pages"])


@app.get("/", include_in_schema=False)
def read_root():
    """Redirects root to the chat interface."""
    return RedirectResponse("/chat")
