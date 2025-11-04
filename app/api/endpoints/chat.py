from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import shutil
from pathlib import Path
from uuid import uuid4
import re

from app.db import schemas, models
from app.api.deps import get_db
from app.services import chat_service, parser_service, summarizer_service, tts_service
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

MEDIA_DIR = Path("media")
CHAT_UPLOADS_DIR = MEDIA_DIR / "chat_uploads"
CHAT_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR = MEDIA_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

async def _generate_and_attach_tts(message_id: int, text: str, audio_filename: str):
    """Background task to generate TTS audio and update the ChatMessage record.

    This runs asynchronously and notifies any connected websocket clients for the
    chat session so the UI can show the audio player live without a reload.
    """
    db = SessionLocal()
    try:
        audio_path = AUDIO_DIR / audio_filename
        # Generate audio in a thread to avoid blocking the event loop
        await __import__("asyncio").to_thread(tts_service.generate_speech, text, 'en', str(audio_path))

        # Attach path (use web-accessible relative path)
        rel_path = str(Path('media') / 'audio' / audio_filename)

        msg = db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()
        if msg:
            msg.audio_file_path = rel_path
            db.add(msg)
            db.commit()
            db.refresh(msg)

            # Notify connected websocket clients for this session (if any)
            try:
                # Local import to avoid circular import at module load
                from app.api.ws import manager as ws_manager
                payload = {
                    "type": "audio_ready",
                    "message_id": msg.id,
                    "audio_file_path": rel_path
                }
                await ws_manager.send_json_to_session(msg.session_id, payload)
                logger.info(f"Notified session {msg.session_id} about audio ready for message {msg.id}")
            except Exception as e:
                logger.warning(f"Failed to notify websocket clients for message {msg.id}: {e}")
    except Exception as e:
        logger.error(f"Background TTS generation failed for message {message_id}: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/sessions", response_model=schemas.ChatSession)
def create_chat_session(
    session_data: schemas.ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Creates a new chat session."""
    new_session = models.ChatSession(title=session_data.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    logger.info(f"Created new chat session: {new_session.id}")
    return new_session


@router.get("/sessions", response_model=List[schemas.ChatSession])
def get_chat_sessions(db: Session = Depends(get_db)):
    """Gets all chat sessions."""
    sessions = db.query(models.ChatSession).order_by(
        models.ChatSession.created_at.desc()
    ).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=schemas.ChatSession)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Gets a specific chat session with all messages."""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=schemas.ChatMessage)
