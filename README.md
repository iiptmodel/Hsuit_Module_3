# Medical Report Analysis & Voice Summary System

## 🎯 Project Objective

Build an intelligent system that analyzes patient medical reports, generates clear explanations, and provides output in voice format with medical guardrails.

### Problem Statement

Patients often receive complex medical reports that are difficult to interpret. Understanding test results without medical assistance can be overwhelming and confusing.

### Solution

This application provides:

1. **Accepts medical reports** (text, images, PDFs)
2. **Analyzes using AI** (MedGemma Vision-Language Model for medical understanding)
3. **Generates clear explanations** (simplified medical terminology with safety guardrails)
4. **Provides voice output** (Text-to-Speech in multiple languages)
5. **Interactive chat** (Ask questions about your medical documents)

## 🏗️ Architecture

### Tech Stack

- **Backend Framework**: FastAPI (async/await support)
- **Database**: PostgreSQL (SQLAlchemy ORM) or SQLite (development)
- **AI Models**:
  - **MedGemma** (`unsloth/medgemma-4b-it`) - Medical image and text analysis
  - **Docling** - Document parsing (PDFs, images, various medical document formats)
  - **Kokoro TTS** - High-quality text-to-speech for voice output
- **Security**: Medical guardrails prevent diagnosis, prescriptions, and inappropriate content
- **Authentication**: JWT-based (disabled in development build)

### Project Structure

```plaintext
d:\Prushal/
├── app/
│   ├── api/
│   │   ├── __init__.py              # API router configuration
│   │   ├── deps.py                  # FastAPI dependencies
│   │   └── endpoints/
│   │       ├── reports.py           # Report upload & processing
│   │       └── chat.py              # Chat endpoints with file upload
│   ├── core/
│   │   ├── config.py                # App configuration
│   │   └── security.py              # JWT & password utilities
│   ├── db/
│   │   ├── database.py              # Database connection
│   │   ├── models.py                # SQLAlchemy models (Report, ChatSession, ChatMessage)
│   │   └── schemas.py               # Pydantic schemas for validation
│   ├── services/
│   │   ├── parser_service.py        # Multi-tier PDF parsing (Docling + OCR fallback)
│   │   ├── summarizer_service.py    # MedGemma AI analysis
│   │   ├── tts_service.py           # Kokoro text-to-speech
│   │   └── chat_service.py          # Chat with medical guardrails
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css            # Main stylesheet
│   │   │   └── chat.css             # Chat interface styles
│   │   └── js/
│   │       ├── app.js               # Main JavaScript
│   │       └── chat.js              # Chat functionality
│   ├── templates/
│   │   └── chat.html                # Unified chat interface
│   ├── main.py                      # FastAPI application entry
│   └── pages.py                     # Template routes
├── media/
│   ├── reports/                     # Uploaded medical documents
│   ├── audio/                       # Generated TTS audio files
│   └── chat_uploads/                # Chat file attachments
├── models/                          # Downloaded AI models (cached)
├── myenv/                           # Python virtual environment
├── requirements.txt                 # Python dependencies
├── download_models.py               # Script to download AI models
├── .env                             # Environment variables (DATABASE_URL, JWT_SECRET_KEY)
├── README.md                        # This file
├── QUICKSTART.md                    # Quick setup guide
├── DOCUMENTATION.md                 # Detailed documentation
└── DEPLOYMENT.md                    # Production deployment guide
```

## 📋 Prerequisites

### Required Software

