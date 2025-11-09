# Scripts Directory

This directory contains utility scripts for the Medical Report Analysis System.

## Available Scripts

### 1. `run_testing_inference.py`

**Purpose**: Process all test reports and generate comprehensive inference results for both patient and doctor audiences.

**Usage**:
```powershell
D:/Prushal/myenv/Scripts/python.exe scripts/run_testing_inference.py
```

**What it does**:
- Processes all PDF files in `testing_reports/` directory
- Extracts text using Docling (with OCR fallback)
- Generates patient-friendly summaries
- Generates professional doctor summaries
- Creates audio files for both audiences using TTS
- Saves all outputs to `testing_reports/inference_results/`

**Output Structure**:
```
testing_reports/inference_results/
├── 1/
│   ├── extracted_text.txt      # Raw extracted text
│   ├── patient_summary.txt     # Patient-friendly summary
│   ├── doctor_summary.txt      # Professional medical summary
│   ├── patient_audio.wav       # Audio for patient
│   ├── doctor_audio.wav        # Audio for doctor
│   └── summary.json            # Metadata
└── overall_results.json         # Summary statistics
```

**Requirements**:
- Ollama running with `amsaravi/medgemma-4b-it:q8` model
- Python virtual environment activated
- All dependencies installed

---

### 2. `update_testing_md.py`

**Purpose**: Update the TESTING.md file with actual inference results.

**Usage**:
```powershell
D:/Prushal/myenv/Scripts/python.exe scripts/update_testing_md.py
```

**What it does**:
- Reads all inference results from `testing_reports/inference_results/`
- Generates comprehensive markdown documentation
- Updates `TESTING.md` in the root directory with:
  - Summary statistics
  - Individual report results
  - Patient and doctor summaries
  - File locations and sizes

**When to use**:
- After running `run_testing_inference.py`
- To regenerate documentation after re-running tests
- To update the testing documentation with fresh results

---

### 3. `download_models.py`

**Purpose**: Download required AI models for the system.

---

### 4. `migrate.py`

**Purpose**: Database migration script.

---

## Testing Workflow

1. **Run inference tests**:
   ```powershell
   D:/Prushal/myenv/Scripts/python.exe scripts/run_testing_inference.py
   ```

2. **Update documentation**:
   ```powershell
   D:/Prushal/myenv/Scripts/python.exe scripts/update_testing_md.py
   ```

3. **View results**:
   - Check `TESTING.md` in the root directory for comprehensive documentation
   - Browse `testing_reports/inference_results/` for individual report outputs

---

## Notes

- **No main project code modification**: All testing scripts are separate from the main application code
- **Isolated outputs**: All test results are stored in `testing_reports/inference_results/` subfolder
- **Reusable**: Scripts can be run multiple times to regenerate results
- **Comprehensive**: Each report gets both text summaries and audio outputs for two different audiences

---

*Last updated: November 9, 2025*
