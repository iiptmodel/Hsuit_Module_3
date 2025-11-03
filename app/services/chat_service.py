"""
Medical Chat Service with Guardrails

This module provides AI-powered chat functionality with strict medical safety guardrails.
It prevents the AI from providing diagnoses, prescriptions, or inappropriate content.

Safety Features:
    - Prevents medical diagnoses
    - Blocks prescription recommendations
    - Filters mental health diagnostic content
    - Blocks jokes and time-pass conversations
    - Ensures professional, educational responses only

Dependencies:
    - summarizer_service: For MedGemma AI model integration
    - re: For pattern matching and validation

Author: Medical Report Analysis System
"""

import logging
import re
from typing import List, Dict, Tuple
import ollama
from app.services import summarizer_service

logger = logging.getLogger(__name__)

# Prohibited topics and regex patterns for safety
PROHIBITED_PATTERNS = {
    'diagnosis': [
        r'\byou (definitely|certainly|clearly) have\b',
        r'\byou are (definitely |certainly )?suffering from\b',
        r'\bmy diagnosis is\b',
        r'\bI (diagnose|confirm) (you have|that you have)\b',
        r'\bthis confirms? (you have|that you have)\b'
    ],
    'prescription': [
        r'\bI (prescribe|recommend taking|suggest taking)\b',
        r'\byou (should|must|need to) take \d+\s*mg\b',
        r'\bstart (taking|medication|treatment with)\b.*\b\d+\s*mg\b',
        r'\btake \w+ \d+\s*(mg|ml) (daily|twice|three times)\b',
        r'\bprescription:?\s*\w+\s*\d+\s*mg\b',
        r'\bI will prescribe\b'
    ],
    'jokes': [
        r'\b(here\'s a|want to hear a|let me tell you a) joke\b',
        r'\bhaha\b.*\bfunny\b',
        r'\blol\b.*\bhilarious\b',
        r'\bpunchline\b'
    ],
    'timepass': [
        r'\blet\'s (chat|talk) about (movies|music|sports|weather)\b',
        r'\btell me about (yourself|your hobbies|your life)\b',
        r'\bwhat\'s? your favorite (movie|song|color|food)\b'
    ],
    'mental_health_diagnosis': [
        r'\byou (have|are suffering from) (clinical )?depression\b',
        r'\byou (have|are suffering from) (severe |chronic )?anxiety disorder\b',
        r'\byou (have|are suffering from) bipolar( disorder)?\b',
        r'\byou (have|are suffering from) schizophrenia\b',
        r'\bI diagnose you with\b.*\b(depression|anxiety|bipolar|ptsd)\b'
    ]
}


def validate_user_query(query: str) -> Tuple[bool, str]:
    """
    Validate if user query is appropriate for medical assistant.
    
    Checks for:
        - Minimum query length
        - Offensive language
        - Time-pass/off-topic queries
    
    Args:
        query: User's input message
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if query passes all checks
            - error_message: Empty string if valid, error description if invalid
            
    Example:
        >>> is_valid, error = validate_user_query("Explain this report")
        >>> print(is_valid)  # True
        >>> print(error)     # ""
    """
    query_lower = query.lower().strip()
    
    # Check minimum length
    if len(query_lower) < 3:
        return False, "Please provide a more detailed question."
    
    # Check for offensive content
    offensive_patterns = [
        r'\bfuck\b', r'\bshit\b', r'\bdamn\b',
        r'\bass\b', r'\bhell\b'
    ]
    for pattern in offensive_patterns:
        if re.search(pattern, query_lower):
            return (
                False,
                "Please keep the conversation professional and respectful."
            )
    
    # Check for time-pass queries
    for pattern in PROHIBITED_PATTERNS['timepass']:
        if re.search(pattern, query_lower):
            return (
                False,
                "I'm here to help with medical information and report analysis. "
                "Please ask health-related questions."
            )
    
    return True, ""


