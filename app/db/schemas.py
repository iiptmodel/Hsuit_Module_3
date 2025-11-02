from pydantic import BaseModel
from datetime import datetime
from app.db.models import ReportStatus, ReportType

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Report(BaseModel):
    id: int
    created_at: datetime
    language: str
    status: ReportStatus
    report_type: ReportType
    raw_text: str | None = None
    original_file_path: str | None = None
    summary_text: str | None = None
    audio_file_path: str | None = None

    class Config:
        from_attributes = True
