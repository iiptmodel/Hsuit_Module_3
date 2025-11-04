from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import shutil
import logging
from pathlib import Path

from app.db import schemas, models
from app.api.deps import get_db
from app.services import parser_service, summarizer_service, tts_service
from app.utils.text_utils import sanitize_text
from app.utils import events as events
import asyncio
import json
from uuid import uuid4

logger = logging.getLogger(__name__)

router = APIRouter()

MEDIA_DIR = Path("media")
REPORTS_DIR = MEDIA_DIR / "reports"
AUDIO_DIR = MEDIA_DIR / "audio"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-text", response_model=schemas.Report)
async def upload_text_report(
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

        # Create event queue for real-time UI updates
        events.create_queue(new_report.id)
        events.publish(new_report.id, {"status": "started", "stage": "created"})

        # 2. Run Summarizer (offload blocking work to thread)
        logger.info("Generating summary from text...")
        events.publish(new_report.id, {"status": "in-progress", "stage": "summarizing"})

        cleaned = sanitize_text(new_report.raw_text)

        def _run_text_pipeline(text, language, report_id):
            # This runs in a background thread
            events.publish(report_id, {"status": "in-progress", "stage": "summarize_start"})
            summary = summarizer_service.generate_summary_from_text(text, language)
            events.publish(report_id, {"status": "in-progress", "stage": "summarize_done"})

            # TTS
            events.publish(report_id, {"status": "in-progress", "stage": "tts_start"})
            audio_file_name = f"report_{report_id}.wav"
            audio_save_path = AUDIO_DIR / audio_file_name
            tts_service.generate_speech(text=summary, language=language, output_file_path=str(audio_save_path))
            events.publish(report_id, {"status": "in-progress", "stage": "tts_done", "audio": str(audio_save_path)})

            return summary, audio_file_name

        summary, audio_file_name = await asyncio.to_thread(_run_text_pipeline, cleaned, new_report.language, new_report.id)

        # 4. Update report with results
        new_report.summary_text = summary
        new_report.audio_file_path = f"media/audio/{audio_file_name}"
        new_report.status = models.ReportStatus.completed
        events.publish(new_report.id, {"status": "completed", "stage": "done", "audio": new_report.audio_file_path})

        logger.info(f"Text report {new_report.id} completed successfully")

    except Exception as e:
        # 5. Handle failure
        logger.error(f"Text report processing failed for report {new_report.id}: {e}", exc_info=True)
        new_report.status = models.ReportStatus.failed
        new_report.summary_text = f"An error occurred: {str(e)}"
        events.publish(new_report.id, {"status": "failed", "error": str(e)})
    
    # 6. Commit final state
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.post("/upload-files", response_model=List[schemas.Report])
async def upload_files_report(
    language: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    Submits and PROCESSES a new file report (image, PDF, or document) synchronously.
    For images (e.g., X-rays), uses MedGemma directly.
    For documents/PDFs, extracts text with Docling then summarizes.
    The user will wait for this endpoint to finish.
    """

    # 1. Save file and create initial report
    results: List[models.Report] = []

    for file in files:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail=f"File {file.filename} too large. Maximum size is 10MB.")
        
        file_path_str = f"{uuid4().hex}_{file.filename.replace(' ', '_')}"
        file_save_path = REPORTS_DIR / file_path_str

        with file_save_path.open("wb") as buffer:
            buffer.write(file_content)

        # Determine file type: prefer content_type, fallback to extension
        content_type = getattr(file, "content_type", "") or ""
        if content_type.startswith("image/"):
            is_image = True
        else:
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            is_image = file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']

        new_report = models.Report(
            language=language,
            report_type=models.ReportType.image if is_image else models.ReportType.text,
            original_file_path=str(f"media/reports/{file_path_str}"),
            status=models.ReportStatus.processing,
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        try:
            logger.info(f"Processing file report {new_report.id}, file: {file.filename}, type: {'image' if is_image else 'document'}")

            # Create event queue for UI real-time updates
            events.create_queue(new_report.id)
            events.publish(new_report.id, {"status": "started", "stage": "created"})

            def _process_file(path, is_img, language, report_id):
                logger.debug(f"Processing file {path} for report {report_id}, is_image={is_img}")
                # Runs in thread
                try:
                    events.publish(report_id, {"status": "in-progress", "stage": "processing_file"})
                    if is_img:
                        events.publish(report_id, {"status": "in-progress", "stage": "image_analysis_start"})
                        summary = summarizer_service.generate_summary_from_image(str(path), language)
                        events.publish(report_id, {"status": "in-progress", "stage": "image_analysis_done"})
                    else:
                        events.publish(report_id, {"status": "in-progress", "stage": "doc_extract_start"})
                        extracted_results = parser_service.extract_data_from_file(str(path))
                        events.publish(report_id, {"status": "in-progress", "stage": "doc_extract_done", "chars": len(extracted_results)})
                        cleaned = sanitize_text(extracted_results)
                        events.publish(report_id, {"status": "in-progress", "stage": "summarize_start"})
                        summary = summarizer_service.generate_summary_from_text(cleaned, language)
                        events.publish(report_id, {"status": "in-progress", "stage": "summarize_done"})

                    # TTS
                    events.publish(report_id, {"status": "in-progress", "stage": "tts_start"})
                    audio_file_name = f"report_{report_id}.wav"
                    audio_save_path = AUDIO_DIR / audio_file_name
                    tts_service.generate_speech(text=summary, language=language, output_file_path=str(audio_save_path))
                    events.publish(report_id, {"status": "in-progress", "stage": "tts_done", "audio": str(audio_save_path)})

                    return {"summary": summary, "audio": audio_file_name}
                except Exception as e:
                    events.publish(report_id, {"status": "failed", "error": str(e)})
                    raise

            result = await asyncio.to_thread(_process_file, file_save_path, is_image, new_report.language, new_report.id)

            summary = result["summary"]
            audio_file_name = result["audio"]

            # Update report with results
            new_report.summary_text = summary
            new_report.audio_file_path = f"media/audio/{audio_file_name}"
            new_report.status = models.ReportStatus.completed
            events.publish(new_report.id, {"status": "completed", "stage": "done", "audio": new_report.audio_file_path})
            logger.info(f"File report {new_report.id} completed successfully")

        except Exception as e:
            # Handle failure
            logger.error(f"File report processing failed for report {new_report.id}: {e}", exc_info=True)
            new_report.status = models.ReportStatus.failed
            new_report.summary_text = f"An error occurred: {str(e)}"

        # Commit final state
        db.commit()
        db.refresh(new_report)
        results.append(new_report)

    return results


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


@router.get("/{report_id}/events")
async def report_events(report_id: int):
    """Server-Sent Events endpoint that streams processing events for a report."""
    q = events.get_queue(report_id)
    if q is None:
        # Create an empty queue so clients can connect before processing starts
        q = events.create_queue(report_id)

    async def event_generator():
        try:
            while True:
                msg = await q.get()
                # Ensure message is JSON serializable
                try:
                    data = json.dumps(msg)
                except Exception:
                    data = json.dumps({"status": "update", "raw": str(msg)})
                yield f"data: {data}\n\n"
                # Optionally break on terminal states
                if isinstance(msg, dict) and msg.get("status") in ("completed", "failed"):
                    break
        finally:
            # Clean up the queue when the client disconnects or processing completes
            events.remove_queue(report_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")