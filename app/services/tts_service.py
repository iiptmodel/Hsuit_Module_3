import logging
import os
import threading
from kokoro import KPipeline
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

# Lazy-initialized Kokoro pipeline to avoid blocking import/startup.
_pipeline = None
_pipeline_lock = threading.Lock()

def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                logger.info("Initializing Kokoro TTS pipeline (lazy)...")
                try:
                    _pipeline = KPipeline(lang_code='a')  # American English
                    logger.info("Kokoro TTS pipeline initialized.")
                except Exception as e:
                    logger.error(f"Failed to initialize Kokoro TTS pipeline: {e}", exc_info=True)
                    _pipeline = None
                    raise
    return _pipeline


def is_pipeline_ready() -> bool:
    """Return True if the Kokoro pipeline is initialized and ready."""
    try:
        return _get_pipeline() is not None
    except Exception:
        return False


def generate_speech(text: str, language: str, output_file_path: str):
    """
    Converts text to speech using Kokoro and saves it to a file.
    """
    logger.info(f"Generating speech for text (length: {len(text)}, language: {language}) to {output_file_path}")

    try:
        pipeline = _get_pipeline()

        # Kokoro supports English, so assume language is 'en' or handle accordingly
        if language.lower() != 'en':
            logger.warning(f"Kokoro only supports English, but language is {language}. Proceeding with English.")

        # Validate text input
        if not text or not text.strip():
            raise ValueError("Text input is empty or invalid")

        logger.info("Starting TTS generation with Kokoro (streaming write)...")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        # Open a soundfile for streaming write (WAV PCM 16)
        samplerate = 24000

        # Use the pipeline generator and write chunks directly to file to avoid large memory use
        generator = pipeline(
            text, voice='af_heart',  # American Female Heart voice
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
