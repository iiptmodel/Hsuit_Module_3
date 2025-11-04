#!/usr/bin/env python3
"""
Script to download all required models for the services.
Models will be saved in the 'models' directory within the project root.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# This project is Ollama-first: MedGemma models are expected to be hosted by an
# Ollama server and accessed via the `ollama` client from the services.
# The previous Hugging Face transformer-based MedGemma download has been removed
# to keep the repo and runtime focused on Ollama. This script now prepares
# other required components (Docling, Kokoro) and provides a clear message.
USE_OLLAMA = True

def download_medgemma():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("MedGemma transformer download removed: using Ollama-only flow.")
    # No-op: MedGemma is expected to be served by an Ollama server.
    # If you want to run MedGemma locally without Ollama, reintroduce
    # a transformer-based loader here (not recommended for Ollama-only setup).
    return

def download_kokoro():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Downloading Kokoro models...")
    try:
        from kokoro import KPipeline
        # This will download models on initialization
        logger.info("Initializing Kokoro pipeline...")
        pipeline = KPipeline(lang_code='a')
        logger.info("Kokoro models downloaded successfully.")
    except Exception as e:
        logger.error(f"Error downloading Kokoro: {e}", exc_info=True)
        raise

def download_docling():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Checking Docling models...")
    try:
        from docling.document_converter import DocumentConverter
        # Docling might download models automatically, but let's initialize
        logger.info("Initializing Docling converter...")
        converter = DocumentConverter()
        logger.info("Docling models ready.")
    except Exception as e:
        logger.error(f"Error with Docling: {e}", exc_info=True)
        raise

def check_and_download_models():
    """Check if models are downloaded, if not, download them."""
    print("Preparing environment for Ollama-first deployment...")
    print("MedGemma is expected to be available via a local or remote Ollama server.")
    # Still ensure other auxiliary models/tools are initialized
    download_kokoro()
    download_docling()
    print("Environment preparation completed.")

if __name__ == "__main__":
    print("Starting model downloads...")
    # MedGemma transformer download removed; ensure Ollama is used.
    download_medgemma()
    download_kokoro()
    download_docling()
    print("All model downloads completed.")