def apply_response_guardrails(response: str) -> str:
    """
    Validate and filter AI response to ensure medical safety guardrails.
    
    Scans AI-generated responses for prohibited content and replaces
    with safe fallback messages if violations are detected.
    
    Args:
        response: AI-generated response text
        
    Returns:
        str: Original response if safe, fallback message if violations detected
        
    Guardrail Checks:
        - Diagnosis language (e.g., "you have diabetes")
        - Prescription recommendations (e.g., "take 50mg daily")
        - Mental health diagnoses (e.g., "you have depression")
        
    Example:
        >>> safe_response = apply_response_guardrails(ai_response)
        >>> print(safe_response)
    """
    response_lower = response.lower()
    
    # Check for diagnosis language
    for pattern in PROHIBITED_PATTERNS['diagnosis']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained diagnosis language: {pattern}")
            return (
                "I can help you understand what these medical findings suggest, "
                "but I cannot provide a definitive diagnosis. Based on the information, "
                "I recommend discussing these results with your healthcare provider who can "
                "properly evaluate your complete medical history and provide an accurate diagnosis. "
                "Would you like me to explain what these findings typically indicate?"
            )
    
    # Check for prescription language
    for pattern in PROHIBITED_PATTERNS['prescription']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained prescription language: {pattern}")
            return (
                "I can explain how certain medications work and their general purposes, "
                "but I cannot prescribe specific medications or dosages. "
                "Your doctor will determine the appropriate medication and dosage based on "
                "your individual health needs. Would you like me to explain what types of "
                "treatments are commonly used for this condition instead?"
            )
    
    # Check for mental health diagnosis
    for pattern in PROHIBITED_PATTERNS['mental_health_diagnosis']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained mental health diagnosis: {pattern}")
            return (
                "I cannot provide mental health diagnoses or psychiatric evaluations. "
                "If you're experiencing mental health concerns, please consult "
                "with a licensed mental health professional or psychiatrist."
            )
    # Check for jokes/humor
    for pattern in PROHIBITED_PATTERNS['jokes']:
        if re.search(pattern, response_lower):
            logger.warning(f"Response contained humor: {pattern}")
            return "I apologize for the inappropriate response. Let me provide you with factual medical information instead."
    
    return response


def generate_chat_response(conversation_history: List[Dict[str, str]], user_message: str) -> str:
    """
    Generates a chat response using Ollama with strict medical guardrails.

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
        # Define system prompt
        system_prompt = """You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results.

YOUR PRIMARY ROLES:
1. Analyze and explain medical reports (blood tests, imaging, lab results, etc.)
2. Break down complex medical terminology into simple, understandable language
3. Explain what test results mean and their normal ranges
4. Provide general health education and lifestyle recommendations
5. Explain what medications do and their general purposes (WITHOUT prescribing)

WHAT YOU CAN DO:
✓ Explain what high cholesterol means and general ways to manage it (diet, exercise)
✓ Describe what blood test values indicate (e.g., "HbA1c shows average blood sugar levels")
✓ Explain medical conditions in educational terms
✓ Suggest general lifestyle modifications (eat healthy, exercise, reduce stress)
✓ Explain what types of medications exist and their general purposes
✓ Answer "What does this test measure?" or "What does this result mean?"

STRICT RULES - WHAT YOU CANNOT DO:
✗ NEVER diagnose: Don't say "You have diabetes" - instead say "These results suggest elevated blood sugar levels that should be discussed with your doctor"
✗ NEVER prescribe: Don't say "Take 500mg of Metformin daily" - instead say "Metformin is commonly used to manage blood sugar, your doctor will determine the right dosage"
✗ NEVER provide personalized treatment plans
✗ NEVER make jokes or engage in casual chitchat
✗ NEVER diagnose mental health conditions

TONE & APPROACH:
- Be clear, empathetic, and educational
- Use simple language while being accurate
- Always encourage consulting healthcare professionals for diagnosis and treatment
- Focus on helping patients understand their reports and ask better questions to their doctors

Remember: You EXPLAIN medical information to empower patients, you don't replace their doctor."""

        # Build conversation messages for Ollama
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 5 messages to avoid token limits)
        for msg in conversation_history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response using Ollama
        logger.info("Generating chat response with Ollama...")
        response = ollama.chat(
            model='alibayram/medgemma:4b',  # Using MedGemma for medical expertise
            messages=messages,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 300
            }
        )

        raw_response = response['message']['content']
        logger.info(f"Raw chat response generated: {raw_response[:100]}...")

        # Apply guardrails to response
        validated_response = apply_response_guardrails(raw_response)
        logger.info("Chat response validation completed")

        return validated_response

    except Exception as e:
        logger.error(f"Chat response generation failed: {e}", exc_info=True)
        return "I apologize, but I encountered an error processing your message. Please try rephrasing your question."
