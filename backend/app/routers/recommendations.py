"""
Recommendations Router - Manage and approve/reject recommendations (§26-27).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.analysis import Analysis
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user

router = APIRouter()


class RecommendationActionRequest(BaseModel):
    """Request to approve/reject/edit a recommendation."""
    action: str = Field(..., pattern="^(approve|reject|edit|ignore)$")
    edited_text: Optional[str] = None


@router.get("/analysis/{analysis_id}")
async def get_recommendations(analysis_id: str, user: User = Depends(get_current_user)):
    """Get all recommendations for an analysis."""
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    recs = await Recommendation.find(
        Recommendation.analysis_id == analysis_id,
        Recommendation.user_id == str(user.id),
    ).sort("sort_order").to_list()

    return [
        {
            "id": str(r.id),
            "title": r.title,
            "category": r.category,
            "status": r.status,
            "impact": r.impact,
            "reason": r.reason,
            "source_requirement": r.source_requirement,
            "section": r.section,
            "current_text": r.current_text,
            "proposed_text": r.proposed_text,
            "user_edited_text": r.user_edited_text,
            "evidence": r.evidence,
            "confidence": r.confidence,
            "factual_risk": r.factual_risk,
            "approval_required": r.approval_required,
            "jd_context": r.jd_context,
            "keyword_addressed": r.keyword_addressed,
        }
        for r in recs
    ]


@router.post("/{recommendation_id}/action")
async def recommendation_action(
    recommendation_id: str,
    data: RecommendationActionRequest,
    user: User = Depends(get_current_user),
):
    """Approve, reject, edit, or ignore a recommendation (§26)."""
    rec = await Recommendation.get(recommendation_id)
    if not rec or rec.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if data.action == "approve":
        rec.status = RecommendationStatus.APPROVED
    elif data.action == "reject":
        rec.status = RecommendationStatus.REJECTED
    elif data.action == "edit":
        if not data.edited_text:
            raise HTTPException(status_code=400, detail="Edited text is required for edit action")
        rec.status = RecommendationStatus.EDITED
        rec.user_edited_text = data.edited_text
    elif data.action == "ignore":
        rec.status = RecommendationStatus.IGNORED

    rec.reviewed_at = datetime.utcnow()
    await rec.save()

    await AuditLog(
        user_id=str(user.id),
        action=f"recommendation_{data.action}d",
        entity_type="recommendation",
        entity_id=str(rec.id),
        analysis_id=rec.analysis_id,
        details={"category": rec.category, "title": rec.title},
    ).save()

    return {"status": rec.status, "message": f"Recommendation {data.action}d successfully"}


@router.post("/analysis/{analysis_id}/approve-all")
async def approve_all_safe(analysis_id: str, user: User = Depends(get_current_user)):
    """Approve all safe (low factual risk) recommendations."""
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    recs = await Recommendation.find(
        Recommendation.analysis_id == analysis_id,
        Recommendation.user_id == str(user.id),
        Recommendation.status == RecommendationStatus.PENDING,
    ).to_list()

    approved_count = 0
    for rec in recs:
        if rec.factual_risk in ("safe", "low"):
            rec.status = RecommendationStatus.APPROVED
            rec.reviewed_at = datetime.utcnow()
            await rec.save()
            approved_count += 1

    return {
        "approved_count": approved_count,
        "remaining_count": len(recs) - approved_count,
        "message": f"Approved {approved_count} safe recommendations. {len(recs) - approved_count} require manual review.",
    }
