from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base

class ReportStatus(enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ReportType(enum.Enum):
    text = "text"
    image = "image"

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    language = Column(String, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.processing)
    report_type = Column(Enum(ReportType), nullable=False)

    raw_text = Column(Text, nullable=True)
    original_file_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    summary_text = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)

    # New: associate report with a chat session (nullable for backward compatibility)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    chat_session = relationship("ChatSession", back_populates="reports")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String, default="New Conversation")
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    # Relationship to reports
    reports = relationship("Report", back_populates="chat_session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    # Optional path to TTS audio generated for assistant responses
    audio_file_path = Column(String, nullable=True)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
