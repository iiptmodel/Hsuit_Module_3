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
