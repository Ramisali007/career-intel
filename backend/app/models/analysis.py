"""
Analysis Model - Analysis session linking CV + JD with processing state machine (§54).
"""

from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class AnalysisStatus(str, Enum):
    """Processing state machine (§54)."""
    QUEUED = "queued"
    PARSING_CV = "parsing_cv"
    PARSING_JD = "parsing_jd"
    EXTRACTING_REQUIREMENTS = "extracting_requirements"
    EXTRACTING_EVIDENCE = "extracting_evidence"
    NORMALIZING = "normalizing"
    MATCHING = "matching"
    SCORING = "scoring"
    SCORING_ATS = "scoring_ats"
    SCORING_QUALITY = "scoring_quality"
    GENERATING_RECOMMENDATIONS = "generating_recommendations"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    OPTIMIZING = "optimizing"
    VERIFYING = "verifying"
    RESCORING = "rescoring"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class MatchClassification(str, Enum):
    """Match classification for requirements (§15)."""
    EXACT_MATCH = "exact_match"
    STRONG_MATCH = "strong_match"
    PARTIAL_MATCH = "partial_match"
    RELATED_MATCH = "related_match"
    WEAK_MATCH = "weak_match"
    MISSING = "missing"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class EvidenceSource(str, Enum):
    """Evidence source types (§5)."""
    CV = "cv"
    USER_PROFILE = "user_profile"
    USER_APPROVED_INPUT = "user_approved_input"
    JD = "jd"
    INFERENCE = "inference"
    MODEL_GENERATED = "model_generated"

    @classmethod
    def _missing_(cls, value):
        return cls.CV


class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"

    @classmethod
    def _missing_(cls, value):
        return cls.NONE


class SkillEvidence(BaseModel):
    """Evidence for a skill from the CV (§14)."""

    skill_name: str
    normalized_name: str = ""
    evidence_text: str = ""  # Quote from CV
    evidence_type: str = ""  # Professional Experience, Education, Project, etc.
    source: EvidenceSource = EvidenceSource.CV
    strength: EvidenceStrength = EvidenceStrength.MODERATE
    years: Optional[float] = None
    recency: Optional[str] = None  # current, recent, older
    role: Optional[str] = None
    project: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    confidence: float = 0.8


class RequirementMatch(BaseModel):
    """Match result for a single JD requirement (§15-16)."""

    requirement_id: str
    requirement_name: str
    requirement_category: str = ""
    requirement_priority: str = "preferred"
    requirement_source_text: str = ""

    # Match result
    classification: MatchClassification = MatchClassification.UNKNOWN
    match_score: float = 0.0  # 0-100

    # CV evidence
    cv_evidence: list[SkillEvidence] = []
    evidence_summary: str = ""

    # Context
    experience_relevance: float = 0.0
    seniority_alignment: float = 0.0

    confidence: float = 0.8
    explanation: str = ""
    recommended_action: str = ""


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown for explainability (§18)."""

    dimension: str
    score: float  # 0-100
    weight: float
    weighted_score: float
    details: str = ""
    evidence_count: int = 0


class KeywordIntelligence(BaseModel):
    """Keyword classification (§22)."""

    keyword: str
    status: str  # FOUND, PARTIAL, MISSING, LOW-CONFIDENCE, OVERUSED, HIGH-VALUE
    jd_context: str = ""
    cv_context: str = ""
    importance: str = "medium"  # high, medium, low
    recommendation: str = ""


class AnalysisScores(BaseModel):
    """All three independent scores (§17, §20, §21)."""

    # Job Match Score
    job_match_score: float = 0.0
    job_match_breakdown: list[ScoreBreakdown] = []
    job_match_confidence: str = "medium"  # high, medium, low

    # ATS Compatibility Score
    ats_score: float = 0.0
    ats_breakdown: list[ScoreBreakdown] = []
    ats_warnings: list[str] = []

    # CV Quality Score
    quality_score: float = 0.0
    quality_breakdown: list[ScoreBreakdown] = []


class Analysis(Document):
    """An analysis session comparing a CV against a Job Description."""

    user_id: str
    document_id: str
    job_description_id: str
    status: AnalysisStatus = AnalysisStatus.QUEUED
    current_step: str = ""
    progress_percentage: int = 0

    # Failed stage tracking (§96)
    failed_stage: Optional[str] = None
    error_message: Optional[str] = None
    stages_completed: list[str] = []

    # Results
    requirement_matches: list[RequirementMatch] = []
    keyword_intelligence: list[KeywordIntelligence] = []
    scores: Optional[AnalysisScores] = None

    # Strengths and gaps
    strengths: list[str] = []
    critical_gaps: list[str] = []
    improvement_areas: list[str] = []

    # Before/After (§37)
    original_scores: Optional[AnalysisScores] = None
    optimized_scores: Optional[AnalysisScores] = None

    # Processing metadata
    ai_provider_used: str = ""
    ai_model_used: str = ""
    processing_time_seconds: Optional[float] = None

    # CV version references
    original_cv_version_id: Optional[str] = None
    optimized_cv_version_id: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Settings:
        name = "analyses"
        indexes = [
            "user_id",
            "document_id",
            "job_description_id",
        ]
