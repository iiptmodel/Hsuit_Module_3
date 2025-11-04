import time
import logging
import os
from typing import Any, Dict

import ollama
from requests import exceptions as req_exceptions

logger = logging.getLogger(__name__)


def _get_ollama_base_url() -> str:
    # The ollama client may be configured by environment; default to localhost:11434
    return os.environ.get('OLLAMA_HOST') or os.environ.get('OLLAMA_URL') or 'http://localhost:11434'


def chat_with_retries(model: str, messages: Any, options: Dict[str, Any] = None, retries: int = 3, backoff: float = 0.6):
    """Call ollama.chat with simple retry logic for ConnectionError.

    Retries on ConnectionError raised by the ollama client. Exponential backoff is applied.
    """
    if options is None:
        options = {}

    attempt = 0
    while True:
        try:
            return ollama.chat(model=model, messages=messages, options=options)
        except Exception as e:
            # Detect connection issues conservatively by message or type
            msg = str(e).lower()
            is_connection = 'failed to connect' in msg or 'connectionerror' in msg or isinstance(e, req_exceptions.ConnectionError)
            attempt += 1
            if not is_connection or attempt > retries:
                logger.exception('Ollama chat failed (no more retries): %s', e)
                raise
            sleep = backoff * (2 ** (attempt - 1))
            logger.warning('Ollama chat connection failed, retrying in %.2fs (attempt %d/%d): %s', sleep, attempt, retries, e)
            time.sleep(sleep)


def is_ollama_reachable(timeout: float = 0.8) -> bool:
    """Quick TCP/HTTP probe to check if an Ollama server is reachable.

    Uses the configured OLLAMA_HOST/OLLAMA_URL or defaults to http://localhost:11434.
    """
    base = _get_ollama_base_url().rstrip('/')
    try:
        # Use requests to probe the base URL root
        import requests
        resp = requests.get(base, timeout=timeout)
        # Any HTTP response indicates the server is reachable
        return True
    except Exception:
        return False
