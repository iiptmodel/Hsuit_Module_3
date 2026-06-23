# Multilingual (Hindi + English) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add full Hindi + English multilingual support to MediScan AI — covering persistent language preference per session, localized static strings, Hindi-safe guardrails, adaptive frontend UX, and resilient TTS.

**Architecture:** Language is stored on the `ChatSession` DB row and round-tripped through the API so it survives page refresh and session switching. Static responses and guardrail patterns are extended to cover Hindi. The frontend reads back the session language and restores the dropdown on switch.

**Tech Stack:** FastAPI (form field, PATCH endpoint), SQLAlchemy + Alembic (DB column), Kokoro TTS (`lang_code='h'`, voice `hf_alpha`), vanilla JS (dropdown state restore, adaptive placeholder)

## Foundation Already Implemented

The following were built in the previous coding session. Do NOT re-implement them:

- `chat.html` — Hindi/English `<select id="languageSelect">` next to the Audience dropdown
- `chat.js` — `languageSelect` wired in `initDomElements()`; `language` appended to `FormData` on send
- `chat.py` — `language: str = Form('English')` accepted; passed to summarizer calls, `generate_chat_response_streaming`, and `_generate_and_attach_tts`
- `chat_service.py` — `generate_chat_response_streaming(language='English')` with `"Always respond in {language}."` in system prompt
- `tts_service.py` — per-language `_pipelines` dict; `_LANG_CONFIG = {'english': ('a','af_heart'), 'hindi': ('h','hf_alpha')}`

## Global Constraints

- Python 3.11+; FastAPI; SQLAlchemy 2.x; Alembic for all schema changes
- Kokoro TTS only; do NOT add a second TTS library
- All new DB columns must have a default value so existing rows are unaffected
- Hindi text literals use Devanagari script (Unicode); do not use transliteration
- No new dependencies unless unavoidable
- Every new endpoint must be tested with `pytest`

---

## File Map

| File | Status | Responsibility |
|------|--------|----------------|
| `app/db/models.py` | Modify | Add `language` column to `ChatSession` |
| `app/db/schemas.py` | Modify | Expose `language` in `ChatSession` schema |
| `app/api/endpoints/chat.py` | Modify | Update session language on each message; return language from GET session endpoint |
| `app/services/chat_service.py` | Modify | Language-aware greeting + error messages; Hindi guardrail reinforcement in system prompt |
| `app/services/tts_service.py` | Modify | Defensive voice-availability check; graceful Hindi TTS fallback |
| `app/static/js/chat.js` | Modify | Restore language dropdown when switching sessions; adaptive placeholder text |
| `app/templates/chat.html` | Modify | Language badge in chat header |
| `app/static/css/chat.css` | Modify | Style for language badge |
| `tests/test_multilingual.py` | Create | End-to-end language flow tests |

---

## Task 1: Persist Language on ChatSession (DB + API)

**Files:**
- Modify: `app/db/models.py` — add `language` column to `ChatSession`
- Modify: `app/db/schemas.py` — add `language` field to `ChatSession` response schema
- Modify: `app/api/endpoints/chat.py` — save language when sending a message
- Test: `tests/test_multilingual.py`

**Interfaces:**
- Produces: `ChatSession.language: str` (DB column, default `'English'`)
- Produces: `GET /api/v1/chat/sessions/{id}` returns `{"language": "Hindi", ...}`
- Produces: `POST /api/v1/chat/sessions/{id}/messages` updates session language to the form's `language` field

---

- [ ] **Step 1: Write the failing test**

```python
# tests/test_multilingual.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_session_language_persists():
    """Language sent with a message is saved on the session and returned."""
    # Create session
    sess = client.post("/api/v1/chat/sessions", json={"title": "Test"}).json()
    sid = sess["id"]

    # Send a message in Hindi (mock heavy services so it doesn't call Ollama)
    resp = client.post(
        f"/api/v1/chat/sessions/{sid}/messages",
        data={"content": "नमस्ते", "audience": "patient", "language": "Hindi"},
    )
    assert resp.status_code == 200

    # Fetch session and assert language is saved
    sess_resp = client.get(f"/api/v1/chat/sessions/{sid}").json()
    assert sess_resp["language"] == "Hindi"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_multilingual.py::test_session_language_persists -v
```

