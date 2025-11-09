"""
Update Testing.md with Actual Results

This script reads the inference results and populates the TESTING.md file
with actual summaries and information from each processed report.
Creates a company-ready document with embedded audio players and clickable PDFs.
"""

import json
from pathlib import Path

# Directories
RESULTS_DIR = Path("D:/Prushal/testing_reports/inference_results")
TESTING_MD = Path("D:/Prushal/TESTING.md")
TESTING_REPORTS_DIR = Path("D:/Prushal/testing_reports")

def read_file_safe(file_path):
    """Safely read a file, returning empty string if not found."""
    try:
        return file_path.read_text(encoding='utf-8')
    except Exception:
        return ""

def truncate_text(text, max_chars=500):
    """Truncate text to max_chars and add ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

# Read overall results
overall_results_file = RESULTS_DIR / "overall_results.json"
overall_results = json.loads(overall_results_file.read_text(encoding='utf-8'))

print(f"Total Reports: {overall_results['total_reports']}")
print(f"Completed: {overall_results['completed']}")
print(f"Failed: {overall_results['failed']}")
print()

# Generate report sections
report_sections = []

for result in overall_results['results']:
    report_name = result['report_name']
    report_dir = RESULTS_DIR / report_name.replace('.pdf', '')
    
    print(f"Processing {report_name}...")
    
    # Read files
    summary_json = json.loads((report_dir / "summary.json").read_text(encoding='utf-8'))
    extracted_text = read_file_safe(report_dir / "extracted_text.txt")
    patient_summary = read_file_safe(report_dir / "patient_summary.txt")
    doctor_summary = read_file_safe(report_dir / "doctor_summary.txt")
    
    # Determine status emoji
    status_emoji = "✅ Completed" if summary_json.get('status') == 'completed' else "❌ Failed"
    
    # Determine report number for display
    report_num = report_name.replace('.pdf', '')
    
    # Create relative paths for linking
    pdf_path = f"testing_reports/{report_name}"
    patient_audio_path = f"testing_reports/inference_results/{report_num}/patient_audio.wav"
    doctor_audio_path = f"testing_reports/inference_results/{report_num}/doctor_audio.wav"
    
    # Create section with embedded content
    section = f"""
### Report {report_num}

**Original Report**: 📄 [{report_name}]({pdf_path})  
**Status**: {status_emoji}

---

#### 👤 Patient Summary

{patient_summary.strip()}

**🔊 Listen to Patient Summary:**

<audio controls>
  <source src="{patient_audio_path}" type="audio/wav">
  Your browser does not support the audio element. Download: <a href="{patient_audio_path}">patient_audio.wav</a>
</audio>

---

#### 👨‍⚕️ Doctor Summary

{doctor_summary.strip()}

**🔊 Listen to Doctor Summary:**

<audio controls>
  <source src="{doctor_audio_path}" type="audio/wav">
  Your browser does not support the audio element. Download: <a href="{doctor_audio_path}">doctor_audio.wav</a>
</audio>

---

"""
    
    report_sections.append(section)

# Create the full updated Testing.md
updated_content = f"""# Medical Report Analysis System - Testing Results

## Executive Summary

This document presents comprehensive testing results for the Medical Report Analysis System, demonstrating the system's capability to process medical reports and generate audience-appropriate summaries with audio playback.

**Testing Overview:**
- **Total Reports Tested**: {overall_results['total_reports']}
- **Successfully Processed**: {overall_results['completed']}
- **Failed**: {overall_results['failed']}
- **Success Rate**: {(overall_results['completed'] / overall_results['total_reports'] * 100):.1f}%

---

## System Capabilities

The Medical Report Analysis System processes medical reports through the following pipeline:

### Processing Steps

1. **📄 Text Extraction** - Uses Docling with OCR fallback for robust PDF text extraction
2. **🤖 AI Analysis** - Powered by MedGemma (medical-specialized LLM)
3. **✍️ Summary Generation** - Creates audience-specific summaries
4. **🔊 Audio Synthesis** - Converts text to natural-sounding speech using Kokoro TTS

### Dual Audience Approach

#### 👤 Patient Summaries
- **Language**: Simple, easy-to-understand, non-technical
- **Length**: 2-4 concise sentences
- **Focus**: Key findings in accessible terms
- **Safety**: Includes medical disclaimer

#### 👨‍⚕️ Doctor Summaries
- **Language**: Professional medical terminology
- **Length**: 4-6 comprehensive sentences
- **Focus**: Clinical significance, measurements, diagnostic indicators
- **Detail**: Thorough analysis with medical context

---

## Test Results

Each test report below shows:
- 📄 **Clickable link** to the original PDF
- 👤 **Patient summary** with playable audio
- 👨‍⚕️ **Doctor summary** with playable audio

{''.join(report_sections)}

## How to Run Tests

### Running the Test Script

```powershell
D:/Prushal/myenv/Scripts/python.exe scripts/run_testing_inference.py
```

This will process all PDFs in the `testing_reports/` directory and generate summaries and audio files.

---

## Technical Details

### Technology Stack

- **Text Extraction**: Docling with RapidOCR fallback
- **AI Model**: MedGemma 4B (medical-specialized language model via Ollama)
- **Text-to-Speech**: Kokoro TTS (American English)
- **Processing**: Python-based pipeline with automated audio generation

### Output Structure

```text
testing_reports/
├── [Original PDF files]
└── inference_results/
    ├── 1/, 2/, 3/, ... (one folder per report)
    │   ├── extracted_text.txt
    │   ├── patient_summary.txt
    │   ├── doctor_summary.txt
    │   ├── patient_audio.wav
    │   └── doctor_audio.wav
    └── overall_results.json
```

---

## Notes

- All testing scripts are separate from main application code
- Audio files use WAV format for maximum compatibility
- PDFs are processed automatically with no manual intervention required
- System includes safeguards and medical disclaimers in patient-facing content

---

*Testing completed: November 9, 2025*  
*System tested and validated on {overall_results['total_reports']} medical reports*
"""

# Write the updated file
TESTING_MD.write_text(updated_content, encoding='utf-8')
print(f"\n✅ Updated {TESTING_MD}")
print(f"   - {overall_results['total_reports']} reports documented")
print(f"   - {overall_results['completed']} completed, {overall_results['failed']} failed")
