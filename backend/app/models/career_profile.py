"""
Caeer Profile Model - Master Career Profile (§6-7).
Source of truth for candidate information with provenance tracking.
"""

from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SkillProvenance(BaseModel):
    """Provenance tracking for a skill (§6, §76)."""

    source: str  # CV, USER_PROFILE, USER_APPROVED_INPUT
    source_document_id: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    evidence_text: str = ""
    confidence: str = "high"  # high, medium, low
    added_at: datetime = Field(default_factory=datetime.utcnow)


class ProfileSkill(BaseModel):
    """A skill in the career profile with provenance."""

    name: str
    normalized_name: str = ""
    category: str = ""  # programming_language, framework, tool, etc.
    proficiency: Optional[str] = None  # expert, advanced, intermediate, beginner
    years: Optional[int] = None
    last_used: Optional[str] = None
    provenance: list[SkillProvenance] = []


class ProfileExperience(BaseModel):
    """Experience entry in career profile."""

    job_title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: str = ""
    responsibilities: list[str] = []
    achievements: list[str] = []
    technologies: list[str] = []
    provenance_source: str = "cv"


class ProfileEducation(BaseModel):
    """Education entry in career profile."""

    degree: str
    field: Optional[str] = None
    institution: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    provenance_source: str = "cv"


class ProfileProject(BaseModel):
    """Project in career profile."""

    name: str
    description: str = ""
    technologies: list[str] = []
    url: Optional[str] = None
    highlights: list[str] = []
    provenance_source: str = "cv"


class ProfileCertification(BaseModel):
    """Certification in career profile."""

    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    provenance_source: str = "cv"


class CareerProfile(Document):
    """Master Career Profile - single source of truth (§6)."""

    user_id: str

    # Personal
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    website: Optional[str] = None

    # Professional
    professional_summary: str = ""
    headline: str = ""
    target_roles: list[str] = []
    target_industries: list[str] = []

    # Structured data
    skills: list[ProfileSkill] = []
    experience: list[ProfileExperience] = []
    education: list[ProfileEducation] = []
    projects: list[ProfileProject] = []
    certifications: list[ProfileCertification] = []
    achievements: list[str] = []
    languages: list[str] = []
    publications: list[str] = []
    volunteer_work: list[str] = []
    leadership: list[str] = []
    domain_experience: list[str] = []
    awards: list[str] = []

    # Source tracking
    source_document_ids: list[str] = []  # Documents that contributed to this profile
    last_enriched_from: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "career_profiles"
        indexes = [
            "user_id",
        ]
