#!/usr/bin/env python3
"""
AI Model Download and Initialization Script

This script prepares the application environment by downloading and initializing
required AI models for:
- Kokoro TTS (Text-to-Speech)
- Docling (Document parsing and OCR)

Note: MedGemma LLM is expected to be hosted via Ollama server.
      This script does NOT download transformer-based models.

Usage:
    python scripts/download_models.py  # Download all models
    
Environment:
    Called automatically during app startup if PRELOAD_MODELS=1
"""

import os
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# This project uses Ollama for LLM inference
# MedGemma models are expected to be available via Ollama server
USE_OLLAMA = True

logger = logging.getLogger(__name__)


# ============================================================================
# MODEL DOWNLOAD FUNCTIONS
# ============================================================================

def download_medgemma():
    """
    MedGemma download placeholder.
    
    NOTE: This project uses Ollama-first deployment.
    MedGemma models should be pulled via Ollama:
        ollama pull medgemma
    
    No transformer-based download is performed here.
    """
    logger.info("MedGemma: Using Ollama server (no local model download)")
    logger.info("Ensure MedGemma is available via: ollama pull <model-name>")


def download_kokoro():
    """
    Download and initialize Kokoro TTS models.
    
    Kokoro is used for multilingual text-to-speech conversion.
    Models are automatically downloaded on first initialization.
    """
    logger.info("📥 Initializing Kokoro TTS pipeline...")
    try:
        from kokoro import KPipeline
        
        # Initialize pipeline - this will download models if not present
        pipeline = KPipeline(lang_code='a')  # 'a' = auto-detect language
        
        logger.info("✅ Kokoro TTS models ready")
    except Exception as e:
        logger.error(f"❌ Failed to download Kokoro models: {e}", exc_info=True)
        raise


def download_docling():
    """
    Initialize Docling document converter.
    
    Docling is used for:
    - PDF parsing and text extraction
    - OCR (Optical Character Recognition)
    - Document structure analysis
    
    Models are downloaded automatically on first use.
    """
    logger.info("📥 Initializing Docling document converter...")
    try:
        from docling.document_converter import DocumentConverter
        
        # Initialize converter - models download automatically
        converter = DocumentConverter()
        
        logger.info("✅ Docling models ready")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Docling: {e}", exc_info=True)
        raise


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def check_and_download_models():
    """
    Main entry point for model preparation.
    
    This function is called during application startup (if PRELOAD_MODELS=1)
    or when running this script directly.
    """
    print("=" * 70)
    print("🔧 Preparing Med Analyzer Environment")
    print("=" * 70)
    print("📋 Model Configuration:")
    print("   • LLM: Ollama-hosted (MedGemma)")
    print("   • TTS: Kokoro (auto-download)")
    print("   • Document Parser: Docling (auto-download)")
    print("=" * 70)
    
    # Initialize auxiliary models (Kokoro, Docling)
    download_kokoro()
    download_docling()
    
    print("=" * 70)
    print("✅ Environment preparation complete")
    print("=" * 70)


# ============================================================================
# COMMAND-LINE EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting model downloads...\n")
    
    # Note: download_medgemma is a no-op (Ollama-only)
    download_medgemma()
    download_kokoro()
    download_docling()
    
    print("\n✅ All model downloads completed.")

