"""
Job Description Model - Structured JD with requirements ontology (§10-11).
"""

from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class RequirementPriority(str, Enum):
    MANDATORY = "mandatory"
    HIGH = "high"
    PREFERRED = "preferred"
    NICE_TO_HAVE = "nice_to_have"


class RequirementCategory(str, Enum):
    TECHNICAL_SKILL = "technical_skill"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    PLATFORM = "platform"
    SOFT_SKILL = "soft_skill"
    CERTIFICATION = "certification"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    LEADERSHIP = "leadership"
    LANGUAGE = "language"
    RESPONSIBILITY = "responsibility"
    OTHER = "other"


class JDRequirement(BaseModel):
    """Normalized requirement object (§11)."""

    id: str
    name: str
    category: RequirementCategory = RequirementCategory.OTHER
    priority: RequirementPriority = RequirementPriority.PREFERRED
    source_text: str = ""  # Original text from JD
    normalized_form: str = ""  # Cleaned/normalized name
    aliases: list[str] = []  # e.g., ["React", "ReactJS", "React.js"]
    semantic_group: str = ""  # e.g., "Frontend Framework"
    confidence: float = 0.9
    years_required: Optional[int] = None
    is_mandatory: bool = False


class ParsedJD(BaseModel):
    """Structured representation of a parsed Job Description (§10)."""

    job_title: str = ""
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, part-time, contract
    work_arrangement: Optional[str] = None  # remote, hybrid, on-site
    seniority: Optional[str] = None  # junior, mid, senior, lead, principal
    department: Optional[str] = None
    salary_range: Optional[str] = None

    # Structured requirements
    responsibilities: list[str] = []
    required_skills: list[JDRequirement] = []
    preferred_skills: list[JDRequirement] = []
    tools_and_technologies: list[JDRequirement] = []
    certifications: list[JDRequirement] = []
    education_requirements: list[JDRequirement] = []
    experience_requirements: list[JDRequirement] = []
    domain_requirements: list[JDRequirement] = []
    soft_skill_requirements: list[JDRequirement] = []
    language_requirements: list[JDRequirement] = []

    # All requirements flat list for scoring
    all_requirements: list[JDRequirement] = []

    # Keywords
    keywords: list[str] = []
    high_value_keywords: list[str] = []

    # Raw
    raw_text: str = ""
    parser_warnings: list[str] = []


class JobDescription(Document):
    """A job description submitted for analysis."""

    user_id: str
    title: str = ""  # User-provided title or extracted job title
    raw_text: str
    parsed_jd: Optional[ParsedJD] = None

    # Status
    is_parsed: bool = False
    parsing_error: Optional[str] = None

    # Metadata
    source_url: Optional[str] = None
    company: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parsed_at: Optional[datetime] = None

    class Settings:
        name = "job_descriptions"
        indexes = [
            "user_id",
        ]
