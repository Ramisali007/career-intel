"""
Audit Log Model - Auditable trail of changes (§59).
"""

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class AuditLog(Document):
    """Audit trail for tracking all important changes."""

    user_id: str
    action: str  # document_uploaded, analysis_started, recommendation_approved, cv_optimized, cv_exported, etc.
    entity_type: str  # document, analysis, recommendation, cv_version, etc.
    entity_id: str
    details: dict = {}  # Action-specific metadata (no PII)

    # Context
    analysis_id: Optional[str] = None
    document_id: Optional[str] = None

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"
        indexes = [
            "user_id",
            "entity_type",
            "action",
        ]
