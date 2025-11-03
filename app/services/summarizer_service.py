import logging
import os
import ollama
from app.services import parser_service

logger = logging.getLogger(__name__)

# Use local Ollama model for summarization rather than loading heavy transformers
# This keeps the service lightweight and delegates model serving to Ollama.

def _guardrail_validator(text: str) -> str:
    # Basic guardrail checks to avoid diagnoses, prescriptions, or casual chat
    prohibited = ['diagnos', 'prescrib', 'you have', 'take ', 'lol', 'omg']
    for p in prohibited:
        if p in text.lower():
            logger.warning(f"Guardrail triggered for pattern: {p}")
            return (
                "I can help explain findings and what they might indicate, but I cannot provide a definitive diagnosis or prescribe medications. "
                "Please consult a healthcare professional for diagnosis and treatment." 
            )
    return text


def generate_summary_from_text(text: str, language: str) -> str:
    """Generate a concise summary using Ollama chat model."""
    logger.info(f"Generating summary via Ollama (text length={len(text)})")
    try:
        system_prompt = (
            "You are a concise, professional medical assistant. Summarize the following extracted text from a medical report in "
            f"{language}. Do not diagnose or prescribe. Keep it clear and patient-friendly."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        resp = ollama.chat(
            model='alibayram/medgemma:4b',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 200}
        )
        summary = resp.get('message', {}).get('content', '')
        return _guardrail_validator(summary)
    except Exception as e:
        logger.error(f"Ollama summarization failed: {e}", exc_info=True)
        # Fallback: return short snippet
        return (text.strip().replace('\n', ' ')[:500] + '...')


def generate_summary_from_image(image_path: str, language: str) -> str:
    """Extract text from the image and summarize using Ollama."""
    logger.info(f"Generating image summary via parser+Ollama for {image_path}")
    try:
        extracted = parser_service.extract_data_from_file(image_path)
        if extracted.startswith('Error:'):
            return extracted
        return generate_summary_from_text(extracted, language)
    except Exception as e:
        logger.error(f"Image summarization failed: {e}", exc_info=True)
        return f"Error: Could not summarize image. {str(e)}"
