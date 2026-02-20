import logging
import os
import threading
import pyttsx3
import tempfile
from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-initialized TTS engines
_pyttsx3_engine = None
_pyttsx3_lock = threading.Lock()

def _get_pyttsx3_engine():
    """Get pyttsx3 engine for English (offline)"""
    global _pyttsx3_engine
    if _pyttsx3_engine is None:
        with _pyttsx3_lock:
            if _pyttsx3_engine is None:
                logger.info("Initializing pyttsx3 TTS engine (lazy)...")
                try:
                    _pyttsx3_engine = pyttsx3.init()
                    # Set voice properties
                    voices = _pyttsx3_engine.getProperty('voices')
                    if voices:
                        # Try to use a female voice if available
                        for voice in voices:
                            if 'female' in voice.name.lower():
                                _pyttsx3_engine.setProperty('voice', voice.id)
                                break
                    _pyttsx3_engine.setProperty('rate', 150)  # Speech rate
                    logger.info("pyttsx3 TTS engine initialized successfully.")
                except Exception as e:
                    logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}", exc_info=True)
                    _pyttsx3_engine = None
                    raise
    return _pyttsx3_engine


def is_pipeline_ready() -> bool:
    """Return True if any TTS engine is initialized and ready."""
    try:
        return _get_pyttsx3_engine() is not None
    except Exception:
        return False


def generate_speech(text: str, language: str, output_file_path: str):
    """
    Converts text to speech using pyttsx3 (offline, Windows native voices).
    """
    logger.info(f"Generating speech for text (length: {len(text)}) to {output_file_path}")

    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        # Validate text input
        if not text or not text.strip():
            raise ValueError("Text input is empty or invalid")

        # Generate speech using pyttsx3
        _generate_english_speech(text, output_file_path)

        logger.info(f"Audio file created successfully: {output_file_path}")

        # Verify file was created and has content
        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
            logger.info(f"Audio file verification passed: {os.path.getsize(output_file_path)} bytes")
        else:
            raise IOError("Audio file was not created or is empty")

    except Exception as e:
        logger.error(f"TTS failed: {e}", exc_info=True)
        # Fallback: create a dummy file with error info
        try:
            error_msg = f"Error generating audio: {str(e)}"
            with open(output_file_path + ".txt", "w", encoding='utf-8') as f:
                f.write(error_msg)
            logger.info(f"Created error fallback file: {output_file_path}.txt")
        except Exception as e2:
            logger.error(f"Failed to create fallback file: {e2}")
        raise


def _generate_english_speech(text: str, output_file_path: str):
    """Generate English speech using pyttsx3"""
    engine = _get_pyttsx3_engine()
    
    # Ensure .wav extension for pyttsx3
    if not output_file_path.endswith('.wav'):
        output_file_path = output_file_path.rsplit('.', 1)[0] + '.wav'
    
    # Use save_to_file with proper path
    engine.save_to_file(text, output_file_path)
    engine.runAndWait()
    
    # Wait a bit for the file to be written
    import time
    time.sleep(1)



def get_supported_languages():
    """Get list of supported languages with their display names"""
    return {
        'en': 'English'
    }


def get_default_language():
    """Get the default language"""
    return settings.DEFAULT_LANGUAGE
