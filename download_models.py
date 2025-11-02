#!/usr/bin/env python3
"""
Script to download all required models for the services.
Models will be saved in the 'models' directory within the project root.
"""

import os
import sys
import torch

# Set cache directory to project root/models
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

if os.environ.get("FORCE_PROJECT_MODELS") == "1":
    os.environ.setdefault("HF_HOME", MODELS_DIR)
    os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(MODELS_DIR, "transformers"))
    os.environ.setdefault("HF_HUB_CACHE", os.path.join(MODELS_DIR, "hub"))
    print(f"Models will be saved to: {MODELS_DIR} (FORCE_PROJECT_MODELS=1)")
else:
    # Do not modify HF_HOME. Use the existing HF cache (typically under
    # %USERPROFILE%\.cache\huggingface on Windows). Inform the user where
    # the models will be written if they haven't already configured HF_HOME.
    effective = os.environ.get("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))
    print(f"Models will be saved to: {effective} (system HF cache). To force project-local caching set FORCE_PROJECT_MODELS=1")

print(f"Models will be saved to: {MODELS_DIR}")

def download_medgemma():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Downloading MedGemma model...")
    try:
        from transformers import AutoModelForImageTextToText, AutoProcessor
        model_name = "unsloth/medgemma-4b-it"
        logger.info(f"Loading model: {model_name}")
        model = AutoModelForImageTextToText.from_pretrained(model_name, dtype=torch.bfloat16, device_map="auto")
        processor = AutoProcessor.from_pretrained(model_name, use_fast=True)
        logger.info("MedGemma model downloaded successfully.")
    except Exception as e:
        logger.error(f"Error downloading MedGemma: {e}", exc_info=True)
        raise

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
    print("Checking and downloading models if needed...")
    download_medgemma()
    download_kokoro()
    download_docling()
    print("All models checked/downloaded.")

if __name__ == "__main__":
    print("Starting model downloads...")
    download_medgemma()
    download_kokoro()
    download_docling()
    print("All model downloads completed.")
