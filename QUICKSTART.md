# Quick Start Guide

## ⚡ Fast Setup (5 Minutes)

### 1. Activate Virtual Environment

```powershell
.\myenv\Scripts\Activate.ps1
```

### 2. Setup Neon Database (Free Cloud PostgreSQL)

**Why Neon?** Serverless PostgreSQL with free tier - no local installation needed!

#### Step-by-Step:

1. **Create Account**: Go to [neon.tech](https://neon.tech) and sign up (free, no credit card)

2. **Create Project**:
   - Click "New Project"
   - Name: `medanalysis`
   - Region: Select closest to you
   - Click "Create Project"

3. **Get Connection String**:
   - In dashboard, click "Connection Details"
   - Copy the connection string (looks like):
   ```
   postgresql://alex:AbC123...@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

4. **Create .env File**:
   ```powershell
   # Copy example file
   Copy-Item .env.example .env
   
   # Edit .env file and paste your Neon connection string
   notepad .env
   ```
   
   Update these lines:
   ```env
   DATABASE_URL=your-neon-connection-string-here
   SECRET_KEY=run-this-to-generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 3. Generate Secret Key

```powershell
# Generate secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy output and paste into .env as SECRET_KEY
```

### 4. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install PyTorch with CUDA (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CPU only (slower)
# pip install torch torchvision torchaudio

# Install all other dependencies
pip install -r requirements.txt
```

**Expected time**: 10-15 minutes

### 5. Download AI Models

```powershell
# This downloads ~10GB to d:\Prushal\models\
python download_models.py
```

**Expected time**: 15-30 minutes
**Models saved to**: `d:\Prushal\models\`

**What's being downloaded**:
- MedGemma (medical AI) - ~8GB
- Kokoro TTS (voice) - ~100MB
- Docling dependencies - ~500MB

### 6. Verify Setup

```powershell
# Run system tests
python test_system.py
```

You should see:
```
✅ Python Version: PASSED
✅ Dependencies: PASSED
✅ Database Connection: PASSED
✅ GPU/CUDA: PASSED (or WARNING if no GPU)
✅ SYSTEM READY!
```

### 7. Run Application

```powershell
# Start the server
uvicorn app.main:app --reload
```

**Server starts at**: `http://localhost:8000`

API-only (headless) mode

If you only want to expose the REST API (no web UI), set the `API_ONLY` environment variable before starting the server:

```powershell
$env:API_ONLY = "1"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In this mode the app will not serve static files or templates and the root `GET /` returns a small JSON health object.

---

## 🎯 First Time Usage

### 1. Open the dashboard

Visit: `http://localhost:8000/dashboard` — authentication is disabled in this development build so you can use the app immediately.

> UI notes (new)
>- Theme toggle: use the theme button in the top-right of the dashboard to switch between light and dark (choice is persisted in localStorage).
>- Files drawer: click the Files button in the chat header to open a right-side drawer listing uploaded files and session reports.
>- Rename sessions: click the pencil icon next to the session title to rename a chat (this sends a PATCH to `/api/v1/chat/sessions/{id}` and persists the change).

### 2. Upload Medical Report

Go to: `http://localhost:8000/dashboard`

**Try these examples**:

#### Text Report
```
Blood Test Results:
- Total Cholesterol: 240 mg/dL (High)
- HDL Cholesterol: 45 mg/dL (Low)
- LDL Cholesterol: 160 mg/dL (High)
- Triglycerides: 175 mg/dL (Borderline High)
```

#### Image Report
- Upload a chest X-ray image
- Or any medical scan (PNG, JPG)

#### PDF Report
- Upload lab test PDF
- Medical report document

### 4. View Results

After processing (5-15 seconds):
- ✅ AI-generated summary (patient-friendly explanation)
- ✅ Voice output (MP3 file)
- ✅ Downloadable audio
- ✅ Files drawer and session reports (open from the Files button in the chat header)

---

## 📊 Understanding the Results

### Example Input (Blood Test):
```
Glucose: 140 mg/dL
HbA1c: 6.8%
```

### AI Output:
```
Your blood sugar level is slightly elevated at 140 mg/dL, and your HbA1c 
of 6.8% indicates prediabetic range. This suggests your blood sugar has 
been higher than normal over the past 2-3 months. Consider reducing sugar 
intake, increasing physical activity, and consult your doctor for personalized 
advice.
```

### Voice Output:
- Natural female voice (American English)
- Clear pronunciation of medical terms
- ~30 second audio file

---

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
