from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
import shutil
import logging
from pathlib import Path

from app.db import schemas, models
from app.api.deps import get_db
from app.services import parser_service, summarizer_service, tts_service
from uuid import uuid4

logger = logging.getLogger(__name__)

router = APIRouter()

MEDIA_DIR = Path("media")
REPORTS_DIR = MEDIA_DIR / "reports"
AUDIO_DIR = MEDIA_DIR / "audio"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-text", response_model=schemas.Report)
def upload_text_report(
    text_content: str = Form(...),
    language: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Submits and PROCESSES a new text-based report synchronously.
    The user will wait for this endpoint to finish.
    """
    # 1. Create initial report in DB
    new_report = models.Report(
        language=language,
        report_type=models.ReportType.text,
        raw_text=text_content,
        status=models.ReportStatus.processing,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    try:
        logger.info(f"Processing text report {new_report.id}")

        # 2. Run Summarizer
        logger.info("Generating summary from text...")
        summary = summarizer_service.generate_summary_from_text(
            new_report.raw_text, new_report.language
        )
        logger.info(f"Summary generated: {summary[:100]}...")

        # 3. Run TTS
        audio_file_name = f"report_{new_report.id}.mp3"
        audio_save_path = AUDIO_DIR / audio_file_name
        logger.info(f"Generating speech audio: {audio_save_path}")
        tts_service.generate_speech(
            text=summary,
            language=new_report.language,
            output_file_path=str(audio_save_path)
        )
        logger.info("Speech generation completed")

        # 4. Update report with results
        new_report.summary_text = summary
        new_report.audio_file_path = f"media/audio/{audio_file_name}"
        new_report.status = models.ReportStatus.completed
        logger.info(f"Text report {new_report.id} completed successfully")

    except Exception as e:
        # 5. Handle failure
        logger.error(f"Text report processing failed for report {new_report.id}: {e}", exc_info=True)
        new_report.status = models.ReportStatus.failed
        new_report.summary_text = f"An error occurred: {str(e)}"
    
    # 6. Commit final state
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.post("/upload-file", response_model=schemas.Report)
@router.post("/upload-image", response_model=schemas.Report)
def upload_file_report(
    language: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Submits and PROCESSES a new file report (image, PDF, or document) synchronously.
    For images (e.g., X-rays), uses MedGemma directly.
    For documents/PDFs, extracts text with Docling then summarizes.
    The user will wait for this endpoint to finish.
    """

    # 1. Save file and create initial report
    file_path_str = f"{uuid4().hex}_{file.filename.replace(' ', '_')}"
    file_save_path = REPORTS_DIR / file_path_str

    with file_save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Determine file type
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    is_image = file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']

    new_report = models.Report(
        language=language,
        report_type=models.ReportType.image,  # Keeping as image for now, could add more types
        original_file_path=str(f"media/reports/{file_path_str}"),
        status=models.ReportStatus.processing,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    try:
        logger.info(f"Processing file report {new_report.id}, file: {file.filename}, type: {'image' if is_image else 'document'}")

        if is_image:
            # 2a. For images, use MedGemma directly
            logger.info("Processing as image - using MedGemma for direct analysis")
            summary = summarizer_service.generate_summary_from_image(
                str(file_save_path), new_report.language
            )
        else:
            # 2b. For documents/PDFs, extract text with Docling then summarize
            logger.info("Processing as document - extracting text with Docling")
            extracted_results = parser_service.extract_data_from_file(
                str(file_save_path)
            )
            logger.info(f"Text extracted: {len(extracted_results)} characters")
            summary = summarizer_service.generate_summary_from_text(
                extracted_results, new_report.language
            )

        logger.info(f"Summary generated: {summary[:100]}...")

        # 3. Run TTS
        audio_file_name = f"report_{new_report.id}.mp3"
        audio_save_path = AUDIO_DIR / audio_file_name
        logger.info(f"Generating speech audio: {audio_save_path}")
        tts_service.generate_speech(
            text=summary,
            language=new_report.language,
            output_file_path=str(audio_save_path)
        )
        logger.info("Speech generation completed")

        # 4. Update report with results
        new_report.summary_text = summary
        new_report.audio_file_path = f"media/audio/{audio_file_name}"
        new_report.status = models.ReportStatus.completed
        logger.info(f"File report {new_report.id} completed successfully")

    except Exception as e:
        # 5. Handle failure
        logger.error(f"File report processing failed for report {new_report.id}: {e}", exc_info=True)
        new_report.status = models.ReportStatus.failed
        new_report.summary_text = f"An error occurred: {str(e)}"

    # 6. Commit final state
    db.commit()
    db.refresh(new_report)

    return new_report


@router.get("/", response_model=List[schemas.Report])
def get_reports(db: Session = Depends(get_db)):
    """Gets a list of all reports (no authentication)."""
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return reports


@router.get("/{report_id}", response_model=schemas.Report)
def get_report_details(
    report_id: int,
    db: Session = Depends(get_db),
):
    """Gets the status and details of a single report (no authentication)."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
    return report