import io
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from PIL import Image

os.environ.setdefault("PRELOAD_MODELS", "0")

from app.main import app
from app.db import models
from app.db.database import Base
from app.api import deps
import app.services.chat_service as chat_service
import app.services.tts_service as tts_service


def test_upload_image_and_message(monkeypatch):
    # Shared in-memory SQLite
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

    # Mock streaming to short deterministic output
    async def fake_stream(user_message, image_path=None):
        yield "Test"
        await asyncio.sleep(0)
        yield " response"

    monkeypatch.setattr(chat_service, "generate_chat_response_streaming", fake_stream)
    monkeypatch.setattr(tts_service, "generate_speech", lambda *a, **k: None)

    client = TestClient(app)

    # Create session
    rv = client.post("/api/v1/chat/sessions", json={"title": "test-session"})
    assert rv.status_code == 200
    sid = rv.json()["id"]

    # Build an in-memory PNG
    img_bytes = io.BytesIO()
    im = Image.new("RGB", (32, 32), color=(200, 100, 50))
    im.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    files = {
        "content": (None, "Please analyze this image"),
        "audience": (None, "patient"),
        "file": ("sample.png", img_bytes, "image/png"),
    }

    rv2 = client.post(f"/api/v1/chat/sessions/{sid}/messages", files=files)
    assert rv2.status_code == 200
    msg = rv2.json()
    assert msg["role"] == "assistant"
    assert "Test" in msg["content"]

    # Fetch session to verify report persisted with original filename and thumbnail
    rv3 = client.get(f"/api/v1/chat/sessions/{sid}")
    assert rv3.status_code == 200
    session = rv3.json()
    reports = session.get("reports", [])
    assert len(reports) == 1
    rep = reports[0]
    assert rep.get("original_filename") == "sample.png"
    assert rep.get("report_type") == "image" or rep.get("report_type") == 'ReportType.image'
    # thumbnail may or may not exist on some CI environments; ensure field present
    assert "thumbnail_path" in rep
