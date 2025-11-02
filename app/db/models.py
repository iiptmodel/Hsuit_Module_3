from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
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
    summary_text = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