- **Python 3.11+** (Download from [python.org](https://www.python.org/downloads/))
- **PostgreSQL 15+** (Optional - can use SQLite for development)
- **Git** (for cloning repository)
- **Tesseract OCR** (for OCR fallback in PDF parsing)

### Hardware Requirements

- **RAM**: Minimum 16GB (32GB recommended for smooth model loading)
- **Storage**: 30GB+ free space (for AI models and data)
- **GPU**:
  - NVIDIA GPU with 8GB+ VRAM recommended for faster inference
  - CUDA 11.8+ or CUDA 12.1+ toolkit
  - CPU-only mode supported but slower

### System Requirements Check

```powershell
# Check Python version
python --version  # Should be 3.11+

# Check available RAM
systeminfo | findstr /C:"Total Physical Memory"

# Check GPU (if NVIDIA)
nvidia-smi

# Check disk space
wmic logicaldisk get size,freespace,caption
```

## 🚀 Quick Start

### Option 1: Using Neon (Recommended for Cloud)

#### Step 1: Create Neon Account

1. Go to [neon.tech](https://neon.tech)
2. Sign up with GitHub/Google
3. Verify your email

#### Step 2: Create New Project

1. Click **"New Project"** in Neon dashboard
2. Enter project details:
   - **Name**: `medanalyzer` (or your choice)
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15 or 16
3. Click **"Create Project"**

#### Step 3: Get Connection String

1. In your project dashboard, click **"Connection Details"**
2. Copy the **Connection String** (format):

   ```plaintext
   postgresql://username:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

3. Save this for the `.env` file

#### Step 4: Configure Database (Optional)

```sql
-- Neon automatically creates the database
-- Verify connection:
SELECT version();

-- Check available extensions:
SELECT * FROM pg_available_extensions WHERE name IN ('uuid-ossp', 'pg_trgm');
```

#### Neon Advantages

- ✅ **Serverless**: Auto-scales, auto-pauses when idle
- ✅ **Free Tier**: 0.5GB storage, 1 compute hour/month
- ✅ **Branching**: Create database branches like Git
- ✅ **Automatic Backups**: Point-in-time recovery

### Option 2: Local PostgreSQL Installation

#### Windows Installation

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer and remember the password you set for `postgres` user
3. Accept default port `5432`

#### Create Database

```powershell
# Open Command Prompt or PowerShell
psql -U postgres

# In psql prompt:
CREATE DATABASE medanalyzer;
CREATE USER meduser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE medanalyzer TO meduser;
\q
```

#### Connection String Format

```plaintext
postgresql://meduser:your_secure_password@localhost:5432/medanalyzer
```

## 📦 Installation

### Step 1: Clone Repository

```powershell
# Navigate to your projects folder
cd D:\Projects  # or your preferred location

# Clone the repository
git clone <repository-url>
cd Prushal
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# For PowerShell:
.\myenv\Scripts\Activate.ps1

# For Command Prompt:
.\myenv\Scripts\activate.bat
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will install:
# - FastAPI and Uvicorn (web framework)
# - SQLAlchemy and Psycopg2 (database)
# - Transformers and Torch (AI models)
# - Docling (document parsing)
# - Pytesseract, pypdf, pdf2image (PDF processing)
# - And other dependencies
```

### Step 4: Install Tesseract OCR

For OCR fallback functionality:

**Windows:**

1. Download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or configure in code

**Or using Chocolatey:**

```powershell
choco install tesseract
```

### Step 5: Download AI Models

```powershell
# Download MedGemma and Kokoro TTS models
python download_models.py

# This downloads:
# 1. MedGemma (unsloth/medgemma-4b-it) - ~8GB
# 2. Kokoro TTS (hexgrad/Kokoro-82M) - ~330MB
# Total time: 10-30 minutes depending on internet speed
```

### Step 6: Configure Environment Variables

Create `.env` file in project root:

```plaintext
# Database Configuration
# Option 1: Neon (Cloud)
DATABASE_URL=postgresql://username:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require

# Option 2: Local PostgreSQL
# DATABASE_URL=postgresql://meduser:your_password@localhost:5432/medanalyzer

# Option 3: SQLite (Development Only)
# DATABASE_URL=sqlite:///./medanalyzer.db

# Security Settings
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Step 7: Initialize Database

```powershell
# The application will automatically create tables on first run
# Or you can use Alembic for migrations (advanced)
```

## ▶️ Running the Application

### Development Mode

```powershell
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at http://localhost:8000
```

### Production Mode

```powershell
# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points

- **Unified Chat Interface**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Alternative API Docs**: <http://localhost:8000/redoc>
- **Health Check**: <http://localhost:8000/health>

## 🎨 Features

### 1. Unified Chat Interface

- **Dashboard Panel**: View stats (total reports, chat sessions, AI model info)
- **File Upload**: Attach PDFs, images (PNG, JPG, BMP, TIFF)
- **Text Chat**: Ask questions about medical documents
- **Combined Input**: Send files + text prompts together
- **Session Management**: Create, switch, and delete chat sessions
- **Real-time Responses**: AI-powered medical analysis with guardrails

### 2. Medical Report Analysis

- Upload text, images, or PDF medical reports
- AI-powered analysis using MedGemma Vision-Language Model
- Extract structured information (diagnoses, prescriptions, test results)
- Generate clear, understandable summaries

### 3. Multi-Language Voice Output

- Convert summaries to speech using Kokoro TTS
- High-quality, natural-sounding voices
- Support for multiple languages
- Download audio files in WAV format

### 4. Medical Guardrails

The system includes safety measures to prevent:

- ❌ Medical diagnoses
- ❌ Prescription recommendations
- ❌ Mental health advice
- ❌ Jokes and inappropriate content
- ✅ Analysis of existing reports only
- ✅ Educational information

### 5. Advanced PDF Processing

Three-tier fallback system:

1. **Primary**: Structured parsing with Docling
2. **Secondary**: PDF sanitization and retry
3. **Tertiary**: OCR fallback for scanned documents

## 🔧 API Endpoints

### Reports API

```http
POST /api/v1/reports/upload-text
Content-Type: application/json

{
  "text": "Patient blood test results...",
  "language": "en"
}
```

```http
POST /api/v1/reports/upload-image
Content-Type: multipart/form-data

file: (binary image data)
language: en
```

### Chat API

```http
POST /api/v1/chat/sessions
Content-Type: application/json

{
  "title": "My Medical Analysis"
}
```

```http
POST /api/v1/chat/sessions/{session_id}/messages
Content-Type: multipart/form-data

content: "Explain this report"
file: (optional PDF or image)
```

## 📊 Data Storage

### Database Tables

1. **reports**
   - Medical document analysis results
   - Stores raw text, summaries, file paths

2. **chat_sessions**
   - Chat conversation sessions
   - Tracks creation time and title

3. **chat_messages**
   - Individual messages (user and AI)
   - Linked to chat sessions

### File Storage

- `media/reports/` - Uploaded medical documents
- `media/audio/` - Generated TTS audio files
- `media/chat_uploads/` - Chat file attachments

## 🛡️ Security Considerations

- 🔒 **Environment Variables**: Store sensitive data in `.env`
- 🔒 **Database Encryption**: Use SSL connections for PostgreSQL
- 🔒 **Medical Guardrails**: Prevent harmful AI responses
- 🔒 **Input Validation**: Pydantic schemas validate all inputs
- ⚠️ **Development Mode**: Authentication disabled for testing
- ⚠️ **Production**: Re-enable JWT authentication for deployment

## 🐛 Troubleshooting

### Common Issues

#### Model Loading Errors

```powershell
# Clear model cache
rm -r models/
python download_models.py
```

#### Database Connection Failed

```powershell
# Test database connection
python -c "from app.db.database import engine; print(engine)"
```

#### OCR Not Working

```powershell
# Verify Tesseract installation
tesseract --version

# Set path in parser_service.py if needed
```

#### Out of Memory

- Reduce batch size in model loading
- Close other applications
- Use CPU-only mode (slower but lower memory)

## 📚 Additional Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [DOCUMENTATION.md](DOCUMENTATION.md) - Detailed technical documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [API.md](API.md) - Complete API reference

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please consult legal and medical professionals before using in production healthcare environments.

## 🆘 Support

For issues and questions:

1. Check existing documentation
2. Search closed issues
3. Open a new issue with details

---

**Built with ❤️ for better healthcare accessibility**
