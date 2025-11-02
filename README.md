# Medical Report Analysis & Voice Summary System

## 🎯 Project Objective

Build a system that analyzes patient medical reports, generates clear explanations, and provides output in voice format in multiple languages.

### Problem Statement
Patients often receive complex medical reports that are difficult to interpret. Understanding test results without assistance can be overwhelming.

### Solution
This application:
1. **Accepts medical reports** (text, images, PDFs)
2. **Analyzes using AI** (MedGemma for medical understanding)
3. **Generates clear explanations** (simplified medical terminology)
4. **Provides voice output** (Text-to-Speech in multiple languages)

## 🏗️ Architecture

### Tech Stack
- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **AI Models**:
  - **MedGemma** (`unsloth/medgemma-4b-it`) - Medical image and text analysis
  - **Docling** - Document parsing (PDFs, various medical document formats)
  - **Kokoro TTS** - Text-to-speech for voice output
- **Authentication**: JWT-based auth with bcrypt password hashing

### Project Structure
```
d:\Prushal/
├── app/
│   ├── api/
│   │   ├── __init__.py          # API router configuration
│   │   ├── deps.py              # FastAPI dependencies
│   │   └── endpoints/
│   │       ├── auth.py          # Authentication endpoints
│   │       └── reports.py       # Report upload & processing
│   ├── core/
│   │   ├── config.py            # App configuration
│   │   └── security.py          # JWT & password utilities
│   ├── db/
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   ├── services/
│   │   ├── parser_service.py    # Docling document parsing
│   │   ├── summarizer_service.py # MedGemma AI analysis
│   │   └── tts_service.py       # Kokoro text-to-speech
│   ├── static/                  # CSS/JS assets
│   ├── templates/               # HTML templates
│   └── main.py                  # FastAPI application
├── media/
│   ├── audio/                   # Generated voice outputs
│   └── reports/                 # Uploaded medical reports
├── models/                      # AI models cache (auto-created)
├── myenv/                       # Python virtual environment
├── download_models.py           # Model download script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database
- CUDA-capable GPU (recommended for AI models)

### 2. Installation

```powershell
# Clone and navigate to project
cd d:\Prushal

# Create and activate virtual environment
python -m venv myenv
.\myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download AI models (will be saved to ./models/ directory)
python download_models.py
```

### 3. Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost/medanalysis_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Setup

```powershell
# Create database tables
# (Automatic on first run via main.py startup event)
# For production, use Alembic migrations
```

### 5. Run Application

```powershell
# Activate virtual environment
.\myenv\Scripts\activate

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the application at: `http://localhost:8000`

## 📋 Features

### 1. User Authentication
- Register new accounts
- Login with JWT tokens
- Secure password hashing (bcrypt)

### 2. Report Upload
- **Text Reports**: Direct text input
- **Image Reports**: X-rays, scans (analyzed by MedGemma vision model)
- **Document Reports**: PDFs, Word docs (parsed by Docling)

### 3. AI Analysis Pipeline
```
Input → Parsing (Docling) → Analysis (MedGemma) → Summary → TTS (Kokoro) → Audio Output
```

#### For Images (e.g., X-rays):
1. Upload image file
2. MedGemma directly analyzes the image
3. Generates patient-friendly explanation
4. Converts to voice

#### For Documents (PDFs):
1. Upload document
2. Docling extracts structured text
3. MedGemma analyzes extracted text
4. Generates patient-friendly explanation
5. Converts to voice

### 4. Voice Output
- Multi-language support (via language parameter)
- High-quality TTS using Kokoro
- Downloadable MP3 files

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Reports
- `POST /api/v1/reports/upload-text` - Submit text report
- `POST /api/v1/reports/upload-file` - Submit image/document report
- `GET /api/v1/reports/` - Get all user reports
- `GET /api/v1/reports/{report_id}` - Get specific report details

### Pages
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /dashboard` - User dashboard (authenticated)

## 🧪 Example Usage

### Upload Text Report
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/reports/upload-text",
    headers={"Authorization": f"Bearer {token}"},
    data={
        "text_content": "Blood test shows cholesterol: 240 mg/dL, HDL: 45 mg/dL",
        "language": "en"
    }
)

report = response.json()
print(f"Summary: {report['summary_text']}")
print(f"Audio: {report['audio_file_path']}")
```

### Upload Image Report (X-ray)
```python
response = requests.post(
    "http://localhost:8000/api/v1/reports/upload-file",
    headers={"Authorization": f"Bearer {token}"},
    data={"language": "en"},
    files={"file": open("xray.png", "rb")}
)
```

## 🧠 AI Models

### MedGemma (`unsloth/medgemma-4b-it`)
- **Purpose**: Medical image and text understanding
- **Capabilities**: 
  - Vision-language model (VLM)
  - Analyzes X-rays, CT scans, lab reports
  - Generates medical explanations
- **Size**: ~4B parameters
- **Location**: `./models/transformers/`

### Docling
- **Purpose**: Document parsing and text extraction
- **Capabilities**:
  - PDF parsing
  - Table extraction
  - Multi-format support
- **Location**: Embedded library

### Kokoro TTS
- **Purpose**: Text-to-speech conversion
- **Capabilities**:
  - Natural-sounding voice
  - Multiple voices (American Female Heart)
  - High-quality 24kHz output
- **Location**: Auto-downloaded on first use

## 🛡️ Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- User-specific report access control
- CORS protection
- Input validation with Pydantic

## 📊 Database Schema

### Users Table
- id, email, hashed_password, created_at

### Reports Table
- id, owner_id, report_type, language
- original_file_path, raw_text
- summary_text, audio_file_path
- status (processing/completed/failed)
- created_at

## 🎯 Intern Focus Areas

1. **Data Collection**: Collect anonymized test reports from clinics/hospitals
2. **Doctor Observations**: Observe how doctors explain results to patients
3. **Pattern Documentation**: Document patterns to improve clarity and patient understanding
4. **Testing**: Test with various medical report formats
5. **Feedback**: Gather patient feedback on explanation clarity

## 🐛 Troubleshooting

### Models not downloading
```powershell
# Run model download script manually
python download_models.py
```

### Database connection issues
```powershell
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
```

### Import errors
```powershell
# Ensure all __init__.py files exist
# Check virtual environment is activated
```

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Team Here]
