"""
Document Model - Uploaded CVs and document versions.
Implements version control (§36) and document fingerprinting (§57).
"""

from beanie import Document as BeanieDocument, Link
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class DocumentType(str, Enum):
    CV = "cv"
    COVER_LETTER = "cover_letter"
    OTHER = "other"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


class ContactInfo(BaseModel):
    """Extracted contact information."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    website: Optional[str] = None


class CVSection(BaseModel):
    """A detected section in the CV."""

    title: str = ""
    content: str = ""
    section_type: str = ""  # summary, experience, education, skills, projects, certifications, etc.
    page_number: Optional[int] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None


class ExperienceEntry(BaseModel):
    """Structured experience entry."""

    job_title: Optional[str] = ""
    company: Optional[str] = ""
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = ""
    bullets: list[str] = []
    technologies: list[str] = []


class EducationEntry(BaseModel):
    """Structured education entry."""

    degree: Optional[str] = ""
    field: Optional[str] = None
    institution: Optional[str] = ""
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: list[str] = []


class ProjectEntry(BaseModel):
    """Structured project entry."""

    name: Optional[str] = ""
    description: Optional[str] = ""
    technologies: list[str] = []
    url: Optional[str] = None
    highlights: list[str] = []


class CertificationEntry(BaseModel):
    """Structured certification entry."""

    name: Optional[str] = ""
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiry: Optional[str] = None
    credential_id: Optional[str] = None


class ParsedCV(BaseModel):
    """Complete structured representation of a parsed CV (§8)."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = ""
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    skills: list[str] = []
    skill_categories: dict[str, list[str]] = {}  # e.g. {"Languages": ["Python", "JS"]}
    projects: list[ProjectEntry] = []
    certifications: list[CertificationEntry] = []
    achievements: list[str] = []
    languages: list[str] = []
    links: list[str] = []
    sections: list[CVSection] = []
    raw_text: Optional[str] = ""
    page_count: int = 0
    formatting_signals: list[str] = []  # multi-column, tables, graphics, etc.
    parser_warnings: list[str] = []


class Document(BeanieDocument):
    """An uploaded document (CV/resume)."""

    user_id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    extension: str
    content_hash: str  # SHA-256 for deduplication (§57)
    document_type: DocumentType = DocumentType.CV
    status: DocumentStatus = DocumentStatus.UPLOADED

    # Parsed content
    parsed_cv: Optional[ParsedCV] = None
    raw_text: Optional[str] = None

    # OCR
    is_scanned: bool = False
    ocr_applied: bool = False
    ocr_confidence: Optional[float] = None

    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    parsed_at: Optional[datetime] = None
    last_analyzed_at: Optional[datetime] = None

    class Settings:
        name = "documents"
        indexes = [
            "user_id",
            "content_hash",
        ]
