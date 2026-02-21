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
from app.core.config import settings
from app.services.translation_service import translation_service


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
    """Generate a greeting response."""
    return "Hello! I'm MedAnalyzer Assistant, ready to help you understand your medical reports., " \
        "summarize uploaded documents for a patient or a doctor, or clarify medical terms. " \
        "Feel free to upload a PDF or image, then ask a question like: 'Explain the key findings for a patient.'"


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

# In generate_chat_response_streaming function, replace the translation logic:

async def generate_chat_response_streaming(user_message: str, history: List[Dict[str, str]] = None, image_path: str = None, target_language: str = 'en'):
    """Generate streaming chat response with proper multilingual support and history."""
    logger.info(f"Streaming response for: {user_message[:50]}..., target_language: {target_language}")
    
    # STEP 1: Always translate user message to English for AI processing
    # (LLaMA works best with English, especially for medical terms)
    processed_message = user_message
    
    detected_lang = translation_service.detect_language(user_message)
    if detected_lang in ['hi', 'mr']:
        # User wrote in Hindi or Marathi, translate to English for AI
        processed_message = translation_service.translate_to_english(user_message)
        logger.info(f"Translated {detected_lang} input to English: {processed_message[:50]}...")
        # If user wrote in English, keep as-is for AI but we'll translate output later
    
    # Handle greetings with proper language
    if is_simple_greeting(processed_message):
        greeting_response = generate_greeting_response()
        if target_language in ['hi', 'mr']:
            greeting_response = translation_service.translate_to_target(greeting_response, target_lang=target_language)
        yield greeting_response
        return

    # Validate query (in English)
    is_valid, err = validate_user_query(processed_message)
    if not is_valid:
        if target_language in ['hi', 'mr']:
            err = translation_service.translate_to_target(err, target_lang=target_language)
        yield err
        return

    # STEP 2: Create system prompt that instructs AI to respond in target language
    if target_language == 'hi':
        system_prompt = (
            "You are MedAnalyzer Assistant (मेडएनालाइजर असिस्टेंट), a professional medical information assistant. "
            "You MUST respond ENTIRELY in Hindi language (Devanagari script). "
            "Use clear, professional Hindi. Do NOT use English words like 'felt', 'risk', 'important' etc. in the middle of Hindi sentences. "
            "Translate them naturally: 'महसूस' for 'felt', 'जोखिम' for 'risk', 'महत्वपूर्ण' for 'important'. "
            "Format your response with proper Markdown headings and bullet points. "
            "For medical terms, you MAY include the English term in parentheses after the Hindi term, e.g., 'मधुमेह (Diabetes)'. "
            "Do NOT include meta-comments like '(Continuation)' or 'Still searching'. "
            "Respond only with the requested information."
        )
    elif target_language == 'mr':
        system_prompt = (
            "You are MedAnalyzer Assistant (मेडएनालाइजर असिस्टंट), a professional medical information assistant. "
            "You MUST respond ENTIRELY in Marathi language (Devanagari script). "
            "Use clear, professional Marathi. Do NOT use English words in the middle of Marathi sentences. "
            "Translate them naturally: 'वाटले' for 'felt', 'धोका' for 'risk', 'महत्वाचे' for 'important'. "
            "Format your response with proper Markdown headings and bullet points. "
            "For medical terms, you MAY include the English term in parentheses after the Marathi term, e.g., 'मधुमेह (Diabetes)'. "
            "Do NOT include meta-comments and respond only with information."
        )
    else:
        system_prompt = (
            "You are MedAnalyzer Assistant, a professional medical information assistant "
            "specialized in helping patients understand their medical reports and test results. "
            "Respond in clear, professional English."
        )

    # Detect if user is switching languages from previous context
    if history and len(history) > 0:
        last_asst_msg = next((m for m in reversed(history) if m.get('role') == 'assistant'), None)
        if last_asst_msg:
            last_content = last_asst_msg.get('content', '')
            last_lang = translation_service.detect_language(last_content)
            # If previous was Devanagari (hi/mr) and we are now in something else, or vice-versa
            if last_lang != target_language and target_language in ['hi', 'mr']:
                lang_name = "Hindi" if target_language == 'hi' else "Marathi"
                # More aggressive instruction for language switch
                system_prompt += f"\n\nCRITICAL: The user has explicitly switched from {last_lang} to {lang_name}. "
                system_prompt += f"You MUST ignore the language of the previous history and respond ONLY in {lang_name}. "
                system_prompt += f"Even if the history is in {last_lang}, your new response must be 100% {lang_name}."

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    
    # STEP 3: Add history (limit to last 10 messages)
    if history:
        for msg in history[-10:]:
            role = msg.get('role')
            content = msg.get('content', '')
            if role and content:
                # Clean up content for the AI
                # 1. Remove file attachment markers
                clean_content = re.sub(r'📎 .*\n\n', '', content)
                # 2. If it's a dual-language message, extract only the part matching user's likely preferred view
                # If we are in Hindi mode, and there's a translation, the Hindi part is better context.
                if "[अनुवाद / Translation]:" in clean_content:
                    parts = clean_content.split("[अनुवाद / Translation]:")
                    clean_content = parts[-1].strip()
                messages.append({"role": role, "content": clean_content})

    if image_path:
        messages.append({"role": "user", "content": processed_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": processed_message})

    try:
        if not is_ollama_reachable(timeout=0.8):
            logger.warning("Ollama not reachable for streaming")
            error_msg = "The AI engine is temporarily unavailable. Please try again shortly."
            if target_language in ['hi', 'mr']:
                error_msg = translation_service.translate_to_target(error_msg, target_lang=target_language)
            yield error_msg
            return

        logger.info("Calling Ollama streaming chat...")
        stream = ollama.chat(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 800},
            stream=True
        )

        full_response = ""
        chunk_buffer = ""
        
        # Stream the response
        for chunk in stream:
            token = chunk['message']['content']
            full_response += token
            chunk_buffer += token

            # Yield chunks for real-time display
            if len(chunk_buffer.split()) >= 8 or chunk_buffer.strip().endswith(('.', '!', '?', '।')):
                yield chunk_buffer
                chunk_buffer = ""

        # Yield remaining buffer
        if chunk_buffer:
            yield chunk_buffer

        # Apply guardrails (check the English version if we need to validate)
        validated = apply_response_guardrails(full_response)
        
        # If guardrails modified the response, yield the difference
        if validated != full_response:
            yield validated[len(full_response):]
            full_response = validated

        # STEP 4: If target is Hindi but AI responded in English, translate the full response
        # (This is a safety net - the system prompt should make AI respond in Hindi,
        # but LLaMA 3:8b might not always follow instructions perfectly)
        if target_language in ['hi', 'mr']:
            # Check if response is mostly English or mismatch (e.g. Hindi when Marathi requested)
            english_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', full_response))
            total_words = len(full_response.split())
            
            detected_out_lang = translation_service.detect_language(full_response)
            
            # Trigger translation if:
            # 1. Mostly English
            # 2. Target is Marathi but detected Hindi (or vice versa)
            needs_translation = False
            if total_words > 5 and english_words > total_words * 0.35:
                needs_translation = True
            elif target_language == 'mr' and detected_out_lang == 'hi':
                # Target is Marathi but detected Hindi (now smarter detection)
                needs_translation = True
            elif target_language == 'hi' and detected_out_lang == 'mr':
                # Target is Hindi but detected Marathi
                needs_translation = True

            if needs_translation:
                lang_name = "Hindi" if target_language == 'hi' else "Marathi"
                logger.info(f"AI response language mismatch for {target_language} (detected {detected_out_lang}), translating to {lang_name}...")
                target_response = translation_service.translate_to_target(full_response, target_lang=target_language)
                yield f"\n\n---\n[अनुवाद / Translation ({lang_name})]:\n"
                yield target_response

        logger.info("Streaming chat response completed")

    except Exception as e:
        logger.exception("Streaming chat response generation failed: %s", e)
        error_msg = "I ran into an issue generating the response. Please try again."
        if target_language in ['hi', 'mr']:
            error_msg = translation_service.translate_to_target(error_msg, target_lang=target_language)
        yield error_msg


def generate_chat_response(user_message: str, history: List[Dict[str, str]] = None, image_path: str = None, target_language: str = 'en') -> str:
    """Generate non-streaming chat response with multilingual support and history."""
    logger.info(f"Generating chat response for: {user_message[:50]}..., target_language: {target_language}")

    # STEP 1: Translate input to English if needed
    processed_message = user_message
    detected_lang = translation_service.detect_language(user_message)
    if detected_lang in ['hi', 'mr']:
        processed_message = translation_service.translate_to_english(user_message)
        logger.info(f"Translated {detected_lang} input to English: {processed_message[:50]}...")

    # Handle greetings
    if is_simple_greeting(processed_message):
        greeting_response = generate_greeting_response()
        if target_language in ['hi', 'mr']:
            greeting_response = translation_service.translate_to_target(greeting_response, target_lang=target_language)
        return greeting_response

    # Validate
    is_valid, err = validate_user_query(processed_message)
    if not is_valid:
        if target_language in ['hi', 'mr']:
            err = translation_service.translate_to_target(err, target_lang=target_language)
        return err

    # STEP 2: Language-specific system prompt
    if target_language == 'hi':
        system_prompt = (
            "You are MedAnalyzer Assistant. "
            "You MUST respond entirely in Hindi language. "
            "Use simple Hindi suitable for patients. "
            "Explain all medical terms in Hindi."
        )
    elif target_language == 'mr':
        system_prompt = (
            "You are MedAnalyzer Assistant. "
            "You MUST respond entirely in Marathi language. "
            "Use simple Marathi suitable for patients. "
            "Explain all medical terms in Marathi."
        )
    else:
        system_prompt = (
            "You are MedAnalyzer Assistant, a professional medical information assistant "
            "specialized in helping patients understand their medical reports and test results."
        )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    # STEP 3: Add history
    if history:
        for msg in history[-10:]:
            role = msg.get('role')
            content = msg.get('content', '')
            if role and content:
                clean_content = re.sub(r'📎 .*\n\n', '', content)
                messages.append({"role": role, "content": clean_content})

    if image_path:
        messages.append({"role": "user", "content": processed_message, "images": [image_path]})
    else:
        messages.append({"role": "user", "content": processed_message})

    try:
        if not is_ollama_reachable(timeout=0.8):
            error_msg = (
                "The AI engine is temporarily unavailable. Please try again soon. "
                "If this keeps happening, ensure the model server is running."
            )
            if target_language == 'hi':
                error_msg = translation_service.translate_to_hindi(error_msg)
            return error_msg

        logger.info("Calling Ollama via chat_with_retries...")
        resp = chat_with_retries(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.7, "top_p": 0.9, "num_predict": 800},
        )

        raw_response = resp["message"].content

        if not raw_response:
            error_msg = "I apologize, but I couldn't generate a response. Please try again."
            if target_language == 'hi':
                error_msg = translation_service.translate_to_hindi(error_msg)
            return error_msg

        # Apply guardrails
        validated = apply_response_guardrails(raw_response)
        
        # STEP 4: Ensure Hindi output if requested
        if target_language in ['hi', 'mr']:
            # Devanagari range check for both Hindi and Marathi
            target_chars = len(re.findall(r'[\u0900-\u097F]', validated))
            total_chars = len(validated)
            
            if total_chars > 20 and target_chars < total_chars * 0.3:
                logger.info(f"Response mostly in English for {target_language}, appending translation...")
                target_trans = translation_service.translate_to_target(validated, target_lang=target_language)
                validated = f"{validated}\n\n---\n[अनुवाद / Translation]:\n{target_trans}"
        
        logger.info("Chat response validated and ready")
        return validated

    except Exception as e:
        logger.exception("Chat response generation failed")
        error_msg = "I ran into an issue processing that. Please try again."
        if target_language == 'hi':
            error_msg = translation_service.translate_to_hindi(error_msg)
        return error_msg
