import logging
import re
from typing import List, Dict
from app.services import summarizer_service

logger = logging.getLogger(__name__)

# Prohibited topics and patterns
PROHIBITED_PATTERNS = {
    'diagnosis': [
        r'\bdiagnos[ei]s?\b', r'\byou have\b', r'\byou are suffering from\b',
        r'\byou might have\b', r'\bit (seems|appears|looks) like you have\b'
    ],
    'prescription': [
        r'\btake (this|these|the following)\b', r'\bprescribe\b', r'\bmedication\b.*\bdosage\b',
        r'\b\d+\s*mg\b', r'\btake.*pills?\b', r'\bdrug\b.*\btreatment\b'
    ],
    'jokes': [
        r'\bjoke\b', r'\bfunny\b', r'\blaugh\b', r'\bhaha\b', r'\blol\b',
        r'\bhumor\b', r'\bpunchline\b'
    ],
    'timepass': [
        r'\blet\'s chat about\b', r'\btell me about yourself\b', r'\bwhat do you like\b',
        r'\bfavorite (movie|song|color|food)\b'
    ],
    'mental_health_diagnosis': [
        r'\bdepression\b', r'\banxiety disorder\b', r'\bbipolar\b', r'\bschizophrenia\b',
        r'\bptsd\b', r'\bmental illness\b', r'\bpsychiatric\b'
    ]
}


def validate_user_query(query: str) -> tuple[bool, str]:
    """
    Validates if user query is appropriate for medical assistant.
    Returns (is_valid, error_message)
    """
    query_lower = query.lower().strip()
    
    # Check if empty or too short
    if len(query_lower) < 3:
        return False, "Please provide a more detailed question."
    
    # Check for offensive content
    offensive_patterns = [r'\bfuck\b', r'\bshit\b', r'\bdamn\b', r'\bass\b', r'\bhell\b']
    for pattern in offensive_patterns:
        if re.search(pattern, query_lower):
            return False, "Please keep the conversation professional and respectful."
    
    # Check for time-pass queries
    if any(re.search(pattern, query_lower) for pattern in PROHIBITED_PATTERNS['timepass']):
        return False, "I'm here to help with medical information and report analysis. Please ask health-related questions."
    
    return True, ""


def apply_response_guardrails(response: str) -> str:
    """
    Validates and filters AI response to ensure it follows medical guardrails.
    """
    response_lower = response.lower()
    
    # Check for diagnosis language
    for pattern in PROHIBITED_PATTERNS['diagnosis']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained diagnosis language: {pattern}")
            return "I apologize, but I cannot provide medical diagnoses. I can help explain medical information, but any diagnosis should come from a qualified healthcare provider. Would you like me to explain any medical terms or concepts instead?"
    
    # Check for prescription language
    for pattern in PROHIBITED_PATTERNS['prescription']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained prescription language: {pattern}")
            return "I apologize, but I cannot prescribe medications or recommend specific treatments. Only licensed healthcare providers can do that. I can explain what certain medications do or help you understand medical information, though."
    
    # Check for mental health diagnosis
    for pattern in PROHIBITED_PATTERNS['mental_health_diagnosis']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained mental health diagnosis: {pattern}")
            return "I cannot provide mental health diagnoses or psychiatric evaluations. If you're experiencing mental health concerns, please consult with a licensed mental health professional or psychiatrist."
    
    # Check for jokes/humor
    for pattern in PROHIBITED_PATTERNS['jokes']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained humor: {pattern}")
            return "I apologize for the inappropriate response. Let me provide you with factual medical information instead."
    
    return response


def generate_chat_response(conversation_history: List[Dict[str, str]], user_message: str) -> str:
    """
    Generates a chat response using MedGemma with strict medical guardrails.
    
    Args:
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        user_message: The current user message
    
    Returns:
        AI response with guardrails applied
    """
    logger.info(f"Generating chat response for message: {user_message[:100]}...")
    
    # Validate user query first
    is_valid, error_msg = validate_user_query(user_message)
    if not is_valid:
        return error_msg
    
    try:
        # Check if model is available
        if not summarizer_service._MODEL_AVAILABLE or summarizer_service.model is None:
            logger.warning("MedGemma model unavailable for chat")
            return "I apologize, but the AI model is currently unavailable. Please try again later."
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": """You are MedAnalyzer Assistant, a professional medical information assistant. Your role is to:

1. Help users understand medical reports and test results
2. Explain medical terminology in simple terms
3. Provide factual medical information and education
4. Answer health-related questions with evidence-based information

STRICT RULES YOU MUST FOLLOW:
- NEVER provide medical diagnoses (e.g., "you have diabetes")
- NEVER prescribe medications or recommend specific treatments
- NEVER make jokes, use humor, or engage in casual chitchat
- NEVER discuss mental health diagnoses or psychiatric conditions
- NEVER give personalized medical advice
- Always recommend consulting healthcare professionals for diagnosis and treatment
- Stay professional, factual, and educational
- If asked about non-medical topics, politely redirect to medical information

Remember: You explain medical information, you don't diagnose or treat."""
                }]
            }
        ]
        
        # Add conversation history (last 5 messages to avoid token limits)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })
        
        # Generate response
        logger.info("Tokenizing chat input for MedGemma...")
        inputs = summarizer_service.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            use_fast=True
        ).to(summarizer_service.model.device, dtype=summarizer_service.torch.bfloat16)
        
        input_len = inputs["input_ids"].shape[-1]
        logger.info(f"Input tokenized, length: {input_len}")
        
        logger.info("Generating chat response with MedGemma...")
        with summarizer_service.torch.inference_mode():
            generation = summarizer_service.model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                temperature=0.7,
                top_p=0.9
            )
            generation = generation[0][input_len:]
        
        response = summarizer_service.processor.decode(generation, skip_special_tokens=True)
        logger.info(f"Raw chat response generated: {response[:100]}...")
        
        # Apply guardrails to response
        validated_response = apply_response_guardrails(response)
        logger.info("Chat response validation completed")
        
        return validated_response
        
    except Exception as e:
        logger.error(f"Chat response generation failed: {e}", exc_info=True)
        return "I apologize, but I encountered an error processing your message. Please try rephrasing your question."
