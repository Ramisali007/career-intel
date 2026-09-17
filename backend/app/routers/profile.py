"""
Profile Router - Master Career Profile management (§6-7, §31).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.models.career_profile import CareerProfile, ProfileSkill, SkillProvenance
from app.security.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_profile(user: User = Depends(get_current_user)):
    """Get or create the user's master career profile."""
    profile = await CareerProfile.find_one(CareerProfile.user_id == str(user.id))

    if not profile:
        profile = CareerProfile(
            user_id=str(user.id),
            full_name=user.full_name,
        )
        await profile.save()

    return {
        "id": str(profile.id),
        "full_name": profile.full_name or user.full_name,
        "headline": profile.headline or "",
        "professional_summary": profile.professional_summary or "",
        "skills": [s.name for s in profile.skills],
        "skills_detailed": [s.model_dump() for s in profile.skills],
        "target_roles": profile.target_roles or [],
        "target_industries": profile.target_industries or [],
        "experience": [e.model_dump() for e in profile.experience],
        "education": [e.model_dump() for e in profile.education],
        "skills_count": len(profile.skills),
        "experience_count": len(profile.experience),
        "education_count": len(profile.education),
        "updated_at": profile.updated_at.isoformat(),
    }


class ProfileUpdateRequest(BaseModel):
    """Request to update career profile."""
    full_name: Optional[str] = None
    headline: Optional[str] = None
    professional_summary: Optional[str] = None
    target_roles: Optional[list[str]] = None
    target_industries: Optional[list[str]] = None
    skills: Optional[list[str]] = None


@router.put("/")
async def update_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
):
    """Update the user's master career profile."""
    profile = await CareerProfile.find_one(CareerProfile.user_id == str(user.id))
    if not profile:
        profile = CareerProfile(user_id=str(user.id))

    if data.full_name is not None:
        profile.full_name = data.full_name
    if data.headline is not None:
        profile.headline = data.headline
    if data.professional_summary is not None:
        profile.professional_summary = data.professional_summary
    if data.target_roles is not None:
        profile.target_roles = data.target_roles
    if data.target_industries is not None:
        profile.target_industries = data.target_industries
    if data.skills is not None:
        profile.skills = [
            ProfileSkill(
                name=s,
                normalized_name=s.strip().lower(),
                provenance=[SkillProvenance(source="USER_PROFILE", confidence="high")],
            )
            for s in data.skills if s.strip()
        ]

    profile.updated_at = datetime.utcnow()
    await profile.save()

    return {"message": "Master career profile updated successfully"}


@router.post("/purge-data")
async def purge_user_data(user: User = Depends(get_current_user)):
    """
    Data deletion support / GDPR Right to be Forgotten (§45).
    Completely purges all user documents, uploaded files, job descriptions,
    analyses, recommendations, CV versions, and master career profile.
    """
    import os
    from app.models.document import Document
    from app.models.job_description import JobDescription
    from app.models.analysis import Analysis
    from app.models.recommendation import Recommendation
    from app.models.cv_version import CVVersion
    from app.models.audit_log import AuditLog

    user_id_str = str(user.id)

    # 1. Delete on-disk files and documents
    docs = await Document.find(Document.user_id == user_id_str).to_list()
    for doc in docs:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass
        await doc.delete()

    # 2. Delete JDs
    jds = await JobDescription.find(JobDescription.user_id == user_id_str).to_list()
    for jd in jds:
        await jd.delete()

    # 3. Delete Analyses
    analyses = await Analysis.find(Analysis.user_id == user_id_str).to_list()
    for a in analyses:
        await a.delete()

    # 4. Delete Recommendations
    recs = await Recommendation.find(Recommendation.user_id == user_id_str).to_list()
    for r in recs:
        await r.delete()

    # 5. Delete CV Versions
    versions = await CVVersion.find(CVVersion.user_id == user_id_str).to_list()
    for v in versions:
        await v.delete()

    # 6. Delete Career Profile
    profile = await CareerProfile.find_one(CareerProfile.user_id == user_id_str)
    if profile:
        await profile.delete()

    # 7. Audit log the purge event (no PII stored)
    await AuditLog(
        user_id=user_id_str,
        action="user_data_purged",
        entity_type="user",
        entity_id=user_id_str,
        details={
            "documents_deleted": len(docs),
            "jds_deleted": len(jds),
            "analyses_deleted": len(analyses),
            "recommendations_deleted": len(recs),
            "versions_deleted": len(versions),
        },
    ).save()

    return {
        "message": "All user data and associated files have been permanently purged.",
        "summary": {
            "documents_deleted": len(docs),
            "job_descriptions_deleted": len(jds),
            "analyses_deleted": len(analyses),
            "recommendations_deleted": len(recs),
            "cv_versions_deleted": len(versions),
        },
    }