Expected: `FAIL` — `KeyError: 'language'` or `AssertionError`

- [ ] **Step 3: Add `language` column to `ChatSession` model**

In `app/db/models.py`, add inside the `ChatSession` class after the `title` column:

```python
language = Column(String, default='English', nullable=False, server_default='English')
"""Language for AI responses in this session (e.g. 'English', 'Hindi')."""
```

- [ ] **Step 4: Add `language` to `ChatSession` schema**

In `app/db/schemas.py`, update `ChatSession`:

```python
class ChatSession(BaseModel):
    id: int
    created_at: datetime
    title: str
    language: str = 'English'   # <-- add this line
    messages: List[ChatMessage] = []
    reports: List[Report] = []

    class Config:
        from_attributes = True
```

- [ ] **Step 5: Run Alembic migration**

```
python scripts/migrate.py -m "add language to chat_sessions"
```

Expected output ends with: `✅ Migration process completed successfully!`

- [ ] **Step 6: Update session language on message send**

In `app/api/endpoints/chat.py`, inside `send_chat_message`, immediately after the session existence check (around line 132), add:

```python
# Keep session language in sync with what the user selected
if session.language != language:
    session.language = language
    db.add(session)
    db.commit()
    db.refresh(session)
```

- [ ] **Step 7: Run test to verify it passes**

```
pytest tests/test_multilingual.py::test_session_language_persists -v
```

Expected: `PASS`

- [ ] **Step 8: Commit**

```bash
git add app/db/models.py app/db/schemas.py app/api/endpoints/chat.py tests/test_multilingual.py
git commit -m "feat: persist language on ChatSession; round-trip through API"
```

---

## Task 2: Restore Language Dropdown When Switching Sessions

**Files:**
- Modify: `app/static/js/chat.js` — read `session.language` when loading a session and set the dropdown

**Interfaces:**
- Consumes: `GET /api/v1/chat/sessions/{id}` returns `session.language` (from Task 1)
- Consumes: `languageSelect` DOM element (already wired in `initDomElements()`)

---

- [ ] **Step 1: Locate `loadSession` (or equivalent) in `chat.js`**

Search for where the app fetches a session by ID and sets `currentSessionId`. Look for:

```
grep -n "currentSessionId" app/static/js/chat.js | head -20
```

The function that fetches a session and populates the chat screen is the target.

- [ ] **Step 2: Add language restore after session load**

Find the block that fetches the session data and sets `sessionTitle`. After setting the title, add:

```js
// Restore the language dropdown to match this session
if (languageSelect && data.language) {
    languageSelect.value = data.language;
}
```

Replace `data` with whatever variable holds the fetched session JSON in that function.

- [ ] **Step 3: Adapt textarea placeholder to selected language**

Add a helper function near `initDomElements`:

```js
const PLACEHOLDERS = {
    'English': 'Ask about your document, or type a question…',
    'Hindi':   'अपने दस्तावेज़ के बारे में पूछें या प्रश्न टाइप करें…',
};

function updatePlaceholder() {
    if (!messageInput || !languageSelect) return;
    const lang = languageSelect.value;
    messageInput.placeholder = PLACEHOLDERS[lang] || PLACEHOLDERS['English'];
}
```

Call `updatePlaceholder()`:
1. At the end of the session restore block above
2. In `setupEventListeners`, add: `languageSelect.addEventListener('change', updatePlaceholder);`
3. At the end of `initDomElements` (for initial page load)

- [ ] **Step 4: Verify manually**

1. Run the app: `uvicorn app.main:app --reload`
2. Open browser at `http://localhost:8000`
3. Create a session, select Hindi, send a message
4. Click a different session, click back — dropdown should show Hindi
5. Textarea placeholder should read in Hindi when Hindi is selected

