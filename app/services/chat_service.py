"""Medical Chat Service with Guardrails.

Provides a thin service layer that builds prompts, calls the Ollama wrapper
`chat_with_retries` and enforces medical safety guardrails on the assistant
output.

This file intentionally keeps responsibilities small and pure: validate the
user query, call the model (via the retry wrapper), and ensure the model's
text does not include diagnoses or prescription recommendations.
"""

from typing import Any, Dict, List, Tuple
import logging
import re

from app.services.ollama_client import chat_with_retries

logger = logging.getLogger(__name__)


# Prohibited topics and regex patterns for safety
PROHIBITED_PATTERNS: Dict[str, List[str]] = {
    "diagnosis": [
        r"\byou (definitely|certainly|clearly) have\b",
        r"\byou are (definitely |certainly )?suffering from\b",
        r"\bmy diagnosis is\b",
        r"\bI (diagnose|confirm) (you have|that you have)\b",
        r"\bthis confirms? (you have|that you have)\b",
    ],
    "prescription": [
        r"\bI (prescribe|recommend taking|suggest taking)\b",
        r"\byou (should|must|need to) take \d+\s*mg\b",
        r"\bstart (taking|medication|treatment with)\b.*\b\d+\s*mg\b",
        r"\btake \w+ \d+\s*(mg|ml) (daily|twice|three times)\b",
        r"\bprescription:?\s*\w+\s*\d+\s*mg\b",
        r"\bI will prescribe\b",
    ],
    "jokes": [
        r"\b(here's a|want to hear a|let me tell you a) joke\b",
        r"\bhaha\b.*\bfunny\b",
        r"\blol\b.*\bhilarious\b",
        r"\bpunchline\b",
    ],
    "timepass": [
        r"\blet's (chat|talk) about (movies|music|sports|weather)\b",
        r"\btell me about (yourself|your hobbies|your life)\b",
        r"\bwhat's? your favorite (movie|song|color|food)\b",
    ],
    "mental_health_diagnosis": [
        r"\byou (have|are suffering from) (clinical )?depression\b",
        r"\byou (have|are suffering from) (severe |chronic )?anxiety disorder\b",
        r"\byou (have|are suffering from) bipolar( disorder)?\b",
        r"\byou (have|are suffering from) schizophrenia\b",
        r"\bI diagnose you with\b.*\b(depression|anxiety|bipolar|ptsd)\b",
    ],
}


def validate_user_query(query: str) -> Tuple[bool, str]:
    """Validate if user query is appropriate for medical assistant.

    Returns (is_valid, error_message).
    """
    query_lower = (query or "").lower().strip()

    # Allow common greetings
    greeting_patterns = [
        r"^\b(hello|hi|hey|good (morning|afternoon|evening)|how are you|howdy|greetings)\b.*$",
        r".*\b(hello|hi|hey|good (morning|afternoon|evening)|how are you|howdy|greetings)\b.*$",
    ]
    if any(re.search(p, query_lower) for p in greeting_patterns):
        return True, ""

    if len(query_lower) < 3:
        return False, "Please provide a more detailed question."

    offensive_patterns = [r"\bfuck\b", r"\bshit\b", r"\bdamn\b", r"\bass\b", r"\bhell\b"]
    if any(re.search(p, query_lower) for p in offensive_patterns):
        return False, "Please keep the conversation professional and respectful."

    if any(re.search(p, query_lower) for p in PROHIBITED_PATTERNS["timepass"]):
        return False, (
            "I'm here to help with medical information and report analysis. "
            "Please ask health-related questions."
        )

    return True, ""


def apply_response_guardrails(response: str) -> str:
    """Filter AI response to enforce medical safety guardrails."""
    response_lower = (response or "").lower()

    for pattern in PROHIBITED_PATTERNS["diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained diagnosis language: %s", pattern)
            return (
                "I can help you understand what these medical findings suggest, "
                "but I cannot provide a definitive diagnosis. Based on the information, "
                "I recommend discussing these results with your healthcare provider who can "
                "properly evaluate your complete medical history and provide an accurate diagnosis. "
                "Would you like me to explain what these findings typically indicate?"
            )

    for pattern in PROHIBITED_PATTERNS["prescription"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained prescription language: %s", pattern)
            return (
                "I can explain how certain medications work and their general purposes, "
                "but I cannot prescribe specific medications or dosages. "
                "Your doctor will determine the appropriate medication and dosage based on "
                "your individual health needs. Would you like me to explain what types of "
                "treatments are commonly used for this condition instead?"
            )

    for pattern in PROHIBITED_PATTERNS["mental_health_diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained mental health diagnosis: %s", pattern)
            return (
                "I cannot provide mental health diagnoses or psychiatric evaluations. "
                "If you're experiencing mental health concerns, please consult "
                "with a licensed mental health professional or psychiatrist."
            )

    for pattern in PROHIBITED_PATTERNS["jokes"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained humor: %s", pattern)
            return "I apologize for the inappropriate response. Let me provide you with factual medical information instead."

    return response


def generate_chat_response(conversation_history: List[Dict[str, str]], user_message: str, image_path: str = None) -> str:
    """Generate a chat response using Ollama (via chat_with_retries) and apply guardrails.

    conversation_history: list of {"role": "user|assistant", "content": str}
    """
    logger.info("Generating chat response for message: %.100s...", user_message)

    is_valid, err = validate_user_query(user_message)
    if not is_valid:
        return err

    system_prompt = (
        "You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results."
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for msg in (conversation_history or [])[-5:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    if image_path:
        messages.append({"role": "user", "content": user_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        logger.info("Calling Ollama via chat_with_retries...")
        resp = chat_with_retries(
            model="amsaravi/medgemma-4b-it:q8",
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 300},
        )

        # Expect the client to return a structure with ['message']['content'] like ollama.chat
        raw_response = None
        if isinstance(resp, dict) and "message" in resp and isinstance(resp["message"], dict):
            raw_response = resp["message"].get("content")
        elif hasattr(resp, "content"):
            raw_response = getattr(resp, "content")

        if not raw_response:
            logger.warning("Empty response from Ollama: %s", resp)
            return "I apologize, but I couldn't generate a response. Please try again."

        validated = apply_response_guardrails(raw_response)
        logger.info("Chat response validated and ready")
        return validated

    except Exception:
        logger.exception("Chat response generation failed")
        return "I apologize, but I encountered an error processing your message. Please try rephrasing your question."
