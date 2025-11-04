"""Text processing utilities for the medical analyzer."""

import re
from typing import Optional


def sanitize_text(text: str) -> str:
    """Sanitize and clean text content for processing.

    Args:
        text: Raw text content to sanitize

    Returns:
        Cleaned text content
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text


def estimate_token_count(text: str) -> int:
    """Estimate the number of tokens in a text string.

    This is a rough approximation based on word count and punctuation.
    Actual tokenization may vary depending on the model.

    Args:
        text: Text to estimate token count for

    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0

    # Split on whitespace and punctuation
    words = re.findall(r'\w+|[^\w\s]', text)

    # Rough estimate: 1 token per word/punctuation, with some overhead
    return len(words)
