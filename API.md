# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## API Endpoints

### Authentication

#### Register New User

**POST** `/api/v1/auth/register`

Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-11-03T12:00:00"
}
```

**Errors**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid email format or weak password

---

#### Login

**POST** `/api/v1/auth/login`

Authenticate and receive JWT token.

**Request Body** (Form Data):
```
username: user@example.com
password: securepassword123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized`: Invalid credentials

**Usage**:
```javascript
// Include token in subsequent requests
headers: {
  "Authorization": "Bearer <access_token>"
}
```

---

### Reports

All report endpoints require authentication (Bearer token).

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
