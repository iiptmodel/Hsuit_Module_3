# app/services/summarizer_service.py
import logging
import re
import os
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch

# Set cache directory to project root/models
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Set Hugging Face cache to project models directory
os.environ["HF_HOME"] = MODELS_DIR
os.environ["TRANSFORMERS_CACHE"] = os.path.join(MODELS_DIR, "transformers")
os.environ["HF_HUB_CACHE"] = os.path.join(MODELS_DIR, "hub")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

logger = logging.getLogger(__name__)

# Load MedGemma model once when the module is imported
MODEL_ID = "unsloth/medgemma-4b-it"
logger.info(f"Loading MedGemma model: {MODEL_ID}")
logger.info(f"Models directory: {MODELS_DIR}")
try:
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_ID,
        dtype=torch.bfloat16,
        device_map="auto",
        cache_dir=MODELS_DIR,
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID, use_fast=True, cache_dir=MODELS_DIR)
    logger.info("MedGemma VLM model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load MedGemma model: {e}", exc_info=True)
    raise

def guardrail_validator(text: str) -> str:
    """
    Validates the generated summary against guardrails.
    - No jokes or humor
    - Professional tone
    - No medical or mental health diagnoses
    - Only factual summary and explanation
    """
    logger.info("Validating summary against guardrails...")

    # Check for prohibited patterns
    prohibited_patterns = [
        r'\bjoke\b', r'\bhumor\b', r'\bfunny\b', r'\blaugh\b',
        r'\bdiagnos', r'\bmental health\b', r'\bpsychiatric\b',
        r'\bI recommend\b', r'\bYou should\b', r'\bconsult\b', r'\bsee a doctor\b'
    ]

    for pattern in prohibited_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Guardrail violation detected in summary: {pattern}")
            return "Summary generation failed due to content policy violation. Please ensure input is appropriate medical report content."

    # Ensure professional tone (basic check for excessive punctuation or informal language)
    if '!' in text or '?' in text or re.search(r'\b(lol|omg|wtf)\b', text, re.IGNORECASE):
        logger.warning("Guardrail violation: Unprofessional tone detected")
        return "Summary generation failed due to content policy violation. Please ensure input is appropriate medical report content."

    logger.info("Guardrail validation passed.")
    return text

def generate_summary_from_text(text: str, language: str) -> str:
    """
    Generates a summary from text results using MedGemma with strict guardrails.
    """
    logger.info(f"Generating summary from text (length: {len(text)}, language: {language})")
    try:
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": f"You are an expert medical assistant. Provide a clear, professional summary of the medical report in {language}. Do not make jokes, provide any diagnoses, give medical advice, or discuss mental health. Only summarize and explain the factual content of the report."}]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text}
                ]
            }
        ]

        logger.info("Tokenizing input for MedGemma...")
        inputs = processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt", use_fast=True
        ).to(model.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]
        logger.info(f"Input tokenized, length: {input_len}")

        logger.info("Generating summary with MedGemma...")
        with torch.inference_mode():
            generation = model.generate(**inputs, max_new_tokens=200, do_sample=False)
            generation = generation[0][input_len:]

        decoded = processor.decode(generation, skip_special_tokens=True)
        logger.info(f"Raw summary generated: {decoded}")

        # Apply guardrail validation
        validated_summary = guardrail_validator(decoded)
        logger.info("Summary generation completed successfully.")
        return validated_summary
    except Exception as e:
        logger.error(f"MedGemma text summarization failed: {e}", exc_info=True)
        return f"Error: Could not summarize text. {str(e)}"

def generate_summary_from_image(image_path: str, language: str) -> str:
    """
    Generates a summary directly from a report IMAGE using MedGemma with strict guardrails.
    """
    logger.info(f"Generating summary from image: {image_path}, language: {language}")
    try:
        logger.info("Opening image file...")
        image = Image.open(image_path)
        logger.info(f"Image opened successfully: {image.format} {image.size}")

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": f"You are an expert radiologist. Provide a clear, professional description of this medical image in {language}. Do not make jokes, provide any diagnoses, give medical advice, or discuss mental health. Only describe and explain the factual content visible in the image."}]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this medical image"},
                    {"type": "image", "image": image}
                ]
            }
        ]

        logger.info("Tokenizing input for MedGemma...")
        inputs = processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt", use_fast=True
        ).to(model.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]
        logger.info(f"Input tokenized, length: {input_len}")

        logger.info("Generating summary with MedGemma...")
        with torch.inference_mode():
            generation = model.generate(**inputs, max_new_tokens=200, do_sample=False)
            generation = generation[0][input_len:]

        decoded = processor.decode(generation, skip_special_tokens=True)
        logger.info(f"Raw summary generated: {decoded}")

        # Apply guardrail validation
        validated_summary = guardrail_validator(decoded)
        logger.info("Image summary generation completed successfully.")
        return validated_summary
    except Exception as e:
        logger.error(f"MedGemma image summarization failed: {e}", exc_info=True)
        return f"Error: Could not summarize image. {str(e)}"
