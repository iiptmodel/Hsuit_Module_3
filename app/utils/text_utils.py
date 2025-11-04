import re
import logging

logger = logging.getLogger(__name__)

def sanitize_text(text: str) -> str:
    """Sanitize noisy text input by removing repeated special characters and collapsing whitespace.

    This preserves basic punctuation (. , ? ! : ; - / % ( ) ) and removes excessive stars '*' and other non-printable
    or uncommon symbols while keeping the medical content readable.
    """
    if not text:
        logger.debug("sanitize_text: empty input")
        return text

    original_len = len(text)
    logger.debug(f"sanitize_text: processing {original_len} chars")

    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse repeated asterisks and other repeated punctuation sequences into a single space
    text = re.sub(r"\*+", " ", text)
    text = re.sub(r"[~`^<>]{2,}", " ", text)

    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", text)

    # Replace sequences of non-word characters that are not common punctuation with a space
    text = re.sub(r"[^\w\s\.\,\?\!\:\;\-\(\)/%]+", " ", text)

    # Collapse multiple whitespace/newlines
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim
    result = text.strip()
    logger.debug(f"sanitize_text: output {len(result)} chars (reduced by {original_len - len(result)})")
    return result
