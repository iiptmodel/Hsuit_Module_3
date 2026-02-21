import logging
import os
import ollama
from typing import List, Dict
from app.services import parser_service
from app.core.config import settings
from app.services.translation_service import translation_service

logger = logging.getLogger(__name__)

# Use local Ollama model for summarization rather than loading heavy transformers
# This keeps the service lightweight and delegates model serving to Ollama.

def _guardrail_validator(text: str, language: str = 'en') -> str:
    """Apply guardrails with disclaimer support."""
    # Basic guardrail checks to avoid diagnoses, prescriptions, or casual chat
    prohibited_patterns = ['diagnos', 'prescrib', 'you have', 'take ', 'lol', 'omg']
    
    if language in ['hi', 'Hindi']:
        disclaimer_text = (
            "\n\n[अस्वीकरण] मैं निष्कर्षों को समझाने में मदद कर सकता हूँ, लेकिन मैं निश्चित निदान प्रदान नहीं कर सकता या दवाएं निर्धारित नहीं कर सकता। "
            "कृपया निदान और उपचार के लिए एक योग्य स्वास्थ्य देखभाल पेशेवर से परामर्श लें।"
        )
    elif language in ['mr', 'Marathi']:
        disclaimer_text = (
            "\n\n[अस्वीकरण] मी निष्कर्ष समजून घेण्यास मदत करू शकतो, परंतु मी निश्चित निदान देऊ शकत नाही किंवा औषधे लिहून देऊ शकत नाही. "
            "कृपया निदान आणि उपचारांसाठी पात्र आरोग्य सेवा व्यावसायिकाचा सल्ला घ्या."
        )
    else:
        disclaimer_text = (
            "\n\n[Disclaimer] I can help explain findings and what they might indicate, but I cannot provide a definitive diagnosis or prescribe medications. "
            "Please consult a qualified healthcare professional for diagnosis and treatment."
        )
    
    text_lower = text.lower()
    for p in prohibited_patterns:
        if p in text_lower:
            logger.warning(f"Guardrail triggered for pattern: {p}")
            
            # Check if disclaimer already exists in the text
            disclaimer_indicators = [
                'consult a', 'i cannot provide a definitive diagnosis',
                'परामर्श लें', 'निदान प्रदान नहीं कर सकता'
            ]
            if any(indicator in text_lower for indicator in disclaimer_indicators):
                return text
            return text + disclaimer_text
    return text


def generate_summary_from_text(text: str, language: str = 'en') -> str:
    """Generate a concise summary using Ollama chat model."""
    logger.info(f"Generating summary via Ollama (text length={len(text)})")
    try:
        if language in ['hi', 'Hindi']:
            target_lang_name = "Hindi"
        elif language in ['mr', 'Marathi']:
            target_lang_name = "Marathi"
        else:
            target_lang_name = "English"
        system_prompt = (
            f"You are a concise, professional medical assistant. Summarize the following extracted text from a medical report in {target_lang_name}. "
            f"You MUST respond entirely in {target_lang_name}. "
            "Do not diagnose or prescribe. Keep it clear and patient-friendly. Aim for 2-4 short sentences suitable for a patient."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.0, "num_predict": 200}
        )
        summary = resp.get('message', {}).get('content', '')
        
        # Translation Safety Net for Devanagari languages
        if language in ['hi', 'Hindi', 'mr', 'Marathi']:
            # Check if response is mostly English
            import re
            target_lang_code = 'mr' if language in ['mr', 'Marathi'] else 'hi'
            english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', summary))
            total_words = len(summary.split())
            if total_words > 0 and english_words > total_words * 0.3:
                logger.info(f"LLM responded in English for {target_lang_name} request, translating...")
                summary = translation_service.translate_to_target(summary, target_lang=target_lang_code)

        return _guardrail_validator(summary, language)
    except Exception as e:
        logger.error(f"Ollama summarization failed: {e}", exc_info=True)
        # Fallback: return short snippet
        fallback = (text.strip().replace('\n', ' ')[:300] + '...')
        if language in ['hi', 'Hindi']:
            fallback = translation_service.translate_to_target(fallback, target_lang='hi')
        elif language in ['mr', 'Marathi']:
            fallback = translation_service.translate_to_target(fallback, target_lang='mr')
        return fallback


