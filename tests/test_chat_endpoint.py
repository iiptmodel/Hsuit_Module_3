import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the app does not preload large models during test startup
os.environ.setdefault("PRELOAD_MODELS", "0")

from app.main import app
from app.db import models
from app.db.database import Base

import app.services.chat_service as chat_service
import app.services.tts_service as tts_service


def run_async(gen):
    """Helper to run async generator to completion when needed."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(gen)


def test_create_session_and_send_message(monkeypatch):
    # Setup in-memory SQLite for tests
    # Use shared in-memory SQLite DB across threads (StaticPool) so FastAPI threadpool sessions see tables
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Override DB dependency
    from app.api import deps

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db

    # Ensure tables exist on the test engine (explicit create after override to avoid race with app import)
    models.Base.metadata.create_all(bind=engine)

    # Patch streaming generator to return deterministic tokens
    async def fake_stream(user_message, image_path=None):
        yield "Hello"
        await asyncio.sleep(0)
        yield " world"

    monkeypatch.setattr(chat_service, "generate_chat_response_streaming", fake_stream)

    # Patch TTS to be a no-op
    monkeypatch.setattr(tts_service, "generate_speech", lambda *a, **k: None)

    client = TestClient(app)

    # Create a session
    rv = client.post("/api/v1/chat/sessions", json={"title": "test-session"})
    assert rv.status_code == 200
    session = rv.json()
    assert "id" in session
    session_id = session["id"] if isinstance(session, dict) else session[0]["id"]

    # Send a message (no file)
    multipart = {
        "content": (None, "Please summarize this."),
        "audience": (None, "patient"),
    }
    rv2 = client.post(f"/api/v1/chat/sessions/{session_id}/messages", files=multipart)
    assert rv2.status_code == 200
    msg = rv2.json()
    assert msg["role"] == "assistant"
    assert "Hello" in msg["content"]
