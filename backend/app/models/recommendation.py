"""
Recommendation Model - Actionable recommendations with approval workflow (§24-27).
"""

from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class RecommendationCategory(str, Enum):
    CRITICAL = "critical"
    HIGH_IMPACT = "high_impact"
    HIGH = "high_impact"
    MEDIUM = "medium"
    OPTIONAL = "optional"
    LOW = "optional"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_lower = value.lower().strip()
            if val_lower in ("high", "high_impact"):
                return cls.HIGH_IMPACT
            if val_lower in ("critical", "urgent"):
                return cls.CRITICAL
            if val_lower in ("medium", "moderate"):
                return cls.MEDIUM
            if val_lower in ("optional", "low"):
                return cls.OPTIONAL
        return cls.MEDIUM


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    IGNORED = "ignored"


class FactualRisk(str, Enum):
    """Factual risk assessment for a recommendation."""
    SAFE = "safe"  # Only reorganizes/rephrases existing CV content
    LOW = "low"  # Minor inference from existing evidence
    MEDIUM = "medium"  # Moderate inference, user should verify
    HIGH = "high"  # Could introduce unverified claims, needs approval
    BLOCKED = "blocked"  # Would fabricate information, cannot be applied

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_lower = value.lower().strip()
            if val_lower in ("safe", "none"):
                return cls.SAFE
            if val_lower in ("low",):
                return cls.LOW
            if val_lower in ("medium", "moderate"):
                return cls.MEDIUM
            if val_lower in ("high", "critical"):
                return cls.HIGH
            if val_lower in ("blocked", "unsupported"):
                return cls.BLOCKED
        return cls.SAFE


class Recommendation(Document):
    """A single actionable recommendation (§24-25)."""

    user_id: str
    analysis_id: str

    # Core
    title: str
    category: RecommendationCategory = RecommendationCategory.MEDIUM
    status: RecommendationStatus = RecommendationStatus.PENDING

    # What
    impact: str = ""  # What improvement this would create
    reason: str = ""  # Why this matters
    source_requirement: str = ""  # Which JD requirement drives this
    source_requirement_id: Optional[str] = None

    # Change details (§27)
    current_text: str = ""  # Original CV text
    proposed_text: str = ""  # Suggested replacement
    user_edited_text: Optional[str] = None  # If user edits the suggestion
    section: str = ""  # Which CV section (summary, experience, skills, etc.)

    # Evidence & Risk (§5, §25)
    evidence: list[str] = []  # Evidence supporting this recommendation
    evidence_sources: list[str] = []  # CV, USER_PROFILE, etc.
    confidence: float = 0.8
    factual_risk: FactualRisk = FactualRisk.SAFE
    approval_required: bool = True

    # JD context
    jd_context: str = ""  # Relevant JD text
    keyword_addressed: Optional[str] = None

    # Order
    sort_order: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None

    class Settings:
        name = "recommendations"
        indexes = [
            "user_id",
            "analysis_id",
        ]
