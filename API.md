# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## API Endpoints

Note: this application can run in API-only mode by setting the environment variable `API_ONLY=1`. In that mode the web UI and static assets are not served and the root (`GET /`) returns a small JSON object. All `/api/v1/*` endpoints remain available.


### Authentication (development)

Authentication endpoints are disabled in this development build. The original
JWT-based register/login endpoints are preserved in the repository history but
are not active by default. Reports endpoints are public; see Reports below.

---

---

### Chat & Session API (chat)

This project includes a chat-oriented interface that groups messages into sessions and supports file attachments. The chat endpoints power the web UI and support streaming assistant responses via WebSocket.

#### Get Sessions

**GET** `/api/v1/chat/sessions`

Returns a list of chat sessions (most recent first) including messages and associated reports.

#### Create Session

**POST** `/api/v1/chat/sessions`

Create a new chat session. Body: `{ "title": "Your session title" }`.

#### Update Session (rename)

**PATCH** `/api/v1/chat/sessions/{session_id}`

Update chat session metadata (currently supports updating `title`). Example request body: `{ "title": "New Title" }`.

Example (curl):
```bash
curl -X PATCH http://localhost:8000/api/v1/chat/sessions/42 \
  -H "Content-Type: application/json" \
  -d '{"title":"Follow-up review"}'
```

#### Delete Session

**DELETE** `/api/v1/chat/sessions/{session_id}`

Deletes a session and all its messages and associated reports.

#### Send Message (with optional file)

**POST** `/api/v1/chat/sessions/{session_id}/messages`

Submit a user message and optionally attach a file (image or PDF). The endpoint accepts multipart form data with fields:

- `content`: string (required) — user message text
- `file`: file (optional) — uploaded file (PDF, PNG, JPG, JPEG, BMP, TIFF)
- `audience`: string (optional, default `patient`) — `patient` or `doctor`. Controls which summarizer path is used.

Notes:
- File size limit: 10MB. The server reads uploaded bytes into a separate variable and writes the file to `media/chat_uploads/` so the textual `content` is not overwritten by raw bytes.
- When a file is uploaded the backend creates a `Report` row and associates it to the chat session. For images the VLM is used directly; for documents text is extracted and summarized.
- The endpoint returns the newly created user message and will create an assistant message that is streamed to clients (websocket) while the AI response is generated.

Example (curl):
```bash
curl -X POST http://localhost:8000/api/v1/chat/sessions/42/messages \
  -F "content=Please review this report" \
  -F "audience=patient" \
  -F "file=@/path/to/report.pdf"
```

---

### Guardrails & Disclaimer Behavior

The summarizer code applies guardrail checks to avoid producing diagnoses or prescriptions. Recent change: instead of replacing the model's output with a canned disclaimer, the service now appends a short disclaimer to flagged outputs while preserving the model content. The guardrail logic is implemented in `app/services/summarizer_service.py` (`_guardrail_validator`).


### Reports

Report endpoints are public in this development build.

#### Upload Text Report

**POST** `/api/v1/reports/upload-text`

Submit a text-based medical report for analysis.

**Request** (Form Data):
```
text_content: "Blood test results: Cholesterol 240 mg/dL, HDL 45 mg/dL"
language: "en"
```

**Response** (200 OK):
```json
{
  "id": 1,
  "owner_id": 1,
  "report_type": "text",
  "language": "en",
  "raw_text": "Blood test results...",
  "summary_text": "Your cholesterol level is slightly above normal at 240 mg/dL...",
  "audio_file_path": "media/audio/report_1.mp3",
  "status": "completed",
  "created_at": "2025-11-03T12:00:00",
  "original_file_path": null
}
```

**Processing Time**: 5-10 seconds

---

#### Upload File Report

**POST** `/api/v1/reports/upload-file`

Submit an image or PDF medical report for analysis.

**Request** (Multipart Form Data):
```
file: <binary file data>
language: "en"
```

**Supported Formats**:
- Images: PNG, JPG, JPEG, BMP, TIFF
- Documents: PDF, DOCX

**Response** (200 OK):
```json
{
  "id": 2,
  "owner_id": 1,
  "report_type": "image",
  "language": "en",
  "raw_text": null,
  "summary_text": "This chest X-ray shows clear lung fields...",
  "audio_file_path": "media/audio/report_2.mp3",
  "original_file_path": "media/reports/1_chest_xray.png",
  "status": "completed",
  "created_at": "2025-11-03T12:05:00"
}
```

**Processing Time**: 
- Images: 10-15 seconds
- PDFs: 15-30 seconds (depends on page count)

**File Size Limit**: 10MB

---

#### Get All Reports

**GET** `/api/v1/reports/`

Retrieve all reports for the authenticated user.

**Response** (200 OK):
```json
[
  {
    "id": 2,
    "owner_id": 1,
    "report_type": "image",
    "language": "en",
    "summary_text": "This chest X-ray shows...",
    "audio_file_path": "media/audio/report_2.mp3",
    "status": "completed",
    "created_at": "2025-11-03T12:05:00"
  },
  {
    "id": 1,
    "owner_id": 1,
    "report_type": "text",
    "language": "en",
    "summary_text": "Your cholesterol level...",
    "audio_file_path": "media/audio/report_1.mp3",
    "status": "completed",
    "created_at": "2025-11-03T12:00:00"
  }
]
```