- [ ] **Step 5: Commit**

```bash
git add app/static/js/chat.js
git commit -m "feat: restore language dropdown on session switch; adaptive placeholder"
```

---

## Task 3: Language Badge in Chat Header

**Files:**
- Modify: `app/templates/chat.html` — add badge element in `.chat-header`
- Modify: `app/static/css/chat.css` — style the badge
- Modify: `app/static/js/chat.js` — update badge on session load and language change

**Interfaces:**
- Consumes: `languageSelect.value`
- Produces: `<span id="langBadge">` visible in chat header showing "EN" or "HI"

---

- [ ] **Step 1: Add badge HTML to chat header**

In `app/templates/chat.html`, inside `.session-info` div (after `<span class="session-status">Active</span>`), add:

```html
<span class="lang-badge" id="langBadge" aria-label="Active language">EN</span>
```

- [ ] **Step 2: Add badge CSS**

In `app/static/css/chat.css`, add at the end of the file:

```css
.lang-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--r-full);
  background: var(--accent-dim);
  border: 1px solid var(--accent-border);
  color: var(--accent);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  vertical-align: middle;
  margin-left: 0.5rem;
}
```

- [ ] **Step 3: Wire badge updates in JS**

Add a helper in `chat.js`:

```js
const LANG_CODES = { 'English': 'EN', 'Hindi': 'HI' };

function updateLangBadge() {
    const badge = document.getElementById('langBadge');
    if (!badge || !languageSelect) return;
    badge.textContent = LANG_CODES[languageSelect.value] || languageSelect.value.slice(0, 2).toUpperCase();
}
```

Call `updateLangBadge()`:
1. Inside `updatePlaceholder()` so both stay in sync (add one call at end of that function)
2. Inside `initDomElements` after the `languageSelect` assignment

- [ ] **Step 4: Verify visually**

1. Run app, check badge shows "EN" on load
2. Switch dropdown to Hindi — badge should change to "HI" immediately
3. Switch sessions — badge should match the restored language

- [ ] **Step 5: Commit**

```bash
git add app/templates/chat.html app/static/css/chat.css app/static/js/chat.js
git commit -m "feat: language badge in chat header tracks active language"
```

---

## Task 4: Localized Static Strings (Greeting + Errors)

**Files:**
- Modify: `app/services/chat_service.py` — greeting and error strings respect `language`

**Interfaces:**
- Consumes: `language: str` param already on `generate_chat_response_streaming`
- Produces: `generate_greeting_response(language)` returns Hindi or English greeting

---

- [ ] **Step 1: Write the failing test**

In `tests/test_multilingual.py`, add:

```python
from app.services.chat_service import generate_greeting_response

def test_greeting_in_hindi():
    response = generate_greeting_response('Hindi')
    # Must contain Devanagari script (any character in range U+0900–U+097F)
    assert any('ऀ' <= ch <= 'ॿ' for ch in response), \
        f"Expected Hindi text, got: {response[:100]}"

def test_greeting_in_english():
    response = generate_greeting_response('English')
    assert 'MedAnalyzer' in response or 'medical' in response.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_multilingual.py::test_greeting_in_hindi tests/test_multilingual.py::test_greeting_in_english -v
```

Expected: `FAIL` — `TypeError: generate_greeting_response() takes 0 positional arguments`

- [ ] **Step 3: Update `generate_greeting_response` to accept language**

In `app/services/chat_service.py`, replace:

```python
def generate_greeting_response() -> str:
    """Static friendly greeting used for simple greeting fast-path."""
    return (
        "Hello! I'm your MedAnalyzer Assistant. You can ask me to explain imaging, lab, or other medical reports, "
        "summarize uploaded documents for a patient or a doctor, or clarify medical terms. "
        "Feel free to upload a PDF or image, then ask a question like: 'Explain the key findings for a patient.'"
    )
```

With:

