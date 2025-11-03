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
            model='amsaravi/medgemma-4b-it:q8',
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
    """
    Analyze medical image directly using MedGemma VLM (Vision-Language Model).
    MedGemma can process images directly without needing text extraction.
    """
    logger.info(f"Analyzing medical image directly with MedGemma VLM: {image_path}")
    try:
        system_prompt = (
            "You are a medical assistant specialized in analyzing medical images. "
            "Describe what you see in this medical image in clear, professional language. "
            f"Provide your response in {language}. "
            "Do NOT diagnose or prescribe. Focus on describing visible findings and what they typically indicate. "
            "Always recommend consulting with a healthcare professional for proper diagnosis."
        )

        # Use Ollama's vision capability to analyze the image directly
        messages = [
            {
                "role": "user",
                "content": "Analyze this medical image and describe the findings. What can you see?",
                "images": [image_path]  # Pass image directly to the model
            }
        ]

        resp = ollama.chat(
            model='amsaravi/medgemma-4b-it:q8',  # Use local MedGemma vision-enabled model
            messages=messages,
            options={
                "temperature": 0.3,  # Lower temperature for more focused medical analysis
                "num_predict": 300
            }
        )
        
        analysis = resp.get('message', {}).get('content', '')
        logger.info(f"MedGemma VLM analysis completed: {analysis[:100]}...")
        
        # Apply guardrails to the response
        return _guardrail_validator(analysis)
        
    except Exception as e:
        logger.error(f"MedGemma VLM analysis failed: {e}", exc_info=True)
        # Fallback to text extraction if VLM fails
        logger.info("Falling back to text extraction method")
        try:
            extracted = parser_service.extract_data_from_file(image_path)
            if extracted.startswith('Error:'):
                return extracted
            return generate_summary_from_text(extracted, language)
        except Exception as fallback_error:
            logger.error(f"Fallback text extraction also failed: {fallback_error}")
            return f"Error: Could not analyze image. {str(e)}"