def generate_summary_from_image(image_path: str, language: str = 'en') -> str:
    """
    Analyze medical image directly using MedGemma VLM (Vision-Language Model).
    MedGemma can process images directly without needing text extraction.
    """
    logger.info(f"Analyzing medical image directly with MedGemma VLM: {image_path}")
    try:
        if language in ['hi', 'Hindi']:
            target_lang_name = "Hindi"
        elif language in ['mr', 'Marathi']:
            target_lang_name = "Marathi"
        else:
            target_lang_name = "English"
        system_prompt = (
            "You are a medical assistant specialized in analyzing medical images. "
            f"Describe what you see in this medical image in clear, professional {target_lang_name}. "
            f"Provide your response entirely in {target_lang_name}. "
            "Do NOT diagnose or prescribe. Focus on describing visible findings and what they typically indicate. "
            "Always recommend consulting with a healthcare professional for proper diagnosis."
        )

        # Use Ollama's vision capability to analyze the image directly
        messages = [
            {
                "role": "user",
                "content": "Analyze this medical image and describe findings. What can you see?",
                "images": [image_path]  # Pass image directly to model
            }
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model=settings.MODEL_NAME,  # Use configured MedGemma model
            messages=messages,
            options={
                "temperature": 0.3,  # Lower temperature for more focused medical analysis
                "num_predict": 300
            }
        )

        analysis = resp.get('message', {}).get('content', '')
        logger.info(f"MedGemma VLM analysis completed: {analysis[:100]}...")

        # Translation Safety Net for Devanagari
        if language in ['hi', 'Hindi', 'mr', 'Marathi']:
            import re
            target_lang_code = 'mr' if language in ['mr', 'Marathi'] else 'hi'
            english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', analysis))
            total_words = len(analysis.split())
            if total_words > 0 and english_words > total_words * 0.3:
                logger.info(f"VLM responded in English for {target_lang_name} request, translating...")
                analysis = translation_service.translate_to_target(analysis, target_lang=target_lang_code)

        # Apply guardrails to the response
        return _guardrail_validator(analysis, language)

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
    """Generate a patient-facing summary in clear, readable format.

    Goals:
      - Plain language explanation of the key findings.
      - Brief "What this might mean" (non-diagnostic, generic context).
      - 1 simple lifestyle / monitoring suggestion.
      - Reminder to consult a healthcare professional.
    Constraints:
      - No definitive diagnoses or medication instructions.
      - Avoid jargon unless briefly explained in parentheses.
    """
    logger.info(f"Generating patient summary (expanded) via Ollama (text length={len(text)})")
    if language in ['hi', 'Hindi']:
        target_lang_name = "Hindi"
    elif language in ['mr', 'Marathi']:
        target_lang_name = "Marathi"
    else:
        target_lang_name = "English"
    try:
        if target_lang_name == "Hindi":
            system_prompt = (
                "You are a medical assistant writing a friendly, easy-to-read summary for a patient in Hindi.\n"
                "You MUST respond entirely in Hindi language (Devanagari script).\n\n"
                "**Instructions:**\n"
                "1. Start with a clear heading like '📋 आपके परीक्षण परिणामों का सारांश'\n"
                "2. रिपोर्ट से मुख्य परीक्षण नाम और मान निकालें\n"
                "3. सरल शब्दों में समझाएं कि परीक्षण क्या मापता है\n"
                "4. बताएं कि परिणाम सामान्य सीमा के भीतर हैं या नहीं\n"
                "5. यह क्या संकेत दे सकता है, इसका संक्षिप्त विवरण दें\n"
                "6. एक सरल स्वास्थ्य टिप दें (लेकिन कोई दवा नहीं)\n"
                "7. अपने डॉक्टर से चर्चा करने के लिए अनुस्मारक के साथ समाप्त करें\n\n"
                "**Format Requirements:**\n"
                "- Use simple Hindi, avoid complex Sanskritized words\n"
                "- Use bullet points (•)\n"
                "- NEVER diagnose or prescribe medications\n\n"
                "**Example Format:**\n"
                "📋 आपके परीक्षण परिणामों का सारांश\n\n"
                "परीक्षण का नाम: [रिपोर्ट से]\n"
                "आपका परिणाम: [मान] [इकाई]\n"
                "सामान्य सीमा: [संदर्भ सीमा]\n\n"
                "इसका क्या मतलब है:\n"
                "[सरल भाषा में विवरण]\n\n"
                "आपके परिणाम:\n"
                "✓ आपके स्तर सामान्य सीमा के भीतर हैं / ⚠️ आपके स्तर सामान्य सीमा से [अधिक/कम] हैं\n\n"
                "क्या जानना है:\n"
                "[संक्षिप्त विवरण]\n\n"
                "अगले कदम:\n"
                "• [सरल टिप]\n"
                "• व्यक्तिगत सलाह के लिए अपने डॉक्टर से बात करें"
            )
        elif target_lang_name == "Marathi":
            system_prompt = (
                "You are a medical assistant writing a friendly, easy-to-read summary for a patient in Marathi.\n"
                "You MUST respond entirely in Marathi language (Devanagari script).\n\n"
                "**Instructions:**\n"
                "1. Start with a clear heading like '📋 तुमच्या चाचणी निकालांचा सारांश'\n"
                "2. Extract key test names and values from the report\n"
                "3. Explain what the test measures in simple Marathi\n"
                "4. State if results are normal or not\n"
                "5. Provide a simple health tip and a reminder to see a doctor\n\n"
                "Format as a clear bulleted list."
            )
        else:
            system_prompt = (
                f"You are a medical assistant writing a friendly, easy-to-read summary for a patient in {target_lang_name}.\n\n"
                "**Instructions:**\n"
                "1. Start with a clear heading like '📋 Your Test Results Summary'\n"
                "2. Extract the key test name and values from the report\n"
                "3. Explain what the test measures in simple terms\n"
                "4. State if the results are within normal range or not (in plain language)\n"
                "5. Provide a brief, general explanation of what this might indicate\n"
                "6. Give one simple health tip or next step (but NO medications)\n"
                "7. End with a reminder to discuss with their healthcare provider\n\n"
                "**Format Requirements:**\n"
                "- Use short paragraphs with line breaks for readability\n"
                "- Use bullet points (•) for lists\n"
                "- Use emojis sparingly for visual appeal (✓ for normal, ⚠️ for attention needed)\n"
                "- Avoid medical jargon or explain it in parentheses\n"
                "- Be reassuring but honest\n"
                "- NEVER diagnose or prescribe medications\n\n"
                "**Example Format:**\n"
                "📋 Your Test Results Summary\n\n"
                "Test Name: [Extract from report]\n"
                "Your Result: [Value] [Unit]\n"
                "Normal Range: [Reference range]\n\n"
                "What This Means:\n"
                "[Plain language explanation of what this test measures]\n\n"
                "Your Results:\n"
                "✓ Your levels are within the normal range / ⚠️ Your levels are [higher/lower] than the normal range\n\n"
                "What to Know:\n"
                "[Brief, non-diagnostic context about what this generally indicates]\n\n"
                "Next Steps:\n"
                "• [Simple health tip or monitoring suggestion]\n"
                "• Discuss these results with your healthcare provider for personalized advice\n\n"
                "Remember: This is a simplified summary. Your doctor can provide a complete interpretation and personalized recommendations."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a patient-friendly summary of this medical report:\n\n{text}"}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.2, "num_predict": 500}  # Allow more length for structured format
        )

        summary = resp.get('message', {}).get('content', '')
        
        # Translation Safety Net for Devanagari
        if language in ['hi', 'Hindi', 'mr', 'Marathi']:
            import re
            target_lang_code = 'mr' if language in ['mr', 'Marathi'] else 'hi'
            english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', summary))
            total_words = len(summary.split())
            if total_words > 0 and english_words > total_words * 0.3:
                logger.info(f"LLM patient summary in English, translating to {target_lang_name}...")
                summary = translation_service.translate_to_target(summary, target_lang=target_lang_code)

        return _guardrail_validator(summary.strip(), language)
    except Exception as e:
        logger.error(f"Expanded patient summary generation failed: {e}", exc_info=True)
        return generate_summary_from_text(text, language)


