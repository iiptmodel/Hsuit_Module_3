"""
Database Models for Med Analyzer Application

This module defines the SQLAlchemy ORM models for:
- Medical reports (text/image processing results)
- Chat sessions and message history
- Report status tracking and file management

Models:
- Report: Stores medical report data, processing status, and generated outputs
- ChatSession: Manages chat conversation sessions
- ChatMessage: Individual messages within a chat session
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ReportStatus(enum.Enum):
    """Status of report processing pipeline."""
    processing = "processing"  # Currently being processed
    completed = "completed"    # Successfully processed
    failed = "failed"          # Processing failed


class ReportType(enum.Enum):
    """Type of input document for the report."""
    text = "text"    # Plain text input
    image = "image"  # Image/PDF document


# ============================================================================
# REPORT MODEL
# ============================================================================

class Report(Base):
    """
    Medical report with AI processing results.
    
    Stores:
    - Original uploaded file information
    - Extracted text content
    - AI-generated summary
    - Text-to-speech audio output
    - Processing status and metadata
    """
    __tablename__ = "reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Processing metadata
    language = Column(String, nullable=False)
    """Language code for TTS and summarization (e.g., 'en', 'es', 'hi')."""
    
    status = Column(Enum(ReportStatus), default=ReportStatus.processing)
    """Current processing status."""
    
    report_type = Column(Enum(ReportType), nullable=False)
    """Type of input document."""
    
    # Content fields
    raw_text = Column(Text, nullable=True)
    """Extracted text from document (OCR or direct text input)."""
    
    summary_text = Column(Text, nullable=True)
    """AI-generated summary of the medical report."""
    
    # File management
    original_file_path = Column(String, nullable=True)
    """Path to uploaded file (relative to media directory)."""
    
    original_filename = Column(String, nullable=True)
    """Original filename as uploaded by user."""
    
    mime_type = Column(String, nullable=True)
    """MIME type of uploaded file (e.g., 'application/pdf', 'image/jpeg')."""
    
    audio_file_path = Column(String, nullable=True)
    """Path to generated TTS audio file."""
    
    thumbnail_path = Column(String, nullable=True)
    """Path to thumbnail image (for PDF/image reports)."""
    
    # Relationships
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    """Optional: Associate report with a chat session."""
    
    chat_session = relationship("ChatSession", back_populates="reports")


# ============================================================================
# CHAT SESSION MODEL
# ============================================================================

class ChatSession(Base):
    """
    Chat conversation session containing multiple messages.
    
    Each session represents a single conversation thread with the AI assistant.
    Sessions can be associated with medical reports for context.
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String, default="New Conversation")
    """User-friendly title for the conversation."""
    
    # Relationships
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan"  # Delete messages when session is deleted
    )
    
    reports = relationship(
        "Report",
        back_populates="chat_session",
        cascade="all, delete-orphan"  # Delete reports when session is deleted
    )


# ============================================================================
# CHAT MESSAGE MODEL
# ============================================================================

class ChatMessage(Base):
    """
    Individual message within a chat session.
    
    Stores both user questions and AI assistant responses,
    along with optional TTS audio for assistant messages.
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    role = Column(String, nullable=False)
    """Message role: 'user' or 'assistant'."""
    
    content = Column(Text, nullable=False)
    """Message text content."""
    
    audio_file_path = Column(String, nullable=True)
    """Optional: Path to TTS audio file for assistant responses."""
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

