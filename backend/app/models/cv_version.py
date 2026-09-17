"""
CV Version Model - Generated CV versions with audit trail (§36, §59).
"""

from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

from app.models.document import ParsedCV


class VersionType(str, Enum):
    ORIGINAL = "original"
    OPTIMIZED = "optimized"
    TAILORED = "tailored"
    MANUAL = "manual"


class VerificationStatus(str, Enum):
    NOT_VERIFIED = "not_verified"
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    FAILED = "failed"


class ClaimVerification(BaseModel):
    """Verification result for a single claim (§39)."""

    claim_text: str
    status: str  # VERIFIED, PARTIALLY_VERIFIED, UNSUPPORTED, CONFLICTING
    evidence: str = ""
    source: str = ""  # CV, USER_PROFILE, etc.
    confidence: float = 0.0


class CVVersion(Document):
    """A version of the CV - never overwrite, maintain history (§36)."""

    user_id: str
    document_id: str  # Original document
    analysis_id: Optional[str] = None
    job_description_id: Optional[str] = None

    # Version info
    version: int = 1
    version_type: VersionType = VersionType.ORIGINAL
    parent_version_id: Optional[str] = None

    # Content
    parsed_cv: Optional[ParsedCV] = None
    content_hash: str = ""

    # Scores
    job_match_score: Optional[float] = None
    ats_score: Optional[float] = None
    quality_score: Optional[float] = None

    # Verification (§39-40)
    verification_status: VerificationStatus = VerificationStatus.NOT_VERIFIED
    claim_verifications: list[ClaimVerification] = []
    quality_audit_passed: bool = False

    # Changes (§59 audit trail)
    approved_recommendation_ids: list[str] = []
    rejected_recommendation_ids: list[str] = []
    changes_summary: list[str] = []

    # Export
    exported_pdf_path: Optional[str] = None
    exported_docx_path: Optional[str] = None
    template_used: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    exported_at: Optional[datetime] = None

    class Settings:
        name = "cv_versions"
        indexes = [
            "user_id",
            "document_id",
            "analysis_id",
        ]
