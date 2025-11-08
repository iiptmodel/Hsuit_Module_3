import asyncio
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("PRELOAD_MODELS", "0")

from app.main import app
from app.db import models
from app.db.database import Base
from app.api import deps
import app.services.chat_service as chat_service
import app.services.tts_service as tts_service


def test_basic_text_message_stream(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db

    async def fake_stream(user_message, image_path=None):
        yield "Hello"
        await asyncio.sleep(0)
        yield ", world!"

    monkeypatch.setattr(chat_service, "generate_chat_response_streaming", fake_stream)
    monkeypatch.setattr(tts_service, "generate_speech", lambda *a, **k: None)

    client = TestClient(app)

    # New session
    rv = client.post("/api/v1/chat/sessions", json={"title": "stream-test"})
    assert rv.status_code == 200
    sid = rv.json()["id"]

    rv2 = client.post(f"/api/v1/chat/sessions/{sid}/messages", data={"content": "Hi"})
    assert rv2.status_code == 200
    msg = rv2.json()
    assert msg["role"] == "assistant"
    assert msg["content"].startswith("Hello")
    assert "world" in msg["content"]
