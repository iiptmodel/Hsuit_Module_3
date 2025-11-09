# Complete Documentation Index

Welcome to the **Medical Report Analysis & Voice Summary System** documentation!

## 🆕 Recent changes (Nov 2025)

- **MODEL_NAME Configuration**: AI model now configurable via `.env` file (`MODEL_NAME=edwardlo12/medgemma-4b-it-Q4_K_M`)
- **Auto Model Verification**: Application checks and auto-downloads Ollama model on startup
- **Improved Testing Docs**: TESTING.md now shows report-wise results with drag-and-drop audio downloads
- Added a right-side Files drawer and Files button in the chat header for viewing uploaded files and session reports.
- Introduced a persistent theme toggle (emerald theme + light/dark) in the dashboard; preference is stored in localStorage.
- Session rename persistence: frontend now PATCHes `/api/v1/chat/sessions/{id}` and the backend persists the `title`.
- Upload handling fix: server reads uploaded bytes into a separate variable and writes files to `media/chat_uploads/` (prevents raw binary from overwriting message text).
- Guardrail behavior adjusted: flagged outputs now preserve the model's analysis and append a short disclaimer (see `app/services/summarizer_service.py` `_guardrail_validator`).
- Added `tools/repair_messages_from_reports.py` to detect/repair existing messages that contain binary dumps from older runs.

## �📚 Documentation Files

### Getting Started
1. **[README.md](README.md)** - Complete project overview, architecture, features
2. **[QUICKSTART.md](QUICKSTART.md)** - Fast 5-minute setup guide with Neon database
3. **[.env.example](.env.example)** - Environment configuration template

### Setup & Configuration
4. **[Requirements](requirements.txt)** - Python dependencies
5. **[Test System](test_system.py)** - System verification script
6. **[Download Models](download_models.py)** - AI model download script

### API & Development
7. **[API.md](API.md)** - Complete API documentation with examples
8. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

For contribution guidelines and release notes see `CONTRIBUTING.md` and `CHANGELOG.md` in the repository root.

---

## 🚀 Quick Navigation

### First Time User?
Start here: **[QUICKSTART.md](QUICKSTART.md)**

### Setting Up Database?
See: **[README.md](README.md)** → Neon Database Setup

### API Integration?
Check: **[API.md](API.md)**

### Deploying to Production?
Read: **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 📖 Key Topics

### Database Setup (Neon - Recommended)

**5-minute setup**, no local PostgreSQL needed:

1. Create free account at [neon.tech](https://neon.tech)
2. Create project named `medanalysis`
3. Copy connection string
4. Paste into `.env` file

**Detailed guide**: [README.md](README.md#database-setup)

---

### Model Storage & Configuration

**AI Model Configuration** (New!):
- Model is now configurable via `.env` file
- Default: `MODEL_NAME=edwardlo12/medgemma-4b-it-Q4_K_M`
- Application auto-verifies and downloads model on startup via Ollama

**Local Model Storage**: **`d:\Prushal\models\`** (Ollama manages this)

**Startup Verification**:
```
🔍 Checking for Ollama model: edwardlo12/medgemma-4b-it-Q4_K_M
📋 Available Ollama models: [...]
✅ Model is available
```

**Models included**:
- MedGemma 4B Q4_K_M (~2.6GB) - Medical AI analysis via Ollama
- Kokoro TTS (~330MB) - Voice generation
- Docling (~500MB) - Document parsing

**Alternative Models**:
You can switch to any Ollama-compatible model:
```env
MODEL_NAME=llama3.2:latest
MODEL_NAME=mistral:latest
MODEL_NAME=any-ollama-model
```

**Download Additional Models**:
```powershell
python scripts/download_models.py  # For TTS and Docling
ollama pull edwardlo12/medgemma-4b-it-Q4_K_M  # For AI model
```

**Full details**: [README.md](../README.md#ai-models-detailed)

---

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| Authentication endpoints | - | Disabled in development build |
| `/api/v1/reports/upload-text` | POST | Analyze text report |
| `/api/v1/reports/upload-file` | POST | Analyze image/PDF |
| `/api/v1/reports/` | GET | List all reports |
| `/api/v1/reports/{id}` | GET | Get report details |

**Full API docs**: [API.md](API.md)

---

### System Requirements

**Minimum**:
- Python 3.11+
- 16GB RAM
- 15GB disk space
- Neon database (free tier)

**Recommended**:
- Python 3.11+
- 32GB RAM
- NVIDIA GPU (8GB+ VRAM)
- 20GB disk space
- Neon database (pro tier)

**Check requirements**: Run `python test_system.py`

---

## 🔧 Common Tasks

### Install Dependencies
```powershell
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Download Models
```powershell
python download_models.py
```

### Run Development Server
```powershell
uvicorn app.main:app --reload
```

### Run Tests
```powershell
python test_system.py
```

### Generate Secret Key
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting

### Module Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'app.api.endpoints'`

**Solution**: All `__init__.py` files are already created. If error persists:
```powershell
# Verify __init__.py files exist
Get-ChildItem -Path .\app -Recurse -Filter "__init__.py"

# Reinstall app in development mode
pip install -e .
```

### Database Connection Failed
**Symptom**: `sqlalchemy.exc.OperationalError`

**Solution**:
1. Check `.env` file exists with correct `DATABASE_URL`
2. Verify Neon connection string includes `?sslmode=require`
3. Test connection: `python test_system.py`

### Models Not Loading
**Symptom**: `Model files not found`

**Solution**:
```powershell
# Re-download models
python download_models.py

# Verify models directory
Get-ChildItem -Path .\models -Recurse
```

### GPU Not Detected
**Symptom**: `CUDA not available`

**Solution**:
1. Install NVIDIA drivers
2. Install CUDA Toolkit 11.8+
3. Reinstall PyTorch:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### Out of Memory
**Symptom**: `CUDA out of memory` or `RAM exhausted`

**Solution**:
- Close other applications
- Use CPU mode (remove CUDA)
- Enable model quantization (edit `summarizer_service.py`)

---

## 📊 Project Structure

```
d:\Prushal\
├── 📄 README.md                 # Main documentation
├── 📄 QUICKSTART.md             # Quick start guide
├── 📄 API.md                    # API documentation
├── 📄 DEPLOYMENT.md             # Deployment guide
├── 📄 .env.example              # Environment template
├── 📄 requirements.txt          # Dependencies
├── 📄 download_models.py        # Model downloader
├── 📄 test_system.py            # System tests
│
├── 📁 app/                      # Main application
│   ├── main.py                  # FastAPI app
│   ├── pages.py                 # Web pages
│   ├── api/                     # API endpoints
│   │   ├── __init__.py          # API router
│   │   ├── deps.py              # Dependencies
│   │   └── endpoints/
│   │       ├── auth.py          # Authentication
│   │       └── reports.py       # Report handling
│   ├── core/                    # Core utilities
│   │   ├── config.py            # Configuration
│   │   └── security.py          # JWT & passwords
│   ├── db/                      # Database
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   ├── services/                # AI services
│   │   ├── parser_service.py   # Docling parsing
│   │   ├── summarizer_service.py # MedGemma AI
│   │   └── tts_service.py       # Kokoro TTS
│   ├── static/                  # CSS/JS
│   └── templates/               # HTML templates
│
├── 📁 models/                   # AI models (10GB)
│   ├── hub/
│   ├── transformers/
│   └── ...
│
├── 📁 media/                    # User data
│   ├── audio/                   # Generated audio
│   └── reports/                 # Uploaded reports
│
└── 📁 myenv/                    # Virtual environment
```

---

## 🎯 Use Cases

### For Developers
- **API Integration**: [API.md](API.md)
- **Local Development**: [QUICKSTART.md](QUICKSTART.md)
- **Custom Features**: Extend services in `app/services/`

### For Patients
- Upload medical reports (text, image, PDF)
- Get AI-generated explanations
- Listen to voice summaries
- Track report history

### For Healthcare Providers
- Bulk report processing (API)
- Patient education tool
- Second opinion system
- Integration with EHR systems

---

## 🔐 Security Notes

- ✅ JWT token-based authentication
- ✅ bcrypt password hashing
- ✅ SSL database connections (Neon)
- ✅ Environment variable configuration
- ⚠️ Always use HTTPS in production
- ⚠️ Change default `SECRET_KEY`
- ⚠️ Enable rate limiting for production

**Security guide**: [DEPLOYMENT.md](DEPLOYMENT.md#security)

---

## 🌐 Deployment Options

| Platform | Difficulty | Cost | GPU Support |
|----------|-----------|------|-------------|
| **Railway** | Easy | $7-25/mo | No |
| **Render** | Easy | $7-25/mo | No |
| **Azure App Service** | Medium | $50+/mo | Yes |
| **AWS EC2 (GPU)** | Hard | $100+/mo | Yes |
| **Docker** | Medium | Varies | Yes |

**Full guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📈 Performance

**Model Loading Time**:
- First startup: 30-60 seconds
- Subsequent: Cached in memory

**Processing Time**:
- Text report: 5-10 seconds
- Image report: 10-15 seconds
- PDF report: 15-30 seconds

**System Resources**:
- RAM: 8-12GB during processing
- VRAM: 6-8GB (GPU mode)
- CPU: 4+ cores recommended

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request

**Repository**: https://github.com/iiptmodel/Hsuit_Module_3

---

## 📞 Support

- **Documentation**: This directory
- **Issues**: GitHub Issues
- **API Docs**: `http://localhost:8000/docs`
- **System Test**: `python test_system.py`

---

## 📝 License

[Your License Here]

---

## 🎓 Learning Resources

### FastAPI
- Official Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial

### Neon Database
- Docs: https://neon.tech/docs
- Quick Start: https://neon.tech/docs/get-started-with-neon

### Hugging Face Transformers
- Docs: https://huggingface.co/docs/transformers
- Models: https://huggingface.co/models

### SQLAlchemy
- Docs: https://docs.sqlalchemy.org
- Tutorial: https://docs.sqlalchemy.org/en/tutorial

---

## 🔄 Version History

### v1.0.0 (Current)
- ✅ MedGemma integration
- ✅ Docling document parsing
- ✅ Kokoro TTS voice generation
- ✅ Neon database support
- ✅ JWT authentication
- ✅ Complete API

### Planned Features
- 🔮 Multi-language support (Spanish, Hindi)
- 🔮 Batch processing API
- 🔮 WebSocket real-time updates
- 🔮 Report comparison
- 🔮 Medical history tracking
- 🔮 Export to PDF

---

**Last Updated**: November 3, 2025

**Maintained by**: IIPT Model Team