```python
_GREETINGS = {
    'hindi': (
        "नमस्ते! मैं आपका MedAnalyzer सहायक हूँ। "
        "आप मुझसे इमेजिंग, लैब या अन्य चिकित्सा रिपोर्ट समझने में मदद माँग सकते हैं, "
        "दस्तावेज़ अपलोड कर सकते हैं और पूछ सकते हैं जैसे: 'यह रिपोर्ट रोगी के लिए समझाइए।'"
    ),
}

def generate_greeting_response(language: str = 'English') -> str:
    """Static friendly greeting in the requested language."""
    key = language.lower()
    if key in _GREETINGS:
        return _GREETINGS[key]
    return (
        "Hello! I'm your MedAnalyzer Assistant. You can ask me to explain imaging, lab, or other medical reports, "
        "summarize uploaded documents for a patient or a doctor, or clarify medical terms. "
        "Feel free to upload a PDF or image, then ask a question like: 'Explain the key findings for a patient.'"
    )
```

- [ ] **Step 4: Update the call sites for `generate_greeting_response`**

In `app/services/chat_service.py`, there are two call sites. Update both:

In `generate_chat_response_streaming`:
```python
# Before (line ~157):
yield generate_greeting_response()
# After:
yield generate_greeting_response(language)
```

In `generate_chat_response`:
```python
# Before (line ~233):
return generate_greeting_response()
# After:
return generate_greeting_response(language)
```

Also update `generate_chat_response` signature to accept language:
```python
def generate_chat_response(user_message: str, image_path: str = None, language: str = 'English') -> str:
```

And update its system prompt (same as streaming version):
```python
system_prompt = (
    "You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results. "
    f"Always respond in {language}."
)
```

- [ ] **Step 5: Update error fallback messages to use language**

In `generate_chat_response_streaming`, the `except` block yields English-only strings. Update to be language-aware:

```python
    except Exception as e:
        logger.exception("Streaming chat response generation failed: %s", e)
        lowered = str(e).lower()
        if "failed to connect" in lowered or "connectionerror" in lowered:
            if language.lower() == 'hindi':
                yield "AI इंजन से कनेक्ट नहीं हो सका। कृपया थोड़ी देर बाद पुनः प्रयास करें।"
            else:
                yield "I couldn't reach the AI engine for streaming. Please try again shortly."
        else:
            if language.lower() == 'hindi':
                yield "प्रतिक्रिया उत्पन्न करने में समस्या हुई। कृपया पुनः प्रयास करें।"
            else:
                yield "I ran into an issue generating the streamed response. Please try again or rephrase your question."
```

- [ ] **Step 6: Run tests**

```
pytest tests/test_multilingual.py::test_greeting_in_hindi tests/test_multilingual.py::test_greeting_in_english -v
```

Expected: `PASS`

- [ ] **Step 7: Commit**

```bash
git add app/services/chat_service.py tests/test_multilingual.py
git commit -m "feat: localized greeting and error messages for Hindi and English"
```

---

## Task 5: Hindi-Safe Guardrails

**Problem:** `apply_response_guardrails` uses English-only regex — Hindi AI responses bypass all safety checks. `validate_user_query` similarly only catches English offensive/off-topic patterns.

**Approach:** Two layers:
1. Add Hindi prohibitions to the system prompt so the LLM self-enforces (most effective)
2. Add a minimal set of Hindi regex patterns for the most critical diagnosis/prescription safety checks

**Files:**
- Modify: `app/services/chat_service.py`

---

- [ ] **Step 1: Write the failing test**

In `tests/test_multilingual.py`, add:

```python
from app.services.chat_service import apply_response_guardrails

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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_multilingual.py::test_hindi_diagnosis_guardrail tests/test_multilingual.py::test_hindi_prescription_guardrail -v
```

Expected: `FAIL` — `TypeError: apply_response_guardrails() takes 1 positional argument`

- [ ] **Step 3: Add Hindi patterns to PROHIBITED_PATTERNS**

