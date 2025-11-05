import logging
import os
import ollama
from typing import List, Dict
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
            # Instead of replacing the entire output with a canned disclaimer (which can be
            # overly conservative), append a short disclaimer while preserving the model's
            # analysis. This loosens the guardrail but keeps an explicit safety notice.
            disclaimer = (
                "\n\n[Disclaimer] I can help explain findings and what they might indicate, but I cannot provide a definitive diagnosis or prescribe medications. "
                "Please consult a qualified healthcare professional for diagnosis and treatment."
            )
            # If the model output already contains the disclaimer text, avoid duplicating it.
            if 'consult a' in text.lower() or 'i cannot provide a definitive diagnosis' in text.lower():
                return text
            return text + disclaimer
    return text


def generate_summary_from_text(text: str, language: str = 'English') -> str:
    """Generate a concise summary using Ollama chat model."""
    logger.info(f"Generating summary via Ollama (text length={len(text)})")
    try:
        system_prompt = (
            "You are a concise, professional medical assistant. Summarize the following extracted text from a medical report in "
            f"{language}. Do not diagnose or prescribe. Keep it clear and patient-friendly. Aim for 2-4 short sentences suitable for a patient."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model='amsaravi/medgemma-4b-it:q8',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 200}
        )
        summary = resp.get('message', {}).get('content', '')
        return _guardrail_validator(summary)
    except Exception as e:
        logger.error(f"Ollama summarization failed: {e}", exc_info=True)
        # Fallback: return short snippet
        return (text.strip().replace('\n', ' ')[:300] + '...')


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

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
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


def generate_patient_summary_from_text(text: str, language: str = 'English') -> str:
    """
    Generate a very short, patient-facing summary (1-2 sentences) with simple actionable advice.
    This is suitable for patients who want a quick understanding and next-step suggestion.
    """
    logger.info(f"Generating patient-summary via Ollama (text length={len(text)})")
    try:
        system_prompt = (
            "You are a medical assistant writing for patients. Given the extracted text from a medical report, "
            f"produce a VERY SHORT (1-2 sentences) plain-language summary in {language}. "
            "Include one short actionable recommendation (e.g., lifestyle change) and a line to consult a doctor for treatment. "
            "Never diagnose or recommend specific medications."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model='amsaravi/medgemma-4b-it:q8',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 120}
        )

        summary = resp.get('message', {}).get('content', '')
        return _guardrail_validator(summary.strip())
    except Exception as e:
        logger.error(f"Patient summary generation failed: {e}", exc_info=True)
        return generate_summary_from_text(text, language)


def generate_detailed_report_from_text(text: str, language: str = 'English') -> str:
    """
    Generate a structured, detailed medical report from extracted text aimed at clinicians.

    The output should include:
      - Report Summary (brief)
      - Key Results (bullet list with numeric values and reference ranges where present)
      - What This Means (interpretation)
      - Confidence/Notes (if available, note any uncertainties)
      - Next Steps (recommended follow-up/testing)
      - General Education

    This prompt asks the model for extra technical detail and to include raw values when present.
    """
    logger.info(f"Generating detailed report via Ollama (text length={len(text)})")
    try:
        system_prompt = (
            "You are a professional medical report assistant writing for clinicians. When given the extracted text "
            "from a medical report, produce a structured report including: Report Summary, Key Results (include raw values and reference ranges when present), "
            "What This Means, Confidence/Notes (mention any uncertainties or low-quality data), Next Steps, and General Education. "
            "Use clinical language but avoid definitive diagnoses. Provide clear bullet points for Key Results."
            f" Provide the response in {language}."
        )

        user_prompt = (
            "Below is the extracted text from a medical document. Create the structured clinician-facing report as requested.\n\n"
            "---BEGIN EXTRACTED TEXT---\n" + text + "\n---END EXTRACTED TEXT---"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model='amsaravi/medgemma-4b-it:q8',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 600}
        )

        report = resp.get('message', {}).get('content', '')
        # For clinician view, still apply guardrails but allow more technical detail
        return _guardrail_validator(report)

    except Exception as e:
        logger.error(f"Detailed report generation failed: {e}", exc_info=True)
        # Fallback to general summary
        return generate_summary_from_text(text, language)


def summarize_chat_context(conversation_history: List[Dict[str, str]], language: str = 'English') -> str:
    """
    Summarize chat conversation history for context management.

    Takes a list of conversation messages and creates a concise summary
    that captures the key medical discussion points, questions asked,
    and important findings mentioned. This summary can be used as context
    when the full conversation exceeds token limits.
    """
    logger.info(f"Summarizing chat context ({len(conversation_history)} messages)")

    if not conversation_history:
        return "No previous conversation."

    try:
        # Convert conversation history to a readable format
        conversation_text = ""
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            conversation_text += f"{role.upper()}: {content}\n\n"

        system_prompt = (
            "You are a medical conversation summarizer. Given a chat conversation between a user and a medical assistant, "
            f"create a concise summary in {language} that captures: "
            "- Key medical topics discussed "
            "- Important symptoms or findings mentioned "
            "- Questions asked by the user "
            "- Key advice or information provided "
            "Keep the summary brief (2-3 sentences) and focused on medical context. "
            "Do not include any new medical advice or diagnoses."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please summarize this medical conversation:\n\n{conversation_text}"}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model='amsaravi/medgemma-4b-it:q8',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 150}  # Keep summary short
        )

        summary = resp.get('message', {}).get('content', '').strip()

        # Apply guardrails to ensure no inappropriate content
        validated_summary = _guardrail_validator(summary)

        logger.info(f"Chat context summarized: {validated_summary[:100]}...")
        return validated_summary

    except Exception as e:
        logger.error(f"Chat context summarization failed: {e}", exc_info=True)
        # Fallback: create a simple summary
        topics = []
        for msg in conversation_history[-5:]:  # Look at recent messages
            content = msg.get('content', '').lower()
            if 'pain' in content or 'symptom' in content:
                topics.append('symptoms discussed')
            elif 'test' in content or 'result' in content:
                topics.append('test results')
            elif 'medication' in content or 'treatment' in content:
                topics.append('treatment options')

        if topics:
            return f"Previous conversation covered: {', '.join(set(topics))}."
        else:
            return "Previous medical conversation summary not available."