async def send_chat_message(
    session_id: int,
    background_tasks: BackgroundTasks,
    content: str = Form(...),
    file: Optional[UploadFile] = File(None),
    audience: str = Form('patient'),
    db: Session = Depends(get_db)
):
    """Sends a message in a chat session with optional file attachment and gets AI response."""
    
    # Verify session exists
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Process file if uploaded
    file_context = ""
    image_path_for_vlm = None
    extracted_text = None
    is_image = False
    
    if file and file.filename:
        try:
            # Save the uploaded file
            file_path_str = f"{uuid4().hex}_{file.filename.replace(' ', '_')}"
            file_save_path = CHAT_UPLOADS_DIR / file_path_str
            
            with file_save_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File uploaded: {file.filename}")
            
            # Determine file type
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            is_image = file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']
            
            if is_image:
                # For images: Pass directly to MedGemma VLM (no text extraction needed)
                logger.info("Image will be analyzed directly by MedGemma VLM")
                image_path_for_vlm = str(file_save_path)
                file_context = f"\n\n[Medical Image Attached: {file.filename}]"
            else:
                # For documents: Extract text
                logger.info("Extracting text from uploaded document")
                extracted_text = parser_service.extract_data_from_file(str(file_save_path))
                file_context = f"\n\n[Document Content]\n{extracted_text[:2000]}"  # Limit to 2000 chars
                is_image = False
            
        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            file_context = f"\n\n[Error: Could not process file {file.filename}]"
    
    # Combine user message with file context
    full_message = content + file_context
    
    # Save user message (with file indicator if applicable)
    display_content = content
    if file and file.filename:
        display_content = f"📎 {file.filename}\n\n{content}"
    
    user_message = models.ChatMessage(
        session_id=session_id,
        role="user",
        content=display_content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    logger.info(f"User message saved in session {session_id}")
    
    try:
        # Get conversation history
        history = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session_id
        ).order_by(models.ChatMessage.created_at.asc()).all()
        
        # Convert to format expected by chat service (exclude current message)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history[:-1]
        ]
        
        # Generate AI response
        logger.info(f"Generating AI response for session {session_id} — audience={audience}")

        # If a document was uploaded and audience explicitly requests doctor view, produce detailed report
        if extracted_text and audience.lower() == 'doctor':
            logger.info("Audience=doctor => generating structured detailed report.")
            try:
                ai_response_text = summarizer_service.generate_detailed_report_from_text(extracted_text, language='English')
            except Exception as e:
                logger.error(f"Detailed report generation failed: {e}", exc_info=True)
                ai_response_text = "I encountered an error generating the detailed report. Please try again."
        elif extracted_text and audience.lower() == 'patient':
            logger.info("Audience=patient => generating concise patient summary.")
            try:
                ai_response_text = summarizer_service.generate_patient_summary_from_text(extracted_text, language='English')
            except Exception as e:
                logger.error(f"Patient summary generation failed: {e}", exc_info=True)
                ai_response_text = "I encountered an error generating the summary. Please try again."
        else:
            ai_response_text = chat_service.generate_chat_response(
                conversation_history,
                full_message,  # Use full message with file context
                image_path=image_path_for_vlm  # Pass image directly to VLM
            )

        # Clean the response text by removing asterisks and extra whitespace
        ai_response_text = re.sub(r'\*+', '', ai_response_text).strip()

        # Create an assistant message placeholder so clients can show a live message
        ai_message = models.ChatMessage(
            session_id=session_id,
            role="assistant",
            content=""
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        # Notify any websocket clients that an assistant message is being streamed
        try:
            from app.api.ws import manager as ws_manager
            init_payload = {
                "type": "assistant_init",
                "message_id": ai_message.id,
                "content": ""
            }
            await ws_manager.send_json_to_session(session_id, init_payload)
        except Exception:
            # Non-fatal: websocket may not be connected
            pass

        # Stream the response to connected websocket clients in reasonable chunks
        try:
            # Simple chunking: keep chunks small so UI can progressively render text
            chunk_size = 200
            chunks = [ai_response_text[i:i+chunk_size] for i in range(0, len(ai_response_text), chunk_size)] or [ai_response_text]

            for idx, chunk in enumerate(chunks):
                # Append chunk to DB message and commit
                ai_message.content = (ai_message.content or "") + chunk
                db.add(ai_message)
                db.commit()
                db.refresh(ai_message)

                # Send delta to websocket clients
                try:
                    from app.api.ws import manager as ws_manager
                    payload = {
                        "type": "assistant_delta",
                        "message_id": ai_message.id,
                        "content": ai_message.content,
                        "final": idx == len(chunks) - 1
                    }
                    await ws_manager.send_json_to_session(session_id, payload)
                except Exception:
                    # Ignore websocket errors; clients may poll instead
                    pass

            # Schedule background TTS generation now that final content is saved
            try:
                audio_filename = f"{uuid4().hex}_response.wav"
                background_tasks.add_task(
                    _generate_and_attach_tts,
                    ai_message.id,
                    ai_message.content,
                    audio_filename,
                )
                logger.info(f"Scheduled background TTS for message {ai_message.id}")
            except Exception as e:
                logger.error(f"Failed to schedule background TTS: {e}", exc_info=True)

            logger.info(f"AI response streamed and saved in session {session_id}")
            return ai_message

        except Exception as e:
            # If streaming fails for any reason, fall back to saving the full response
            logger.exception("Streaming assistant response failed, falling back to full save: %s", e)
            ai_message.content = ai_response_text
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)
            return ai_message
        
    except Exception as e:
        logger.error(f"Error generating chat response: {e}", exc_info=True)
        # Save error message
        error_message = models.ChatMessage(
            session_id=session_id,
            role="assistant",
            content="I apologize, but I encountered an error processing your request. Please try again."
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        return error_message


@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Deletes a chat session and all its messages."""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    logger.info(f"Deleted chat session: {session_id}")
    return {"message": "Chat session deleted successfully"}


@router.get("/sessions/{session_id}/messages", response_model=List[schemas.ChatMessage])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    """Gets all messages for a specific session."""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id
    ).order_by(models.ChatMessage.created_at.asc()).all()
    
    return messages