In `app/services/chat_service.py`, extend `PROHIBITED_PATTERNS`:

```python
PROHIBITED_PATTERNS: Dict[str, List[str]] = {
    # ... existing English keys unchanged ...
    "hindi_diagnosis": [
        r"आपको.*(है|हैं|हो)",          # "You have [condition]"
        r"आप.*(बीमारी|रोग|विकार).*(से पीड़ित|है)",
        r"(मेरा|मैं).*(निदान|डायग्नोसिस)",
        r"निश्चित रूप से.*(है|हैं)",
    ],
    "hindi_prescription": [
        r"आप.*(मिलीग्राम|mg|ml).*(लें|खाएं|पियें)",
        r"(रोज़|प्रतिदिन|दिन में).*(मिलीग्राम|mg)",
        r"मैं.*(दवाई|दवा|औषधि).*(देता|देती|लिखता)",
        r"(शुरू करें|लेना शुरू करें).*(मिलीग्राम|mg)",
    ],
}
```

- [ ] **Step 4: Update `apply_response_guardrails` signature and logic**

Replace the function signature and add Hindi pattern checks:

```python
def apply_response_guardrails(response: str, language: str = 'English') -> str:
    """Filter AI response to enforce medical safety guardrails."""
    response_lower = (response or "").lower()

    # English guardrails (existing — unchanged)
    for pattern in PROHIBITED_PATTERNS["diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained diagnosis language: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं चिकित्सा निष्कर्षों को समझाने में मदद कर सकता हूँ, लेकिन निश्चित निदान नहीं दे सकता। "
                    "कृपया अपने स्वास्थ्य सेवा प्रदाता से परामर्श करें।"
                )
            return (
                "I can help you understand what these medical findings suggest, "
                "but I cannot provide a definitive diagnosis. Please discuss with your healthcare provider."
            )

    for pattern in PROHIBITED_PATTERNS["prescription"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained prescription language: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं दवाइयाँ लिख या सुझाव नहीं दे सकता। "
                    "सही खुराक के लिए अपने डॉक्टर से मिलें।"
                )
            return (
                "I can explain how medications work, but I cannot prescribe specific medications or dosages. "
                "Your doctor will determine the appropriate treatment."
            )

    for pattern in PROHIBITED_PATTERNS["mental_health_diagnosis"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained mental health diagnosis: %s", pattern)
            if language.lower() == 'hindi':
                return (
                    "मैं मानसिक स्वास्थ्य निदान नहीं कर सकता। "
                    "कृपया किसी मानसिक स्वास्थ्य विशेषज्ञ से परामर्श करें।"
                )
            return (
                "I cannot provide mental health diagnoses. "
                "Please consult with a licensed mental health professional."
            )

    for pattern in PROHIBITED_PATTERNS["jokes"]:
        if re.search(pattern, response_lower):
            logger.warning("Response contained humor: %s", pattern)
            return "I apologize for the inappropriate response. Let me provide factual medical information instead."

    # Hindi-specific guardrails (applied to original response, not lowercased, since Devanagari is case-neutral)
    if language.lower() == 'hindi':
        for pattern in PROHIBITED_PATTERNS["hindi_diagnosis"]:
            if re.search(pattern, response):
                logger.warning("Hindi response contained diagnosis language: %s", pattern)
                return (
                    "मैं चिकित्सा निष्कर्षों को समझाने में मदद कर सकता हूँ, लेकिन निश्चित निदान नहीं दे सकता। "
                    "कृपया अपने स्वास्थ्य सेवा प्रदाता से परामर्श करें।"
                )
        for pattern in PROHIBITED_PATTERNS["hindi_prescription"]:
            if re.search(pattern, response):
                logger.warning("Hindi response contained prescription language: %s", pattern)
                return (
                    "मैं दवाइयाँ लिख या सुझाव नहीं दे सकता। "
                    "सही खुराक के लिए अपने डॉक्टर से मिलें।"
                )

    return response
```

