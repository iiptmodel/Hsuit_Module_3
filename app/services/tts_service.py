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
    Supports English and Hindi; falls back to English for unsupported languages.
    """
    logger.info(f"Generating speech for text (length: {len(text)}, language: {language}) to {output_file_path}")

    lang_key = language.lower()
    if lang_key not in _LANG_CONFIG:
        logger.warning(f"Language '{language}' not supported by Kokoro TTS; falling back to English.")
        lang_key = 'english'

    lang_code, voice = _LANG_CONFIG[lang_key]

    try:
        pipeline = _get_pipeline(lang_code)

        # Validate text input
        if not text or not text.strip():
            raise ValueError("Text input is empty or invalid")

        logger.info(f"Starting TTS generation with Kokoro (lang={lang_code}, voice={voice}, streaming write)...")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        # Open a soundfile for streaming write (WAV PCM 16)
        samplerate = 24000

        # Use the pipeline generator and write chunks directly to file to avoid large memory use
        generator = pipeline(
            text, voice=voice,
            speed=1, split_pattern=r'\n+'
        )

        with sf.SoundFile(output_file_path, mode='w', samplerate=samplerate, channels=1, subtype='PCM_16') as sf_file:
            chunk_count = 0
            total_frames = 0
            for i, (gs, ps, audio) in enumerate(generator):
                # audio may be list or numpy array
                arr = np.asarray(audio)
                # If audio is multi-channel, collapse or handle accordingly
                if arr.ndim > 1 and arr.shape[1] > 1:
                    # If multi-channel, take first channel
                    arr = arr[:, 0]
                # Ensure float32 -> int16 conversion handled by soundfile
                sf_file.write(arr)
                frames = arr.shape[0]
                total_frames += frames
                chunk_count += 1
                logger.debug(f"Processed chunk {i+1}: {frames} frames")

        logger.info(f"Audio generation completed. Total chunks: {chunk_count}, Total frames: {total_frames}")

        # Verify file was created and has content
        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
            logger.info(f"Audio file verification passed: {os.path.getsize(output_file_path)} bytes")
        else:
            raise IOError("Audio file was not created or is empty")

    except Exception as e:
        logger.error(f"Kokoro TTS failed: {e}", exc_info=True)
        # Fallback: create a dummy file with error info
        try:
            error_msg = f"Error generating audio: {str(e)}"
            with open(output_file_path + ".txt", "w", encoding='utf-8') as f:
                f.write(error_msg)
            logger.info(f"Created error fallback file: {output_file_path}.txt")
        except Exception as e2:
            logger.error(f"Failed to create fallback file: {e2}")
        raise  # Re-raise to let caller handle it
