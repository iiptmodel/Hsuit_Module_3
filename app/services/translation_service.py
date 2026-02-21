import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Try Google Translate first (best for Hindi)
try:
    from googletrans import Translator
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

class TranslationService:
    """Reliable translation service with fallback."""
    
    def __init__(self):
        self._translator = None
        if GOOGLE_TRANSLATE_AVAILABLE:
            try:
                self._translator = Translator()
                # Test translation
                test = self._translator.translate("hello", dest='hi')
                logger.info("Google Translate initialized successfully")
            except Exception as e:
                logger.warning(f"Google Translate init failed: {e}")
                self._translator = None
    
    def detect_language(self, text: str) -> str:
        """Detect language - returns 'en', 'hi', or 'mr'."""
        if not text or len(text.strip()) < 3:
            return 'en'
        
        # If Google Translate is available, it's very reliable for detection
        if self._translator:
            try:
                result = self._translator.detect(text[:500])
                if result and result.lang in ['hi', 'mr']:
                    return result.lang
                elif result and result.lang == 'en':
                    # Still do a quick Devanagari check in case detector missed it
                    if re.search(r'[\u0900-\u097F]', text):
                        # Heuristic: Marathi uses 'ळ' (U+0933), Hindi doesn't
                        if '\u0933' in text:
                            return 'mr'
                        return 'hi'
                    return 'en'
            except:
                pass
        
        # Fallback to Regex and Keyword Heuristics
        if re.search(r'[\u0900-\u097F]', text):
            # 1. Direct character check: ळ (u0933) is purely Marathi
            if '\u0933' in text:
                return 'mr'
            
            # 2. Common suffix/keyword checks
            text_lower = text.lower()
            # Marathi markers: आहे (is), आणि (and), किंवा (or), हे (this), चा/ची/चे (of), आपण (we)
            marathi_markers = ['आहे', 'आणि', 'किंवा', 'बदल', 'झाला', ' आहे', ' आणि', ' किंवा', ' चा ', ' ची ', ' चे ', ' आपण ', ' पण ', ' म्हणून ']
            # Hindi markers: है (is), और (and), लेकिन (but), यह (this), का/की/के (of), हम (we)
            hindi_markers = [' है', 'और', 'क्या', 'लेकिन', 'किया', ' है ', ' और ', ' क्या ', ' लेकिन ', ' किया ', ' का ', ' की ', ' के ', ' यह ', ' हम ', ' आप ']
            
            m_count = sum(1 for m in marathi_markers if m in text_lower)
            h_count = sum(1 for h in hindi_markers if h in text_lower)
            
            if m_count > h_count:
                return 'mr'
            return 'hi'
        
        return 'en'
    
    def translate_to_english(self, text: str) -> str:
        """Translate Hindi text to English."""
        if not text or not text.strip():
            return text
        
        # If already English, return as-is
        if not re.search(r'[\u0900-\u097F]', text):
            return text
        
        if self._translator:
            try:
                result = self._translator.translate(text, dest='en', src='hi')
                return result.text if result else text
            except Exception as e:
                logger.error(f"Translation to English failed: {e}")
        
        return text
    
    def translate_to_target(self, text: str, target_lang: str = 'hi') -> str:
        """Translate English text to a target language (hi, mr, etc.)."""
        if not text or not text.strip():
            return text
        
        # If already has target script, might be already translated
        # Devanagari check works for both Hindi and Marathi
        if re.search(r'[\u0900-\u097F]', text) and len(re.findall(r'[\u0900-\u097F]', text)) > len(text) * 0.3:
            return text
        
        if self._translator:
            try:
                # Split long text to avoid API limits
                max_len = 4000
                if len(text) > max_len:
                    parts = [text[i:i+max_len] for i in range(0, len(text), max_len)]
                    translated_parts = []
                    for part in parts:
                        result = self._translator.translate(part, dest=target_lang, src='en')
                        translated_parts.append(result.text if result else part)
                    return ' '.join(translated_parts)
                else:
                    result = self._translator.translate(text, dest=target_lang, src='en')
                    return result.text if result else text
            except Exception as e:
                logger.error(f"Translation to {target_lang} failed: {e}")
        
        return text  # Fallback: return original

# Global instance
translation_service = TranslationService()