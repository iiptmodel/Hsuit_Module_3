import logging
import os
import threading
from kokoro import KPipeline
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

# Per-language Kokoro pipeline cache to avoid reinitializing on every call.
_pipelines: dict = {}
_pipeline_lock = threading.Lock()

# Kokoro lang_code and default voice per language name
_LANG_CONFIG = {
    'english': ('a', 'af_heart'),
    'hindi':   ('h', 'hf_alpha'),
}

def _get_pipeline(lang_code: str) -> KPipeline:
    if lang_code not in _pipelines:
        with _pipeline_lock:
            if lang_code not in _pipelines:
                logger.info(f"Initializing Kokoro TTS pipeline for lang_code='{lang_code}' (lazy)...")
                try:
                    _pipelines[lang_code] = KPipeline(lang_code=lang_code)
                    logger.info(f"Kokoro TTS pipeline initialized for lang_code='{lang_code}'.")
                except Exception as e:
                    logger.error(f"Failed to initialize Kokoro TTS pipeline for lang_code='{lang_code}': {e}", exc_info=True)
                    raise
    return _pipelines[lang_code]


def is_pipeline_ready() -> bool:
    """Return True if at least the default English pipeline can initialize."""
    try:
        return _get_pipeline('a') is not None
    except Exception:
        return False


def generate_speech(text: str, language: str, output_file_path: str):
    """
    Converts text to speech using Kokoro and saves it to a file.
    Supports English and Hindi; falls back to English for unsupported languages
    or if the target pipeline fails to initialize.
    """
    logger.info(f"Generating speech (length={len(text)}, language={language}) -> {output_file_path}")

    lang_key = language.lower()
    if lang_key not in _LANG_CONFIG:
        logger.warning(f"Language '{language}' not in TTS config; falling back to English.")
        lang_key = 'english'

    lang_code, voice = _LANG_CONFIG[lang_key]

    # Try target language; fall back to English if pipeline unavailable
    try:
        pipeline = _get_pipeline(lang_code)
    except Exception as e:
        logger.warning(f"TTS pipeline for '{language}' (lang_code={lang_code}) unavailable: {e}. Falling back to English.")
        lang_code, voice = _LANG_CONFIG['english']
        pipeline = _get_pipeline(lang_code)

    if not text or not text.strip():
        raise ValueError("Text input is empty or invalid")

    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    samplerate = 24000
    generator = pipeline(text, voice=voice, speed=1, split_pattern=r'\n+')

    with sf.SoundFile(output_file_path, mode='w', samplerate=samplerate, channels=1, subtype='PCM_16') as sf_file:
        total_frames = 0
        for i, (gs, ps, audio) in enumerate(generator):
            arr = np.asarray(audio)
            if arr.ndim > 1 and arr.shape[1] > 1:
                arr = arr[:, 0]
            sf_file.write(arr)
            total_frames += arr.shape[0]
            logger.debug(f"TTS chunk {i+1}: {arr.shape[0]} frames")

    if not (os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0):
        raise IOError("Audio file was not created or is empty")

    logger.info(f"TTS complete: {os.path.getsize(output_file_path)} bytes at {output_file_path}")