- [ ] **Step 5: Update all call sites to pass `language`**

In `chat_service.py`, update both places where `apply_response_guardrails` is called:

In `generate_chat_response_streaming` (after the streaming loop):
```python
validated = apply_response_guardrails(full_response, language=language)
```

In `generate_chat_response`:
```python
validated = apply_response_guardrails(raw_response, language=language)
```

- [ ] **Step 6: Strengthen system prompt with Hindi guardrail language**

In `generate_chat_response_streaming`, update the system prompt:

```python
_GUARDRAIL_SUFFIX = {
    'hindi': (
        " कभी भी निश्चित निदान न दें या दवाइयाँ न लिखें। "
        "हमेशा रोगी को डॉक्टर से परामर्श लेने की सलाह दें।"
    ),
    'english': (
        " Never provide a definitive diagnosis or prescribe medications. "
        "Always recommend consulting a healthcare professional."
    ),
}

system_prompt = (
    "You are MedAnalyzer Assistant, a professional medical information assistant specialized in helping patients understand their medical reports and test results. "
    f"Always respond in {language}."
    + _GUARDRAIL_SUFFIX.get(language.lower(), _GUARDRAIL_SUFFIX['english'])
)
```

Apply the same updated `system_prompt` in `generate_chat_response` as well.

- [ ] **Step 7: Run tests**

```
pytest tests/test_multilingual.py -v
```

Expected: all tests `PASS`

- [ ] **Step 8: Commit**

```bash
git add app/services/chat_service.py tests/test_multilingual.py
git commit -m "feat: Hindi guardrail patterns + strengthened system prompt safety for non-English"
```

---

## Task 6: TTS Hindi Resilience

**Problem:** If the Kokoro `hf_alpha` Hindi voice is not bundled with the installed version, the entire TTS task crashes silently (audio just never attaches). We need a clear diagnostic and graceful English fallback.

**Files:**
- Modify: `app/services/tts_service.py`

---

- [ ] **Step 1: Write the failing test**

In `tests/test_multilingual.py`, add:

```python
from unittest.mock import patch, MagicMock
from app.services import tts_service

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
    import os
    assert os.path.exists(out)
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_multilingual.py::test_tts_falls_back_to_english_on_hindi_failure -v
```

Expected: `FAIL` — the function raises `RuntimeError` instead of falling back.

- [ ] **Step 3: Add fallback logic in `generate_speech`**

In `app/services/tts_service.py`, update `generate_speech` to try the target language then fall back:

```python
def generate_speech(text: str, language: str, output_file_path: str):
    """
    Converts text to speech using Kokoro and saves it to a file.
    Supports English and Hindi; falls back to English for unsupported languages
    or if the target pipeline fails to initialize.
    """
    logger.info(f"Generating speech (length={len(text)}, language={language}) -> {output_file_path}")

    lang_key = language.lower()
    if lang_key not in _LANG_CONFIG:
        logger.warning(f"Language '{language}' not in TTS config; falling back to English.")
        lang_key = 'english'

    lang_code, voice = _LANG_CONFIG[lang_key]

    # Try target language; fall back to English if pipeline unavailable
    try:
        pipeline = _get_pipeline(lang_code)
    except Exception as e:
        logger.warning(f"TTS pipeline for '{language}' (lang_code={lang_code}) unavailable: {e}. Falling back to English.")
        lang_code, voice = _LANG_CONFIG['english']
        pipeline = _get_pipeline(lang_code)

    if not text or not text.strip():
        raise ValueError("Text input is empty or invalid")

    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    samplerate = 24000
    generator = pipeline(text, voice=voice, speed=1, split_pattern=r'\n+')

    with sf.SoundFile(output_file_path, mode='w', samplerate=samplerate, channels=1, subtype='PCM_16') as sf_file:
        total_frames = 0
        for i, (gs, ps, audio) in enumerate(generator):
            arr = np.asarray(audio)
            if arr.ndim > 1 and arr.shape[1] > 1:
                arr = arr[:, 0]
            sf_file.write(arr)
            total_frames += arr.shape[0]
            logger.debug(f"TTS chunk {i+1}: {arr.shape[0]} frames")

    if not (os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0):
        raise IOError("Audio file was not created or is empty")

    logger.info(f"TTS complete: {os.path.getsize(output_file_path)} bytes at {output_file_path}")
```

