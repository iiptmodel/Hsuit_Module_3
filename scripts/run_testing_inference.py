"""
Testing Inference Script

This script processes all PDF reports in the testing_reports directory and generates:
1. Text summaries for both Patient and Doctor audiences
2. Audio files for both audiences

Results are saved in testing_reports/inference_results/ organized by report name.

Usage:
    python scripts/run_testing_inference.py
"""

import os
import sys
import logging
from pathlib import Path
import json
import subprocess

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import parser_service, summarizer_service, tts_service
from app.services.ollama_client import chat_with_retries

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directories
TESTING_REPORTS_DIR = Path("D:/Prushal/testing_reports")
RESULTS_DIR = TESTING_REPORTS_DIR / "inference_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Static background image for videos
AUDIO_BG_IMAGE = Path("D:/Prushal/scripts/pngtree-pure-white-minimalist-background-wallpaper-picture-image_1219011.jpg")


def convert_audio_to_video(audio_file: Path, video_file: Path) -> bool:
    """
    Convert WAV audio file to MP4 video with static background image.
    
    Args:
        audio_file: Path to input WAV file
        video_file: Path to output MP4 file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Verify audio file exists and has content
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return False
        
        if audio_file.stat().st_size == 0:
            logger.error(f"Audio file is empty: {audio_file}")
            return False
            
        logger.info(f"Converting audio ({audio_file.stat().st_size} bytes) to video...")
        
        # FFmpeg command to create video from audio + static image
        cmd = [
            'ffmpeg',
            '-y',
            '-loop', '1',
            '-i', str(AUDIO_BG_IMAGE),
            '-i', str(audio_file),
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '256k',  # Increased bitrate for better quality
            '-ar', '48000',  # Higher sample rate
            '-ac', '2',  # Stereo audio
            '-af', 'volume=5.0',  # Boost audio volume by 3x
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-map', '0:v:0',  # Take video from image
            '-map', '1:a:0',  # Take audio from WAV
            '-vf', 'scale=1280:720',
            '-movflags', '+faststart',  # Enable streaming
            str(video_file)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Log FFmpeg output for debugging
        if result.stderr:
            logger.info(f"FFmpeg output: {result.stderr}")
        
        # Verify output file was created
        if not video_file.exists():
            logger.error("Video file was not created")
            return False
            
        logger.info(f"Video created successfully ({video_file.stat().st_size} bytes)")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Video conversion error: {e}")
        return False


def generate_doctor_summary(extracted_text: str, language: str = 'English') -> str:
    """
    Generate a detailed, professional summary for healthcare professionals.
    """
    logger.info(f"Generating doctor-oriented summary (text length={len(extracted_text)})")
    try:
        system_prompt = (
            "You are a medical assistant providing detailed analysis for healthcare professionals. "
            f"Analyze the following medical report text in {language}. "
            "Provide a comprehensive summary including:\n"
            "1. Key findings and observations\n"
            "2. Notable measurements or test results\n"
            "3. Clinical significance\n"
            "4. Any areas requiring attention\n"
            "Be thorough and use appropriate medical terminology. Aim for 4-6 sentences."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": extracted_text}
        ]

        resp = chat_with_retries(
            model='edwardlo12/medgemma-4b-it-Q4_K_M',
            messages=messages,
            options={"temperature": 0.0, "num_predict": 400}
        )
        summary = resp.get('message', {}).get('content', '')
        return summary
    except Exception as e:
        logger.error(f"Doctor summary generation failed: {e}", exc_info=True)
        return f"Error generating doctor summary: {str(e)}"


def generate_patient_summary(extracted_text: str, language: str = 'English') -> str:
    """
    Generate a patient-friendly summary using the existing summarizer service.
    """
    logger.info(f"Generating patient-oriented summary (text length={len(extracted_text)})")
    try:
        return summarizer_service.generate_summary_from_text(extracted_text, language)
    except Exception as e:
        logger.error(f"Patient summary generation failed: {e}", exc_info=True)
        return f"Error generating patient summary: {str(e)}"


def process_report(pdf_path: Path, report_name: str):
    """
    Process a single PDF report and generate outputs for both audiences.
    """
    logger.info(f"Processing report: {report_name}")
    
    # Create output directory for this report
    report_output_dir = RESULTS_DIR / report_name.replace('.pdf', '')
    report_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Extract text from PDF
        logger.info(f"Extracting text from {pdf_path}")
        extracted_text = parser_service.extract_data_from_file(str(pdf_path))
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            logger.warning(f"Insufficient text extracted from {report_name}")
            extracted_text = "Unable to extract sufficient text from this report."
        
        # Save extracted text
        text_file = report_output_dir / "extracted_text.txt"
        text_file.write_text(extracted_text, encoding='utf-8')
        logger.info(f"Saved extracted text to {text_file}")
        
        # Step 2: Generate Patient Summary
        logger.info("Generating patient summary...")
        patient_summary = generate_patient_summary(extracted_text, language='English')
        patient_summary_file = report_output_dir / "patient_summary.txt"
        patient_summary_file.write_text(patient_summary, encoding='utf-8')
        logger.info(f"Saved patient summary to {patient_summary_file}")
        
        # Step 3: Generate Doctor Summary
        logger.info("Generating doctor summary...")
        doctor_summary = generate_doctor_summary(extracted_text, language='English')
        doctor_summary_file = report_output_dir / "doctor_summary.txt"
        doctor_summary_file.write_text(doctor_summary, encoding='utf-8')
        logger.info(f"Saved doctor summary to {doctor_summary_file}")
        
        # Step 4: Generate Patient Audio
        logger.info("Generating patient audio...")
        patient_audio_file = report_output_dir / "patient_audio.wav"
        patient_video_file = report_output_dir / "patient_audio.mp4"
        try:
            tts_service.generate_speech(
                text=patient_summary,
                language='en',
                output_file_path=str(patient_audio_file)
            )
            logger.info(f"Saved patient audio to {patient_audio_file}")
            
            # Convert WAV to MP4 with static background
            convert_audio_to_video(patient_audio_file, patient_video_file)
            logger.info(f"Converted to video: {patient_video_file}")
        except Exception as e:
            logger.error(f"Failed to generate patient audio: {e}")
            patient_audio_file.write_text(f"Audio generation failed: {str(e)}", encoding='utf-8')
        
        # Step 5: Generate Doctor Audio
        logger.info("Generating doctor audio...")
        doctor_audio_file = report_output_dir / "doctor_audio.wav"
        doctor_video_file = report_output_dir / "doctor_audio.mp4"
        try:
            tts_service.generate_speech(
                text=doctor_summary,
                language='en',
                output_file_path=str(doctor_audio_file)
            )
            logger.info(f"Saved doctor audio to {doctor_audio_file}")
            
            # Convert WAV to MP4 with static background
            convert_audio_to_video(doctor_audio_file, doctor_video_file)
            logger.info(f"Converted to video: {doctor_video_file}")
        except Exception as e:
            logger.error(f"Failed to generate doctor audio: {e}")
            doctor_audio_file.write_text(f"Audio generation failed: {str(e)}", encoding='utf-8')
        
        # Step 6: Create summary JSON
        summary_data = {
            "report_name": report_name,
            "extracted_text_length": len(extracted_text),
            "patient_summary_length": len(patient_summary),
            "doctor_summary_length": len(doctor_summary),
            "files": {
                "extracted_text": str(text_file.relative_to(TESTING_REPORTS_DIR)),
                "patient_summary": str(patient_summary_file.relative_to(TESTING_REPORTS_DIR)),
                "doctor_summary": str(doctor_summary_file.relative_to(TESTING_REPORTS_DIR)),
                "patient_audio": str(patient_audio_file.relative_to(TESTING_REPORTS_DIR)),
                "doctor_audio": str(doctor_audio_file.relative_to(TESTING_REPORTS_DIR))
            },
            "status": "completed"
        }
        
        summary_json = report_output_dir / "summary.json"
        summary_json.write_text(json.dumps(summary_data, indent=2), encoding='utf-8')
        logger.info(f"Saved summary metadata to {summary_json}")
        
        logger.info(f"✓ Successfully processed {report_name}")
        return summary_data
        
    except Exception as e:
        logger.error(f"Failed to process {report_name}: {e}", exc_info=True)
        error_data = {
            "report_name": report_name,
            "status": "failed",
            "error": str(e)
        }
        error_json = report_output_dir / "summary.json"
        error_json.write_text(json.dumps(error_data, indent=2), encoding='utf-8')
        return error_data


def main():
    """
    Main function to process all test reports.
    """
    logger.info("=" * 80)
    logger.info("Starting Testing Inference Run")
    logger.info("=" * 80)
    
    # Find all PDF files in testing_reports directory
    pdf_files = sorted(TESTING_REPORTS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.error("No PDF files found in testing_reports directory!")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF reports to process")
    
    results = []
    for idx, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        logger.info("-" * 80)
        result = process_report(pdf_path, pdf_path.name)
        results.append(result)
    
    # Save overall results
    overall_results = {
        "total_reports": len(pdf_files),
        "completed": len([r for r in results if r.get('status') == 'completed']),
        "failed": len([r for r in results if r.get('status') == 'failed']),
        "results": results
    }
    
    results_file = RESULTS_DIR / "overall_results.json"
    results_file.write_text(json.dumps(overall_results, indent=2), encoding='utf-8')
    
    logger.info("\n" + "=" * 80)
    logger.info("Testing Inference Complete!")
    logger.info(f"Total Reports: {overall_results['total_reports']}")
    logger.info(f"Completed: {overall_results['completed']}")
    logger.info(f"Failed: {overall_results['failed']}")
    logger.info(f"Results saved to: {RESULTS_DIR}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()