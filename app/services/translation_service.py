import logging

logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    logger.warning("deep-translator not installed — translation will be unavailable")

# Map our language names to Google Translate language codes
_LANG_CODES = {
    'hindi': 'hi',
    'marathi': 'mr',
    'english': 'en',
}

_MAX_CHUNK = 4500  # Google Translate free API limit


def _translate(text: str, target: str) -> str:
    """Translate text (assumed English) to target language code. Returns original on failure."""
    if not _AVAILABLE or not text or not text.strip():
        return text
    try:
        if len(text) <= _MAX_CHUNK:
            return GoogleTranslator(source='en', target=target).translate(text)
        # Split long text on paragraph boundaries to stay within limits
        parts = [text[i:i + _MAX_CHUNK] for i in range(0, len(text), _MAX_CHUNK)]
        return ' '.join(
            GoogleTranslator(source='en', target=target).translate(p) for p in parts
        )
    except Exception as e:
        logger.error(f"Translation to '{target}' failed: {e}")
        return text


def maybe_translate(text: str, language: str) -> str:
    """Translate text to the requested language if non-English; return unchanged otherwise."""
    code = _LANG_CODES.get(language.lower())
    if not code or code == 'en':
        return text
    return _translate(text, code)
