#!/usr/bin/env python3
"""
AI Model Download and Initialization Script

Prepares the application environment by downloading and initializing the
auxiliary AI models used by the app:
- Kokoro TTS (text-to-speech)
- Docling (document parsing and OCR)

Note: the MedGemma LLM is served via an Ollama server and is NOT downloaded
here — it is pulled with ``ollama pull <model-name>`` and verified by the app
on startup.

Usage:
    python scripts/download_models.py   # download/initialize all aux models

Environment:
    Also invoked from app startup (in a worker thread) when PRELOAD_MODELS=1.
"""

import os
import sys

# ============================================================================
# PATH SETUP — make the project root importable when run directly
# ============================================================================
# When launched as ``python scripts/download_models.py`` the interpreter only
# puts the ``scripts/`` directory on sys.path, so ``import app.*`` would fail.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import logging

from app.core.logging_config import setup_logging, banner

# ============================================================================
# CONFIGURATION
# ============================================================================

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# This project uses Ollama for LLM inference; MedGemma is provided by Ollama.
USE_OLLAMA = True

logger = logging.getLogger("download_models")


# ============================================================================
# MODEL DOWNLOAD FUNCTIONS
# ============================================================================

def download_medgemma():
    """No-op: MedGemma is served via Ollama, not downloaded locally."""
    logger.info("MedGemma : served via Ollama — no local download")
    logger.info("           pull it once with: ollama pull <model-name>")


def download_kokoro():
    """Initialize Kokoro TTS, downloading its weights on first run."""
    logger.info("Kokoro   : initializing TTS pipeline (downloads on first run)...")
    try:
        from kokoro import KPipeline

        # Initializing the pipeline triggers the model download if not cached.
        KPipeline(lang_code="a")  # 'a' = auto-detect language
        logger.info("Kokoro   : ready ✓")
    except Exception as e:
        logger.error("Kokoro   : download failed — %s", e, exc_info=True)
        raise


def download_docling():
    """Initialize the Docling converter, downloading its models on first run."""
    logger.info("Docling  : initializing document converter (downloads on first run)...")
    try:
        from docling.document_converter import DocumentConverter

        DocumentConverter()  # models download automatically
        logger.info("Docling  : ready ✓")
    except Exception as e:
        logger.error("Docling  : initialization failed — %s", e, exc_info=True)
        raise


# ============================================================================
# MAIN ENTRY POINTS
# ============================================================================

def check_and_download_models():
    """Prepare auxiliary models (Kokoro, Docling).

    Called from app startup (PRELOAD_MODELS=1). ``setup_logging`` is idempotent,
    so this is a no-op when the app has already configured logging.
    """
    setup_logging()
    banner(logger, "Preparing Med Analyzer models")
    logger.info("LLM      : Ollama-hosted (MedGemma) — verified at app startup")
    logger.info("TTS      : Kokoro (auto-download)")
    logger.info("Parser   : Docling (auto-download)")
    download_kokoro()
    download_docling()
    logger.info("Environment preparation complete ✓")


if __name__ == "__main__":
    setup_logging()
    banner(logger, "Starting model downloads")
    download_medgemma()
    download_kokoro()
    download_docling()
    logger.info("All downloads completed ✓")
