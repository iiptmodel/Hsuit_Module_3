import logging
import os
from kokoro import KPipeline
import soundfile as sf

logger = logging.getLogger(__name__)

logger.info("Loading Kokoro TTS model...")
try:
    pipeline = KPipeline(lang_code='a')  # American English
    logger.info("Kokoro TTS model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Kokoro TTS model: {e}", exc_info=True)
    raise

def generate_speech(text: str, language: str, output_file_path: str):
    """
    Converts text to speech using Kokoro and saves it to a file.
    """
    logger.info(f"Generating speech for text (length: {len(text)}, language: {language}) to {output_file_path}")

    try:
        # Kokoro supports English, so assume language is 'en' or handle accordingly
        if language.lower() != 'en':
            logger.warning(f"Kokoro only supports English, but language is {language}. Proceeding with English.")

        # Validate text input
        if not text or not text.strip():
            raise ValueError("Text input is empty or invalid")

        logger.info("Starting TTS generation with Kokoro...")
        # Generate audio
        generator = pipeline(
            text, voice='af_heart',  # American Female Heart voice
            speed=1, split_pattern=r'\n+'
        )

        # Collect audio data
        audio_data = []
        chunk_count = 0
        for i, (gs, ps, audio) in enumerate(generator):
            audio_data.extend(audio)
            chunk_count += 1
            logger.debug(f"Processed chunk {i+1}: {len(audio)} samples")

        if not audio_data:
            raise ValueError("No audio data generated")

        logger.info(f"Audio generation completed. Total chunks: {chunk_count}, Total samples: {len(audio_data)}")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        # Save to file
        sf.write(output_file_path, audio_data, 24000)  # Kokoro uses 24kHz
        logger.info(f"TTS audio saved successfully to {output_file_path}")

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
            with open(output_file_path + ".txt", "w") as f:
                f.write(error_msg)
            logger.info(f"Created error fallback file: {output_file_path}.txt")
        except Exception as e2:
            logger.error(f"Failed to create fallback file: {e2}")
        raise  # Re-raise to let caller handle it
