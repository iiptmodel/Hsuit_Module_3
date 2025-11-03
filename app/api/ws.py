from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Map session_id -> set of WebSocket
        self.active: Dict[int, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, session_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            conns = self.active.get(session_id) or set()
            conns.add(websocket)
            self.active[session_id] = conns
        logger.info(f"WebSocket connected for session {session_id} (total={len(self.active[session_id])})")

    async def disconnect(self, session_id: int, websocket: WebSocket):
        async with self.lock:
            conns = self.active.get(session_id)
            if not conns:
                return
            if websocket in conns:
                conns.remove(websocket)
            if len(conns) == 0:
                self.active.pop(session_id, None)
            else:
                self.active[session_id] = conns
        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_json_to_session(self, session_id: int, data: dict):
        """Send JSON payload to all connected websockets for a session."""
        conns = self.active.get(session_id)
        if not conns:
            logger.debug(f"No websocket connections for session {session_id}")
            return
        to_remove = []
        for ws in list(conns):
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send websocket message to session {session_id}: {e}")
                to_remove.append(ws)
        if to_remove:
            async with self.lock:
                for ws in to_remove:
                    conns.discard(ws)
                if conns:
                    self.active[session_id] = conns
                else:
                    self.active.pop(session_id, None)

manager = ConnectionManager()

@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    try:
        await manager.connect(session_id, websocket)
        # Keep connection open; echo or simple heartbeat handling
        while True:
            try:
                msg = await websocket.receive_text()
                # Clients may send pings; ignore
            except WebSocketDisconnect:
                break
    except Exception as e:
        logger.error(f"Websocket connection error for session {session_id}: {e}")
    finally:
        await manager.disconnect(session_id, websocket)
