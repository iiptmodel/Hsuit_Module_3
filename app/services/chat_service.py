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
from app.services.translation_service import maybe_translate
from app.core.config import settings


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
    "hindi_diagnosis": [
        r"आपको.*(है|हैं|हो)",          # "You have [condition]"
        r"आप.*(बीमारी|रोग|विकार).*(से पीड़ित|है)",
        r"(मेरा|मैं).*(निदान|डायग्नोसिस)",
        r"निश्चित रूप से.*(है|हैं)",
    ],
    "hindi_prescription": [
        r"आप.*(मिलीग्राम|mg|ml).*(लें|खाएं|पियें)",
        r"(रोज़|प्रतिदिन|दिन में).*(मिलीग्राम|mg)",
        r"मैं.*(दवाई|दवा|औषधि).*(देता|देती|लिखता)",
        r"(शुरू करें|लेना शुरू करें).*(मिलीग्राम|mg)",
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


_GUARDRAIL_SUFFIX = {
    'hindi': (
        " कभी भी निश्चित निदान न दें या दवाइयाँ न लिखें। "
        "हमेशा रोगी को डॉक्टर से परामर्श लेने की सलाह दें।"
    ),
    'english': (
        " Never provide a definitive diagnosis or prescribe medications. "
        "Always recommend consulting a healthcare professional."
    ),
}


_GREETINGS = {
    'hindi': (
        "नमस्ते! मैं आपका MedAnalyzer सहायक हूँ। "
        "आप मुझसे इमेजिंग, लैब या अन्य चिकित्सा रिपोर्ट समझने में मदद माँग सकते हैं, "
        "दस्तावेज़ अपलोड कर सकते हैं और पूछ सकते हैं जैसे: 'यह रिपोर्ट रोगी के लिए समझाइए।'"
    ),
}


def generate_greeting_response(language: str = 'English') -> str:
    """Static friendly greeting in the requested language."""
    key = language.lower()
    if key in _GREETINGS:
        return _GREETINGS[key]
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


def apply_response_guardrails(response: str, language: str = 'English') -> str:
    """Filter AI response to enforce medical safety guardrails."""
    response_lower = (response or "").lower()

    for pattern in PROHIBITED_PATTERNS["diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained diagnosis language: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं चिकित्सा निष्कर्षों को समझाने में मदद कर सकता हूँ, लेकिन निश्चित निदान नहीं दे सकता। "
                    "कृपया अपने स्वास्थ्य सेवा प्रदाता से परामर्श करें।"
                )
            return (
                "I can help you understand what these medical findings suggest, but I cannot provide a definitive diagnosis. "
                "Based on the information, I recommend discussing these results with your healthcare provider who can properly evaluate "
                "your complete medical history and provide an accurate diagnosis. "
                "Would you like me to explain what these findings typically indicate?"
            )

    for pattern in PROHIBITED_PATTERNS["prescription"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained prescription language: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं दवाइयाँ लिख या सुझाव नहीं दे सकता। "
                    "सही खुराक के लिए अपने डॉक्टर से मिलें।"
                )
            return (
                "I can explain how certain medications work and their general purposes, but I cannot prescribe specific medications or dosages. "
                "Your doctor will determine the appropriate medication and dosage based on your individual health needs. "
                "Would you like me to explain what types of treatments are commonly used for this condition instead?"
            )

    for pattern in PROHIBITED_PATTERNS["mental_health_diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained mental health diagnosis: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं मानसिक स्वास्थ्य निदान नहीं कर सकता। "
                    "कृपया किसी मानसिक स्वास्थ्य विशेषज्ञ से परामर्श करें।"
                )
            return (
                "I cannot provide mental health diagnoses or psychiatric evaluations. "
                "If you're experiencing mental health concerns, please consult with a licensed mental health professional or psychiatrist."
            )

    for pattern in PROHIBITED_PATTERNS["jokes"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained humor: %s", pattern)
            if language.lower() == 'hindi':
                return "मैं क्षमा चाहता हूँ। मैं केवल चिकित्सा जानकारी प्रदान करने के लिए यहाँ हूँ।"
            return "I apologize for the inappropriate response. Let me provide you with factual medical information instead."

    # Hindi-specific guardrails (applied to original response, not lowercased, since Devanagari is case-neutral)
    if language.lower() == 'hindi':
        for pattern in PROHIBITED_PATTERNS["hindi_diagnosis"]:
            if re.search(pattern, response):
                logger.warning("Hindi response contained diagnosis language: %s", pattern)
                return (
                    "मैं चिकित्सा निष्कर्षों को समझाने में मदद कर सकता हूँ, लेकिन निश्चित निदान नहीं दे सकता। "
                    "कृपया अपने स्वास्थ्य सेवा प्रदाता से परामर्श करें।"
                )
        for pattern in PROHIBITED_PATTERNS["hindi_prescription"]:
            if re.search(pattern, response):
                logger.warning("Hindi response contained prescription language: %s", pattern)
                return (
                    "मैं दवाइयाँ लिख या सुझाव नहीं दे सकता। "
                    "सही खुराक के लिए अपने डॉक्टर से मिलें।"
                )

    return response

async def generate_chat_response_streaming(user_message: str, image_path: str = None, language: str = 'English'):
    """Generate a chat response using Ollama streaming API, yielding tokens in real-time.

    Applies guardrails after full response is received.
    """
    logger.info("Generating streaming chat response for message: %.100s...", user_message)

    # Allow simple greetings to yield a single static message (still via streaming interface)
    if is_simple_greeting(user_message):
        yield generate_greeting_response(language)
        return

    is_valid, err = validate_user_query(user_message)
    if not is_valid:
        yield err
        return

    # Always generate in English — the model is English-only.
    # Translation to the target language happens after generation.
    system_prompt = (
        "You are MedAnalyzer Assistant, a professional medical information assistant "
        "specialized in helping patients understand their medical reports and test results."
        + _GUARDRAIL_SUFFIX['english']
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
            yield maybe_translate(
                "The AI engine is temporarily unavailable. Please try again shortly.", language
            )
            return

        logger.info("Calling Ollama streaming chat...")
        stream = ollama.chat(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 300},
            stream=True
        )

        full_response = ""
        chunk_buffer = ""
        chunk_size = 10
        needs_translation = language.lower() != 'english'

        for chunk in stream:
            token = chunk['message']['content']
            full_response += token
            chunk_buffer += token

            # Stream English chunks in real-time; buffer for non-English (translate at end)
            if not needs_translation:
                if len(chunk_buffer.split()) >= chunk_size or chunk_buffer.strip().endswith(('.', '!', '?')):
                    yield chunk_buffer
                    chunk_buffer = ""

        if not needs_translation and chunk_buffer:
            yield chunk_buffer

        # Apply guardrails on the English output, then translate
        validated = apply_response_guardrails(full_response, language='English')
        final = maybe_translate(validated, language)
        if needs_translation:
            # Yield the entire translated response as one chunk
            yield final
        elif final != full_response:
            yield final
        full_response = final

        logger.info("Streaming chat response completed and validated")

    except Exception as e:
        logger.exception("Streaming chat response generation failed: %s", e)
        lowered = str(e).lower()
        if "failed to connect" in lowered or "connectionerror" in lowered:
            yield maybe_translate(
                "I couldn't reach the AI engine. Please try again shortly.", language
            )
        else:
            yield maybe_translate(
                "I ran into an issue generating a response. Please try again or rephrase your question.", language
            )


def generate_chat_response(user_message: str, image_path: str = None, language: str = 'English') -> str:
    """Generate a chat response using Ollama (via chat_with_retries) and apply guardrails.

    conversation_history: list of {"role": "user|assistant", "content": str}
    """
    logger.info("Generating chat response for message: %.100s...", user_message)

    if is_simple_greeting(user_message):
        return generate_greeting_response(language)

    is_valid, err = validate_user_query(user_message)
    if not is_valid:
        return err

    system_prompt = (
        "You are MedAnalyzer Assistant, a professional medical information assistant "
        "specialized in helping patients understand their medical reports and test results."
        + _GUARDRAIL_SUFFIX['english']
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    if image_path:
        messages.append({"role": "user", "content": user_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        if not is_ollama_reachable(timeout=0.8):
            logger.warning("Ollama server not reachable; returning friendly message")
            return maybe_translate(
                "The AI engine is temporarily unavailable. Please try again soon.", language
            )

        logger.info("Calling Ollama via chat_with_retries...")
        resp = chat_with_retries(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 300},
        )

        raw_response = resp["message"].content

        if not raw_response:
            logger.warning("Empty response from Ollama: %s", resp)
            return maybe_translate(
                "I couldn't generate a response. Please try again.", language
            )

        validated = apply_response_guardrails(raw_response, language='English')
        final = maybe_translate(validated, language)
        logger.info("Chat response validated and ready")
        return final

    except Exception as e:
        logger.exception("Chat response generation failed")
        lowered = str(e).lower()
        if "failed to connect" in lowered or "connectionerror" in lowered:
            return maybe_translate(
                "I couldn't reach the AI engine. Please retry in a moment.", language
            )
        return maybe_translate(
            "I ran into an issue processing that. Please try again or rephrase your question.", language
        )