- [ ] **Step 4: Run test**

```
pytest tests/test_multilingual.py::test_tts_falls_back_to_english_on_hindi_failure -v
```

Expected: `PASS`

- [ ] **Step 5: Run all multilingual tests**

```
pytest tests/test_multilingual.py -v
```

Expected: all `PASS`

- [ ] **Step 6: Commit**

```bash
git add app/services/tts_service.py tests/test_multilingual.py
git commit -m "feat: graceful Hindi TTS fallback to English when voice unavailable"
```

---

## Task 7: Integration Smoke Test + Run Verification

**Files:**
- Test: `tests/test_multilingual.py` — full session flow test (mocked Ollama)

---

- [ ] **Step 1: Add end-to-end flow test**

In `tests/test_multilingual.py`, add:

```python
from unittest.mock import patch, AsyncMock

async def _mock_stream(*args, **kwargs):
    yield "यह एक परीक्षण प्रतिक्रिया है।"  # "This is a test response."

def test_full_hindi_session_flow():
    """Create session, send Hindi message, verify response saved and session language updated."""
    sess = client.post("/api/v1/chat/sessions", json={"title": "Hindi Test"}).json()
    sid = sess["id"]

    with patch(
        "app.services.chat_service.generate_chat_response_streaming",
        side_effect=_mock_stream
    ), patch(
        "app.api.endpoints.chat._generate_and_attach_tts",
        new_callable=AsyncMock
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
```

- [ ] **Step 2: Run full test suite**

```
pytest tests/test_multilingual.py -v
```

Expected: all tests `PASS`

- [ ] **Step 3: Run app and manual smoke test**

```
uvicorn app.main:app --reload
```

1. Open `http://localhost:8000`
2. Create new session
3. Switch dropdown to **Hindi**
4. Verify placeholder reads: `अपने दस्तावेज़ के बारे में पूछें या प्रश्न टाइप करें…`
5. Verify header badge shows **HI**
6. Type `नमस्ते` and send — should get Hindi greeting response
7. Upload a PDF, select Hindi, select Patient → should get Hindi patient summary
8. Refresh page, click the session → dropdown should restore to **Hindi**, badge shows **HI**

- [ ] **Step 4: Final commit**

```bash
git add tests/test_multilingual.py
git commit -m "test: end-to-end Hindi session flow smoke test"
```

---

## Self-Review

### Spec Coverage

| Requirement | Task |
|---|---|
| Hindi text in AI responses | Task 4 (system prompt), Task 5 (guardrail reinforcement) |
| Language persists per session across refresh | Task 1 (DB), Task 2 (JS restore) |
| Hindi-aware safety guardrails | Task 5 |
| Hindi greeting response | Task 4 |
| Hindi error messages | Task 4 |
| Adaptive textarea placeholder | Task 2 |
| Language badge in header | Task 3 |
| TTS Hindi support | Foundation (already done) |
| TTS Hindi fallback | Task 6 |
| Tests for all above | Tasks 1–7 |

### Placeholder Scan

No TBD, no "similar to Task N", no "add error handling" without code — all steps include actual code.

### Type Consistency

- `apply_response_guardrails(response: str, language: str = 'English')` — used with `language=language` in both call sites ✓
- `generate_greeting_response(language: str = 'English')` — called as `generate_greeting_response(language)` in both streaming and non-streaming ✓
- `ChatSession.language` column returns `str` — matched in schema as `language: str = 'English'` ✓
- `_generate_and_attach_tts(message_id, text, audio_filename, language)` — all 4 args passed at `background_tasks.add_task(...)` call site ✓
