import asyncio
import os
from unittest.mock import patch, MagicMock

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
from app.services.chat_service import generate_greeting_response, apply_response_guardrails


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


def test_greeting_in_hindi():
    response = generate_greeting_response('Hindi')
    # Must contain Devanagari script (any character in range U+0900-U+097F)
    assert any('ऀ' <= ch <= 'ॿ' for ch in response), \
        f"Expected Hindi text, got: {response[:100]}"


def test_greeting_in_english():
    response = generate_greeting_response('English')
    assert 'MedAnalyzer' in response or 'medical' in response.lower()


def test_hindi_diagnosis_guardrail():
    """A Hindi diagnosis statement must be caught by guardrails."""
    hindi_diagnosis = "आपको निश्चित रूप से मधुमेह है।"  # "You definitely have diabetes."
    result = apply_response_guardrails(hindi_diagnosis, language='Hindi')
    # Must not pass through unchanged
    assert result != hindi_diagnosis, "Hindi diagnosis should be filtered by guardrails"


def test_hindi_prescription_guardrail():
    """A Hindi prescription statement must be caught by guardrails."""
    hindi_rx = "आप रोज़ 500 मिलीग्राम मेटफॉर्मिन लें।"  # "Take 500mg metformin daily."
    result = apply_response_guardrails(hindi_rx, language='Hindi')
    assert result != hindi_rx, "Hindi prescription should be filtered by guardrails"


async def _mock_stream(*args, **kwargs):
    yield "यह एक परीक्षण प्रतिक्रिया है।"  # "This is a test response."


def test_full_hindi_session_flow():
    """Create session, send Hindi message, verify response saved and session language updated."""
    from unittest.mock import AsyncMock

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

    with TestClient(app) as client:
        sess = client.post("/api/v1/chat/sessions", json={"title": "Hindi Test"}).json()
        sid = sess["id"]

        with patch(
            "app.services.chat_service.generate_chat_response_streaming",
            side_effect=_mock_stream,
        ), patch(
            "app.api.endpoints.chat._generate_and_attach_tts",
            new_callable=AsyncMock,
        ):
            resp = client.post(
                f"/api/v1/chat/sessions/{sid}/messages",
                data={"content": "रिपोर्ट समझाइए", "audience": "patient", "language": "Hindi"},
            )

        assert resp.status_code == 200
        msg = resp.json()
        assert msg["role"] == "assistant"

        # Session language persisted
        sess_data = client.get(f"/api/v1/chat/sessions/{sid}").json()
        assert sess_data["language"] == "Hindi"

    app.dependency_overrides.clear()


def test_tts_falls_back_to_english_on_hindi_failure(tmp_path):
    """If Hindi pipeline init fails, TTS falls back to English without raising."""
    out = str(tmp_path / "test.wav")

    def bad_pipeline(lang_code):
        if lang_code == 'h':
            raise RuntimeError("voice hf_alpha not found")
        # Return a real-ish mock for English
        mock = MagicMock()
        mock.return_value = iter([(None, None, [0.0] * 24000)])
        return mock

    # Clear cached pipelines so our mock takes effect
    tts_service._pipelines.clear()
    with patch("app.services.tts_service.KPipeline", side_effect=bad_pipeline):
        # Should not raise — falls back to English
        tts_service.generate_speech("Hello test", "Hindi", out)

    # English pipeline was used; file exists
    assert os.path.exists(out)
