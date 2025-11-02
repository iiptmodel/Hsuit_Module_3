# Quick Start Guide

## First Time Setup

1. **Activate virtual environment**:
   ```powershell
   .\myenv\Scripts\activate
   ```

2. **Download models** (this will save them to `d:\Prushal\models\`):
   ```powershell
   python download_models.py
   ```
   
   This may take 10-20 minutes depending on your internet speed.
   Models will be saved to: `d:\Prushal\models\`

3. **Configure database** (create `.env` file):
   ```env
   DATABASE_URL=postgresql://user:password@localhost/medanalysis_db
   SECRET_KEY=your-secret-key-change-this
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Run the application**:
   ```powershell
   uvicorn app.main:app --reload
   ```

## Testing the Application

### 1. Register a User
Visit: `http://localhost:8000/register`

### 2. Login
Visit: `http://localhost:8000/login`

### 3. Upload a Report
Go to dashboard and upload:
- Text report (e.g., "Blood test: cholesterol 240 mg/dL")
- Image report (X-ray, scan)
- PDF document (lab results)

### 4. View Results
- See AI-generated summary
- Listen to voice explanation
- Download audio file

## Architecture Flow

```
┌──────────────┐
│ User Upload  │ (Text/Image/PDF)
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Document Parsing    │ (Docling for PDFs)
│  or Direct Input     │ (Text/Images)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   MedGemma AI        │ Analyzes medical content
│   Analysis           │ Generates explanation
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Kokoro TTS          │ Converts to voice
│  Voice Generation    │ Saves MP3 file
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Database Storage    │ Saves report + audio
└──────────────────────┘
```

## Model Storage

All AI models are stored in: **`d:\Prushal\models\`**

This includes:
- MedGemma model files (~8GB)
- Kokoro TTS models (~100MB)
- Hugging Face cache

**Note**: The `models/` directory is in `.gitignore` to avoid committing large files.

## Common Commands

```powershell
# Activate environment
.\myenv\Scripts\activate

# Install new package
pip install package-name

# Run application
uvicorn app.main:app --reload

# Run in background (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check model directory size
Get-ChildItem -Path .\models -Recurse | Measure-Object -Property Length -Sum
```