def generate_detailed_report_from_text(text: str, language: str = 'English') -> str:
    """Generate an expanded structured clinician-facing report with deeper comprehension.

    Sections (in this order):
      1. Report Summary – concise overview.
      2. Key Results – bullet list; include raw values & reference ranges if present in source.
      3. Interpretive Context / Pathophysiology – explain patterns & possible physiological significance WITHOUT making a diagnosis.
      4. Clinical Significance & Risk Stratification – categorize findings (e.g., normal / borderline / notable) when safely inferable.
      5. Limitations / Data Quality – note missing data, ambiguity, OCR issues.
      6. Recommended Follow-Up – non-diagnostic next steps (monitoring, generic further evaluation) avoiding prescriptions.
      7. Education Points – brief clarifications of technical terms.

    Requirements:
      - Avoid definitive diagnostic statements or medication advice.
      - Prefer concise bullet points over long prose.
      - If no numeric values found, still produce Key Results with qualitative findings.
      - If reference ranges appear, format: VALUE (Ref: X–Y).
    """
    logger.info(f"Generating expanded clinician report via Ollama (text length={len(text)})")
    if language in ['hi', 'Hindi']:
        target_lang_name = "Hindi"
    elif language in ['mr', 'Marathi']:
        target_lang_name = "Marathi"
    else:
        target_lang_name = "English"
    try:
        system_prompt = (
            f"You are an advanced clinical decision support assistant creating a comprehensive, structured medical report for healthcare professionals in {target_lang_name}.\n\n"
            f"You MUST respond entirely in {target_lang_name}. "
            
            "**CRITICAL INSTRUCTIONS:**\n"
            "You MUST create a detailed, well-structured report using the EXACT format and sections below. Each section is MANDATORY.\n\n"
            
            "**REQUIRED REPORT STRUCTURE:**\n\n"
            
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 CLINICAL ANALYSIS REPORT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "## 1️⃣ EXECUTIVE SUMMARY\n"
            "[Provide a 2-3 sentence high-level overview of the report type, key findings, and overall clinical picture]\n\n"
            
            "## 2️⃣ KEY LABORATORY/DIAGNOSTIC RESULTS\n"
            "[Extract and present ALL test values in structured format. For EACH result include:]\n"
            "• **Test Name:** [Full name]\n"
            "  - Result: [Numeric value] [Unit]\n"
            "  - Reference Range: [Lower limit - Upper limit] [Unit]\n"
            "  - Status: [Normal ✓ / Elevated ↑ / Decreased ↓ / Critical ⚠️]\n"
            "  - Deviation: [If abnormal, calculate % above/below reference range]\n\n"
            "[If multiple tests, list each one separately with clear visual separation]\n\n"
            
            "## 3️⃣ INTERPRETIVE CONTEXT & PATHOPHYSIOLOGY\n"
            "[Provide detailed scientific context WITHOUT diagnosing:]\n"
            "• **Biological Significance:**\n"
            "  - What does this marker/parameter measure at the molecular/cellular level?\n"
            "  - What physiological processes does it reflect?\n"
            "  - What mechanisms could cause elevation/reduction?\n\n"
            "• **Clinical Correlations:**\n"
            "  - What clinical conditions are COMMONLY associated with these patterns?\n"
            "  - What are the differential considerations? (List 3-5 possibilities)\n"
            "  - Are there any patterns across multiple markers?\n\n"
            "• **Contextual Factors:**\n"
            "  - Age/demographic considerations if relevant\n"
            "  - Temporal trends if multiple values present\n"
            "  - Potential confounding factors (medications, diet, timing)\n\n"
            
            "## 4️⃣ CLINICAL SIGNIFICANCE & RISK STRATIFICATION\n"
            "[Categorize findings based on clinical importance:]\n\n"
            "**🟢 Normal/Low Risk Findings:**\n"
            "• [List parameters within expected ranges]\n"
            "• Clinical Implication: [Brief explanation]\n\n"
            
            "**🟡 Borderline/Moderate Risk Findings:**\n"
            "• [List parameters slightly outside reference but not critical]\n"
            "• Clinical Implication: [Explain significance and monitoring needs]\n\n"
            
            "**🔴 Abnormal/High Risk Findings:**\n"
            "• [List significantly abnormal values]\n"
            "• Clinical Implication: [Explain urgency and potential clinical impact]\n"
            "• Action Threshold: [Indicate if values cross critical decision points]\n\n"
            
            "**⚡ Critical/Immediate Attention:**\n"
            "• [List any life-threatening values if present]\n"
            "• Immediate Considerations: [What requires urgent evaluation]\n\n"
            
            "## 5️⃣ DATA QUALITY & LIMITATIONS\n"
            "[Critically assess the report quality:]\n"
            "• **Completeness:** [Are all expected values present? Any missing tests?]\n"
            "• **Methodology:** [Test method noted? Any limitations of technique?]\n"
            "• **Specimen Quality:** [Any collection/handling issues noted?]\n"
            "• **OCR/Data Extraction:** [Any unclear values or potential transcription errors?]\n"
            "• **Uncertainty Factors:** [What clinical context is missing?]\n\n"
            
            "## 6️⃣ RECOMMENDED FOLLOW-UP ACTIONS\n"
            "[Evidence-based next steps WITHOUT prescribing:]\n\n"
            "**Immediate Actions (0-24 hours):**\n"
            "• [List any urgent evaluations needed]\n\n"
            
            "**Short-term Follow-up (1-4 weeks):**\n"
            "• [Recommended repeat testing or additional investigations]\n"
            "• [Clinical correlation needed with symptoms/history]\n\n"
            
            "**Long-term Monitoring:**\n"
            "• [Ongoing surveillance recommendations]\n"
            "• [Frequency of repeat testing based on current findings]\n\n"
            
            "**Additional Diagnostic Workup (if indicated):**\n"
            "• [Complementary tests that would provide additional context]\n"
            "• [Imaging or specialized studies to consider]\n\n"
            
            "**Patient Education/Lifestyle:**\n"
            "• [General health recommendations relevant to findings]\n"
            "• [Monitoring guidance for patient]\n\n"
            
            "## 7️⃣ CLINICAL PEARLS & EDUCATION POINTS\n"
            "[Provide educational context for clinicians:]\n\n"
            "**Technical Terminology:**\n"
            "• [Define any complex medical terms with brief explanations]\n\n"
            
            "**Clinical Pearls:**\n"
            "• [Important practice points or common pitfalls to avoid]\n"
            "• [Evidence-based insights related to these findings]\n\n"
            
            "**Reference Standards:**\n"
            "• [Note if reference ranges are population-specific]\n"
            "• [Mention any recent guideline updates relevant to interpretation]\n\n"
            
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "**DISCLAIMER:** This analysis is for informational and educational purposes only. It does NOT constitute a diagnosis, treatment recommendation, or replace clinical judgment. All findings must be interpreted in the context of complete patient history, physical examination, and additional clinical data. Consult appropriate specialists as needed.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "**FORMATTING REQUIREMENTS:**\n"
            "- Use markdown formatting with headers (##), bold (**), and bullet points (•)\n"
            "- Use emojis for visual hierarchy (numbers, symbols, indicators)\n"
            "- Include actual numeric values with units\n"
            "- Calculate deviations from reference ranges when abnormal\n"
            "- Use clinical terminology appropriate for healthcare professionals\n"
            "- Be comprehensive but organized - use subsections liberally\n"
            "- NEVER provide definitive diagnoses or medication prescriptions\n"
            "- Always acknowledge uncertainty and need for clinical correlation\n"
        )

        user_prompt = (
            "Generate a comprehensive clinical analysis report from the following medical document.\n"
            "Follow the EXACT structure provided in the system prompt. Each section MUST be present and detailed.\n\n"
            "---BEGIN MEDICAL DOCUMENT---\n" + text + "\n---END MEDICAL DOCUMENT---\n\n"
            "Create the full structured report now, ensuring ALL 7 sections are thoroughly completed:"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        from app.services.ollama_client import chat_with_retries
        resp = chat_with_retries(
            model=settings.MODEL_NAME,
            messages=messages,
            options={"temperature": 0.1, "num_predict": 2000}  # Much longer for comprehensive report
        )

        report = resp.get('message', {}).get('content', '')
        
        # Translation Safety Net for Devanagari
        if language in ['hi', 'Hindi', 'mr', 'Marathi']:
            import re
            target_lang_code = 'mr' if language in ['mr', 'Marathi'] else 'hi'
            english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', report))
            total_words = len(report.split())
            if total_words > 0 and english_words > total_words * 0.3:
                logger.info(f"LLM clinician report in English, translating to {target_lang_name}...")
                report = translation_service.translate_to_target(report, target_lang=target_lang_code)

        return _guardrail_validator(report, language)
    except Exception as e:
        logger.error(f"Expanded clinician report generation failed: {e}", exc_info=True)
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
            model=settings.MODEL_NAME,
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
