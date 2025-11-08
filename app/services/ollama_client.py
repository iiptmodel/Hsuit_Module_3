"""
Ollama Client Wrapper with Retry Logic

This module provides a resilient interface to the Ollama LLM server with:
- Automatic retry on connection failures
- Exponential backoff
- Health check functionality

Environment Variables:
- OLLAMA_HOST: Ollama server URL (default: http://localhost:11434)
- OLLAMA_URL: Alternative to OLLAMA_HOST
"""

import time
import logging
import os
from typing import Any, Dict

import ollama
from requests import exceptions as req_exceptions

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

def _get_ollama_base_url() -> str:
    """
    Get Ollama server URL from environment or use default.
    
    Returns:
        Ollama server base URL
    """
    return (
        os.environ.get('OLLAMA_HOST') or 
        os.environ.get('OLLAMA_URL') or 
        'http://localhost:11434'
    )


# ============================================================================
# OLLAMA CHAT API WITH RETRY
# ============================================================================

def chat_with_retries(
    model: str,
    messages: Any,
    options: Dict[str, Any] = None,
    retries: int = 3,
    backoff: float = 0.6
):
    """
    Call ollama.chat with automatic retry logic for connection errors.
    
    Features:
    - Exponential backoff on connection failures
    - Configurable retry attempts
    - Detailed error logging
    
    Args:
        model: Ollama model name (e.g., 'medgemma', 'llama2')
        messages: List of message dictionaries with 'role' and 'content'
        options: Optional parameters for the model (temperature, max_tokens, etc.)
        retries: Maximum number of retry attempts (default: 3)
        backoff: Base backoff time in seconds (default: 0.6)
    
    Returns:
        Ollama chat response dictionary
    
    Raises:
        Exception: If all retries are exhausted or non-connection error occurs
    
    Example:
        >>> response = chat_with_retries(
        ...     model='medgemma',
        ...     messages=[{'role': 'user', 'content': 'Hello'}],
        ...     options={'temperature': 0.7}
        ... )
    """
    if options is None:
        options = {}

    attempt = 0
    while True:
        try:
            return ollama.chat(model=model, messages=messages, options=options)
        except Exception as e:
            # Detect connection-related errors
            msg = str(e).lower()
            is_connection = (
                'failed to connect' in msg or 
                'connectionerror' in msg or 
                isinstance(e, req_exceptions.ConnectionError)
            )
            
            attempt += 1
            
            # Give up if not a connection error or out of retries
            if not is_connection or attempt > retries:
                logger.exception('❌ Ollama chat failed (no more retries): %s', e)
                raise
            
            # Calculate exponential backoff
            sleep = backoff * (2 ** (attempt - 1))
            logger.warning(
                '⚠️  Ollama connection failed, retrying in %.2fs (attempt %d/%d): %s',
                sleep, attempt, retries, e
            )
            time.sleep(sleep)


# ============================================================================
# HEALTH CHECK
# ============================================================================

def is_ollama_reachable(timeout: float = 0.8) -> bool:
    """
    Quick TCP/HTTP health check for Ollama server.
    
    Args:
        timeout: Request timeout in seconds (default: 0.8)
    
    Returns:
        True if server responds, False otherwise
    
    Example:
        >>> if is_ollama_reachable():
        ...     print("Ollama server is online")
    """
    base_url = _get_ollama_base_url().rstrip('/')
    
    try:
        import requests
        resp = requests.get(base_url, timeout=timeout)
        # Any HTTP response indicates server is reachable
        logger.debug(f"✅ Ollama server reachable at {base_url}")
        return True
    except Exception as e:
        logger.debug(f"❌ Ollama server unreachable at {base_url}: {e}")
        return False
