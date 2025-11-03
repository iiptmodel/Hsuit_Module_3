from fastapi import APIRouter
from app.api.endpoints import reports, chat
from app.api import ws

api_router = APIRouter()
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
# WebSocket routes for chat realtime features
api_router.include_router(ws.router, prefix="/chat", tags=["Chat Websockets"])

