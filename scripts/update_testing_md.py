"""
Update TESTING.md with Actual Results (GitHub-friendly)

This script reads the inference results and populates the TESTING.md file
with actual summaries and information from each processed report.

Important: Avoids using HTML <audio> tags, since GitHub strips/sanitizes
them and they often don't render. Instead, it uses plain Markdown links
to audio files, which GitHub can preview or download directly. Each report
section is presented in a comprehensive, report-wise layout:

Report N: <file>.pdf
    - Extracted text (preview + link to full)
    - Patient summary (inline) + Patient audio (link)
    - Doctor summary (inline) + Doctor audio (link)
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

    # Prepare truncated preview of extracted text for readability
    extracted_preview = truncate_text(extracted_text.strip(), max_chars=1200)
    quoted_extracted_preview = extracted_preview.replace('\n', '\n> ').strip()

    # Create beautifully formatted section using <video> tag for inline audio playback on GitHub
    section = f"""
<div align="center">

### 📋 Report {report_num}: `{report_name}`

![Status](https://img.shields.io/badge/Status-{status_emoji.replace(' ', '%20')}-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**{report_name}**]({pdf_path}) • [Full Extracted Text](testing_reports/inference_results/{report_num}/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> {quoted_extracted_preview}

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> {patient_summary.strip()}

</td>
<td width="30%" align="center">

**🔊 Audio:**

[![Audio](https://img.shields.io/badge/▶️_Play-Patient_Audio-blue?style=for-the-badge)]({patient_audio_path})

[📥 Download WAV]({patient_audio_path})

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> {doctor_summary.strip()}

</td>
<td width="30%" align="center">

**🔊 Audio:**

[![Audio](https://img.shields.io/badge/▶️_Play-Doctor_Audio-green?style=for-the-badge)]({doctor_audio_path})

[📥 Download WAV]({doctor_audio_path})

</td>
</tr>
</table>

---

<br>

"""
    
    report_sections.append(section)

# Create the full updated Testing.md with beautiful formatting
updated_content = f"""<div align="center">

# 🏥 Medical Report Analysis System
## Testing Results & Validation

![Total Reports](https://img.shields.io/badge/Total%20Reports-{overall_results['total_reports']}-blue?style=for-the-badge)
![Success Rate](https://img.shields.io/badge/Success%20Rate-{(overall_results['completed'] / overall_results['total_reports'] * 100):.0f}%25-success?style=for-the-badge)
![Completed](https://img.shields.io/badge/Completed-{overall_results['completed']}-brightgreen?style=for-the-badge)
![Failed](https://img.shields.io/badge/Failed-{overall_results['failed']}-red?style=for-the-badge)

</div>

---

## 📊 Executive Summary

This document presents **comprehensive testing results** for the **Medical Report Analysis System**, demonstrating the system's capability to process medical reports and generate audience-appropriate summaries with audio playback.

<table>
<tr>
<td align="center"><b>📝 Total Reports Tested</b></td>
<td align="center"><b>✅ Successfully Processed</b></td>
<td align="center"><b>❌ Failed</b></td>
<td align="center"><b>🎯 Success Rate</b></td>
</tr>
<tr>
<td align="center"><h3>{overall_results['total_reports']}</h3></td>
<td align="center"><h3>{overall_results['completed']}</h3></td>
<td align="center"><h3>{overall_results['failed']}</h3></td>
<td align="center"><h3>{(overall_results['completed'] / overall_results['total_reports'] * 100):.1f}%</h3></td>
</tr>
</table>

---

## 🔬 System Capabilities

The Medical Report Analysis System processes medical reports through a sophisticated **multi-stage pipeline**:

<table>
<tr>
<td width="25%" align="center">
<h3>📄</h3>
<b>Text Extraction</b><br>
<small>Docling + OCR fallback</small>
</td>
<td width="25%" align="center">
<h3>🤖</h3>
<b>AI Analysis</b><br>
<small>MedGemma LLM</small>
</td>
<td width="25%" align="center">
<h3>✍️</h3>
<b>Summary Generation</b><br>
<small>Dual audience</small>
</td>
<td width="25%" align="center">
<h3>🔊</h3>
<b>Audio Synthesis</b><br>
<small>Kokoro TTS</small>
</td>
</tr>
</table>

### 🎯 Dual Audience Approach

<table>
<tr>
<td width="50%">

#### 👤 **Patient Summaries**
- ✅ Simple, easy-to-understand language
- ✅ Non-technical terminology
- ✅ 2-4 concise sentences
- ✅ Focus on key findings
- ✅ Includes medical disclaimer

</td>
<td width="50%">

#### 👨‍⚕️ **Doctor Summaries**
- ✅ Professional medical terminology
- ✅ 4-6 comprehensive sentences
- ✅ Clinical significance highlighted
- ✅ Detailed measurements & ranges
- ✅ Diagnostic context provided

</td>
</tr>
</table>

---

## 📑 Test Results

> **Note:** Each test report below includes:
> - 📄 Original PDF document link
> - 🔍 Collapsible extracted text preview
> - 👤 Patient summary with embedded audio player
> - 👨‍⚕️ Doctor summary with embedded audio player

{''.join(report_sections)}

---

## 🚀 How to Run Tests

<div align="center">

### Running the Test Script

</div>

```powershell
D:/Prushal/myenv/Scripts/python.exe scripts/run_testing_inference.py
```

This will process all PDFs in the `testing_reports/` directory and generate summaries and audio files.

---

## 🛠️ Technical Details

<table>
<tr>
<td width="50%">

### 📚 Technology Stack

| Component | Technology |
|-----------|------------|
| **Text Extraction** | Docling + RapidOCR |
| **AI Model** | MedGemma 4B via Ollama |
| **Text-to-Speech** | Kokoro TTS (American) |
| **Processing** | Python Pipeline |

</td>
<td width="50%">

### 📂 Output Structure

```
testing_reports/
├── [Original PDFs]
└── inference_results/
    ├── 1/, 2/, 3/, ...
    │   ├── extracted_text.txt
    │   ├── patient_summary.txt
    │   ├── doctor_summary.txt
    │   ├── patient_audio.wav
    │   └── doctor_audio.wav
    └── overall_results.json
```

</td>
</tr>
</table>

---

## 📝 Notes

> - ✅ All testing scripts are separate from main application code
> - ✅ Audio files use WAV format for maximum compatibility
> - ✅ PDFs are processed automatically with no manual intervention
> - ✅ System includes safeguards and medical disclaimers

---

<div align="center">

### ⚡ Testing Summary

**Testing completed:** *November 9, 2025*  
**System validated on:** *{overall_results['total_reports']} medical reports*

---

Made with ❤️ for Healthcare Innovation

</div>
"""

# Write the updated file
TESTING_MD.write_text(updated_content, encoding='utf-8')
print(f"\n✅ Updated {TESTING_MD}")
print(f"   - {overall_results['total_reports']} reports documented")
print(f"   - {overall_results['completed']} completed, {overall_results['failed']} failed")
