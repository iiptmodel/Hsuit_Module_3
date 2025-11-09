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
import ollama

from app.services.ollama_client import chat_with_retries, is_ollama_reachable


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


def is_simple_greeting(query: str) -> bool:
    """Return True if the user input is a short greeting (no medical intent).

    We purposely treat very short greeting variants as a fast-path to avoid
    unnecessary model calls and latency spikes on cold starts.
    """
    if not query:
        return False
    q = query.strip().lower()
    # Accept variants like hi, hii, hiiii, hey, heyy, heyyyy, hello, howdy, greetings
    return bool(re.fullmatch(r"(hi+|he+y+|hello|hey|howdy|greetings|good (morning|afternoon|evening))!?", q))


def generate_greeting_response() -> str:
    """Static friendly greeting used for simple greeting fast-path."""
    return (
        "Hello! I'm your MedAnalyzer Assistant. You can ask me to explain imaging, lab, or other medical reports, "
        "summarize uploaded documents for a patient or a doctor, or clarify medical terms. "
        "Feel free to upload a PDF or image, then ask a question like: 'Explain the key findings for a patient.'"
    )


def validate_user_query(query: str) -> Tuple[bool, str]:
    """Validate if user query is appropriate for medical assistant.

    Returns (is_valid, error_message). Simple greetings are considered valid and handled upstream.
    """
    query_lower = (query or "").lower().strip()

    # Block offensive language
    offensive_patterns = [r"\bfuck\b", r"\bshit\b", r"\bdamn\b", r"\bass\b", r"\bhell\b"]
    if any(re.search(p, query_lower) for p in offensive_patterns):
        return False, "Please keep the conversation professional and respectful."

    # Block off-topic conversation attempts
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

async def generate_chat_response_streaming(user_message: str, image_path: str = None):
    """Generate a chat response using Ollama streaming API, yielding tokens in real-time.

    Applies guardrails after full response is received.
    """
    logger.info("Generating streaming chat response for message: %.100s...", user_message)

    # Allow simple greetings to yield a single static message (still via streaming interface)
    if is_simple_greeting(user_message):
        yield generate_greeting_response()
        return

    is_valid, err = validate_user_query(user_message)
    if not is_valid:
        yield err
        return

    system_prompt = (
        "You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results."
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    if image_path:
        messages.append({"role": "user", "content": user_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        # Preflight check: ensure model backend is reachable to avoid streaming exceptions
        if not is_ollama_reachable(timeout=0.8):
            logger.warning("Ollama not reachable for streaming; returning friendly notice")
            yield "The AI engine is temporarily unavailable for streaming responses. Please try again shortly."
            return

        logger.info("Calling Ollama streaming chat...")
        # Use ollama.chat with stream=True
        stream = ollama.chat(
            model="amsaravi/medgemma-4b-it:q6",
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 300},
            stream=True
        )

        full_response = ""
        chunk_buffer = ""
        chunk_size = 10  # Yield every 10 tokens or at sentence end
        for chunk in stream:
            token = chunk['message']['content']
            full_response += token
            chunk_buffer += token

            # Yield chunk if buffer reaches size or ends with sentence punctuation
            if len(chunk_buffer.split()) >= chunk_size or chunk_buffer.strip().endswith(('.', '!', '?')):
                yield chunk_buffer
                chunk_buffer = ""

        # Yield any remaining buffer
        if chunk_buffer:
            yield chunk_buffer

        # After streaming, apply guardrails to full response
        validated = apply_response_guardrails(full_response)
        if validated != full_response:
            # If guardrails modified the response, yield the difference or handle accordingly
            yield validated[len(full_response):]

        logger.info("Streaming chat response completed and validated")

    except Exception as e:
        logger.exception("Streaming chat response generation failed: %s", e)
        lowered = str(e).lower()
        if "failed to connect" in lowered or "connectionerror" in lowered:
            yield "I couldn't reach the AI engine for streaming. Please try again shortly."
        else:
            yield "I ran into an issue generating the streamed response. Please try again or rephrase your question."


def generate_chat_response(user_message: str, image_path: str = None) -> str:
    """Generate a chat response using Ollama (via chat_with_retries) and apply guardrails.

    conversation_history: list of {"role": "user|assistant", "content": str}
    """
    logger.info("Generating chat response for message: %.100s...", user_message)

    if is_simple_greeting(user_message):
        return generate_greeting_response()

    is_valid, err = validate_user_query(user_message)
    if not is_valid:
        return err

    system_prompt = (
        "You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results."
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    if image_path:
        messages.append({"role": "user", "content": user_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": user_message})

    # Preflight: if the model backend is unreachable, provide a clear user message instead of a generic error
    try:
        if not is_ollama_reachable(timeout=0.8):
            logger.warning("Ollama server not reachable; returning friendly message")
            return (
                "The AI engine is temporarily unavailable. Please try again soon. "
                "If this keeps happening, ensure the model server is running."
            )

        logger.info("Calling Ollama via chat_with_retries...")
        resp = chat_with_retries(
            model="amsaravi/medgemma-4b-it:q8",
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 300},
        )

        # Expect the client to return a structure with ['message']['content'] like ollama.chat
        raw_response = resp["message"].content

        if not raw_response:
            logger.warning("Empty response from Ollama: %s", resp)
            return "I apologize, but I couldn't generate a response. Please try again."

        validated = apply_response_guardrails(raw_response)
        logger.info("Chat response validated and ready")
        return validated

    except Exception as e:
        logger.exception("Chat response generation failed")
        lowered = str(e).lower()
        if "failed to connect" in lowered or "connectionerror" in lowered:
            return "I couldn't reach the AI engine. Please retry in a moment."
        return "I ran into an issue processing that. Please try again or rephrase your question."
