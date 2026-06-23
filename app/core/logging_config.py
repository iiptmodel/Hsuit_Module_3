"""
Centralized logging configuration for the Med Analyzer application.

This module provides a single ``setup_logging()`` entry point used by the web
app (``app/main.py``), CLI scripts (``scripts/*.py``), and — implicitly — every
service module. Configuring logging in one place keeps console output
consistent and colorized, and keeps third-party libraries from flooding the
terminal.

Design notes:
- Only *entry points* call ``setup_logging()``. Library/service modules just do
  ``logging.getLogger(__name__)`` and inherit the root configuration. This is
  the standard Python logging pattern.
- Color is emitted only when stdout is an interactive terminal. When output is
  piped or redirected to a file, colors are dropped automatically so logs stay
  grep-friendly. Override with ``FORCE_COLOR=1`` or disable with ``NO_COLOR=1``.

Environment variables:
- LOG_LEVEL:   DEBUG | INFO | WARNING | ERROR | CRITICAL  (default: INFO)
- NO_COLOR:    Disable ANSI colors entirely.
- FORCE_COLOR: Force ANSI colors even when not a TTY.
"""

import contextvars
import logging
import os
import sys
import warnings

# ============================================================================
# REQUEST TRACING
# ============================================================================

# Set by the HTTP middleware in main.py; surfaces in every log line as a short
# "(req=xxxxxxxx)" tag so logs from a single request can be correlated.
REQUEST_ID = contextvars.ContextVar("request_id", default=None)

# ============================================================================
# COLORS
# ============================================================================

_RESET = "\033[0m"
_DIM = "\033[2m"
_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",      # cyan
    logging.INFO: "\033[32m",       # green
    logging.WARNING: "\033[33m",    # yellow
    logging.ERROR: "\033[31m",      # red
    logging.CRITICAL: "\033[97;41m",  # white on red
}

# Third-party loggers that emit noisy INFO/DEBUG output during model loads,
# downloads, and requests. Pinned to WARNING so only real problems show.
_NOISY_LOGGERS = (
    "urllib3", "watchfiles", "PIL", "rapidocr", "torch",
    "huggingface_hub", "transformers", "filelock", "asyncio",
    "matplotlib", "numba", "fontTools", "httpx", "httpcore",
)

_configured = False


# ============================================================================
# FILTERS
# ============================================================================

class _RecordEnricher(logging.Filter):
    """Adds derived fields used by the formatter to every record.

    - ``short_name``: last component of a dotted logger name
      (``app.services.tts_service`` -> ``tts_service``).
    - ``req_tag``: ``" (req=abcd1234)"`` when a request id is set, else ``""``.
    """

    def filter(self, record):
        record.short_name = record.name.rsplit(".", 1)[-1]
        rid = REQUEST_ID.get()
        record.req_tag = f" (req={rid[:8]})" if rid else ""
        return True


# ============================================================================
# FORMATTER
# ============================================================================

class ColorFormatter(logging.Formatter):
    """Formats records with a color-coded, fixed-width level and dim metadata.

    Padding is applied *before* the ANSI color codes so column alignment is
    preserved (the invisible escape codes would otherwise break ``%-5s`` width).
    """

    def __init__(self, use_color=True):
        if use_color:
            fmt = (
                f"{_DIM}%(asctime)s{_RESET} %(levelname)s "
                f"{_DIM}[%(short_name)s]{_RESET}%(req_tag)s %(message)s"
            )
        else:
            fmt = "%(asctime)s %(levelname)s [%(short_name)s]%(req_tag)s %(message)s"
        super().__init__(fmt, datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        original_levelname = record.levelname
        padded = f"{original_levelname:<5}"
        if self.use_color:
            color = _LEVEL_COLORS.get(record.levelno, "")
            record.levelname = f"{color}{padded}{_RESET}" if color else padded
        else:
            record.levelname = padded
        try:
            return super().format(record)
        finally:
            # Restore so other handlers / repeated formatting see the original.
            record.levelname = original_levelname


# ============================================================================
# SETUP
# ============================================================================

def _supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _quiet_noisy_warnings():
    """Silence known-benign warnings that clutter startup/model loads."""
    warnings.filterwarnings("ignore", message=r".*dropout option adds dropout.*")
    warnings.filterwarnings("ignore", message=r".*weight_norm.*is deprecated.*")
    warnings.filterwarnings("ignore", category=FutureWarning, module=r"torch.*")
    # Avoid the noisy tokenizers fork/parallelism warning.
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def setup_logging(level=None, *, force=False):
    """Configure root logging once; safe to call repeatedly.

    Args:
        level: Log level name (e.g. "INFO"). Falls back to the ``LOG_LEVEL``
            environment variable, then "INFO". Read from the environment (not
            app settings) to avoid an import cycle with ``app.core.config``.
        force: Rebuild handlers even if logging was already configured.

    Returns:
        The configured root logger.
    """
    global _configured

    level_name = (level or os.environ.get("LOG_LEVEL") or "INFO").upper()
    level_no = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()

    # Already configured: just allow the level to be (re)applied and return.
    if _configured and not force:
        root.setLevel(level_no)
        return root

    # Ensure the console stream can emit our box-drawing chars / emoji. On
    # Windows the default code page is often cp1252, which raises
    # UnicodeEncodeError on these; force UTF-8 and degrade gracefully if a
    # character still can't be encoded.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    use_color = _supports_color()
    if use_color and sys.platform == "win32":
        # Enable ANSI handling on legacy Windows consoles.
        try:
            import colorama
            colorama.just_fix_windows_console()
        except Exception:
            pass

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_RecordEnricher())
    handler.setFormatter(ColorFormatter(use_color=use_color))

    # Replace any existing handlers to avoid duplicate lines.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level_no)

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    # Route warnings.warn(...) through logging so they share the format.
    logging.captureWarnings(True)
    _quiet_noisy_warnings()

    _configured = True
    return root


def banner(logger, title, char="─", width=64):
    """Log a titled separator block for clear section boundaries."""
    line = char * width
    logger.info(line)
    logger.info(title)
    logger.info(line)
