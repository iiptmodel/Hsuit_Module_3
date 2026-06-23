import asyncio
import os

# Must be set before importing app to suppress Ollama requirement at startup
os.environ.setdefault("PRELOAD_MODELS", "0")
os.environ.setdefault("REQUIRE_OLLAMA", "0")
os.environ.setdefault("RUN_MIGRATIONS", "0")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import models
from app.db.database import Base
from app.api import deps
import app.services.chat_service as chat_service
import app.services.tts_service as tts_service


def test_session_language_persists(monkeypatch):
    """Language sent with a message is saved on the session and returned."""
    # Setup in-memory SQLite for tests (StaticPool keeps the same connection
    # across threads so the FastAPI threadpool and test share the same DB)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db

    # Mock the streaming generator so the endpoint completes without Ollama
    async def fake_stream(user_message, image_path=None, language="English"):
        yield "OK"

    monkeypatch.setattr(chat_service, "generate_chat_response_streaming", fake_stream)

    # Mock TTS to be a no-op
    monkeypatch.setattr(tts_service, "generate_speech", lambda *a, **k: None)

    # Use 'with' so the lifespan runs and routes get registered
    with TestClient(app) as client:
        # Create session
        sess = client.post("/api/v1/chat/sessions", json={"title": "Test"}).json()
        sid = sess["id"]

        # Send a message in Hindi
        resp = client.post(
            f"/api/v1/chat/sessions/{sid}/messages",
            data={"content": "नमस्ते", "audience": "patient", "language": "Hindi"},
        )
        assert resp.status_code == 200

        # Fetch session and assert language is saved
        sess_resp = client.get(f"/api/v1/chat/sessions/{sid}").json()
        assert sess_resp["language"] == "Hindi"

    # Clean up dependency override
    app.dependency_overrides.clear()
