from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services import tts_service

router = APIRouter()

@router.get('/tts', summary='TTS health check')
def tts_health_check():
    """Returns the readiness of the Kokoro TTS pipeline."""
    ready = tts_service.is_pipeline_ready()
    status = 'ready' if ready else 'unavailable'
    return JSONResponse({"service": "kokoro_tts", "status": status})


@router.get('/ollama', summary='Ollama health check')
def ollama_health_check():
    """Checks whether an Ollama server is reachable from this process."""
    try:
        from app.services.ollama_client import is_ollama_reachable
        ready = is_ollama_reachable()
    except Exception:
        ready = False
    status = 'ready' if ready else 'unavailable'
    return JSONResponse({"service": "ollama", "status": status})