**Sorting**: Most recent first (by `created_at DESC`)

---

#### Get Single Report

**GET** `/api/v1/reports/{report_id}`

Retrieve details of a specific report.

**Parameters**:
- `report_id` (path): Integer, report ID

**Response** (200 OK):
```json
{
  "id": 1,
  "owner_id": 1,
  "report_type": "text",
  "language": "en",
  "raw_text": "Blood test results...",
  "summary_text": "Your cholesterol level is slightly above normal...",
  "audio_file_path": "media/audio/report_1.mp3",
  "original_file_path": null,
  "status": "completed",
  "created_at": "2025-11-03T12:00:00"
}
```

**Errors**:
- `404 Not Found`: Report doesn't exist or belongs to another user

---

## Report Status Values

| Status | Description |
|--------|-------------|
| `processing` | AI analysis in progress |
| `completed` | Successfully processed |
| `failed` | Processing encountered an error |

---

## Data Models

### User Schema

```typescript
{
  id: number;
  email: string;
  created_at: datetime;
}
```

### Report Schema

```typescript
{
  id: number;
  owner_id: number;
  report_type: "text" | "image";
  language: string;  // ISO 639-1 code (e.g., "en")
  raw_text: string | null;
  summary_text: string;
  audio_file_path: string;
  original_file_path: string | null;
  status: "processing" | "completed" | "failed";
  created_at: datetime;
}
```

---

## Example Requests

### cURL Examples

#### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secure123"}'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=secure123"
```

#### Upload Text Report
```bash
curl -X POST http://localhost:8000/api/v1/reports/upload-text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text_content=Blood glucose: 140 mg/dL" \
  -F "language=en"
```

#### Upload Image
```bash
curl -X POST http://localhost:8000/api/v1/reports/upload-file \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@xray.png" \
  -F "language=en"
```

#### Get Reports
```bash
curl -X GET http://localhost:8000/api/v1/reports/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Python Examples

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"email": "test@example.com", "password": "secure123"}
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "test@example.com", "password": "secure123"}
)
token = response.json()["access_token"]

# Headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Upload text report
response = requests.post(
    f"{BASE_URL}/reports/upload-text",
    headers=headers,
    data={
        "text_content": "Blood test: Cholesterol 240 mg/dL",
        "language": "en"
    }
)
report = response.json()
print(f"Summary: {report['summary_text']}")
print(f"Audio: {report['audio_file_path']}")

# Upload image
with open("xray.png", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/reports/upload-file",
        headers=headers,
        data={"language": "en"},
        files={"file": f}
    )
    report = response.json()
    print(f"Analysis: {report['summary_text']}")

# Get all reports
response = requests.get(f"{BASE_URL}/reports/", headers=headers)
reports = response.json()
for report in reports:
    print(f"Report {report['id']}: {report['status']}")
```

---

### JavaScript (Fetch API)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Register
const register = async () => {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "test@example.com",
      password: "secure123"
    })
  });
  return response.json();
};

// Login
const login = async () => {
  const formData = new URLSearchParams();
  formData.append("username", "test@example.com");
  formData.append("password", "secure123");
  
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    body: formData
  });
  const data = await response.json();
  return data.access_token;
};

// Upload text report
const uploadText = async (token) => {
  const formData = new FormData();
  formData.append("text_content", "Blood glucose: 140 mg/dL");
  formData.append("language", "en");
  
  const response = await fetch(`${BASE_URL}/reports/upload-text`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${token}` },
    body: formData
  });
  return response.json();
};

// Upload image
const uploadImage = async (token, file) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", "en");
  
  const response = await fetch(`${BASE_URL}/reports/upload-file`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${token}` },
    body: formData
  });
  return response.json();
};

// Usage
(async () => {
  const token = await login();
  const report = await uploadText(token);
  console.log("Summary:", report.summary_text);
})();
```

---

## Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI**: `http://localhost:8000/docs`
  - Interactive API testing
  - Try endpoints directly in browser
  - See request/response schemas

- **ReDoc**: `http://localhost:8000/redoc`
  - Clean, detailed documentation
  - Better for reading

---

## Rate Limiting

Currently not implemented. Recommended for production:

```python
# Install: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/reports/upload-text")
@limiter.limit("5/minute")  # 5 requests per minute
async def upload_text_report(...):
    ...
```

---

## Error Handling

All errors return consistent JSON format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Server/model error |

---

## WebSocket Support (Future)

For real-time processing updates:

```javascript
// Coming soon
const ws = new WebSocket("ws://localhost:8000/ws/reports");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Processing:", data.progress);
};
```

---

## Pagination (Future Enhancement)

For large datasets:

```
GET /api/v1/reports/?skip=0&limit=20
```

---

## Support

- **Documentation**: `GET /docs` (Swagger UI)
- **Health Check**: `GET /health` (returns server status)
- **GitHub Issues**: https://github.com/iiptmodel/Hsuit_Module_3/issues
