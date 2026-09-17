"""
CV Versions Router - Version management and optimization (§36).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.models.user import User
from app.models.cv_version import CVVersion
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_cv_versions(
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """List all CV versions for the current user with pagination (§74)."""
    query = CVVersion.find(CVVersion.user_id == str(user.id))
    total = await query.count()
    versions = await query.sort("-created_at").skip(skip).limit(min(limit, 50)).to_list()

    items = [
        {
            "id": str(v.id),
            "document_id": v.document_id,
            "version": v.version,
            "version_type": v.version_type,
            "job_match_score": v.job_match_score,
            "ats_score": v.ats_score,
            "quality_score": v.quality_score,
            "verification_status": v.verification_status,
            "template_used": v.template_used,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{version_id}")
async def get_cv_version(version_id: str, user: User = Depends(get_current_user)):
    """Get a specific CV version with full details."""
    version = await CVVersion.get(version_id)
    if not version or version.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="CV version not found")

    return {
        "id": str(version.id),
        "document_id": version.document_id,
        "version": version.version,
        "version_type": version.version_type,
        "parsed_cv": version.parsed_cv.model_dump() if version.parsed_cv else None,
        "job_match_score": version.job_match_score,
        "ats_score": version.ats_score,
        "quality_score": version.quality_score,
        "verification_status": version.verification_status,
        "claim_verifications": [v.model_dump() for v in version.claim_verifications],
        "changes_summary": version.changes_summary,
        "template_used": version.template_used,
        "created_at": version.created_at.isoformat(),
    }


@router.get("/{version_id}/diff")
async def get_version_diff(version_id: str, user: User = Depends(get_current_user)):
    """
    Get visual and structural diff between this version and original CV (§38).
    Classifies changes into ADDED, REMOVED, MODIFIED, and UNCHANGED.
    """
    from app.models.document import Document
    from app.utils.diff_generator import compare_parsed_cvs

    version = await CVVersion.get(version_id)
    if not version or version.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="CV version not found")

    # Fetch original document
    doc = await Document.get(version.document_id)
    if not doc or not doc.parsed_cv:
        raise HTTPException(status_code=404, detail="Original document not found")

    if not version.parsed_cv:
        raise HTTPException(status_code=400, detail="This version does not contain parsed CV data")

    orig_dict = doc.parsed_cv.model_dump()
    opt_dict = version.parsed_cv.model_dump()

    diff_report = compare_parsed_cvs(orig_dict, opt_dict)

    return {
        "version_id": str(version.id),
        "version_number": version.version,
        "version_type": version.version_type,
        "changes_summary": version.changes_summary,
        "approved_recommendation_ids": version.approved_recommendation_ids,
        "scores": {
            "job_match": version.job_match_score,
            "ats": version.ats_score,
            "quality": version.quality_score,
        },
        "diff": diff_report,
    }


@router.post("/{version_id}/rollback")
async def rollback_cv_version(version_id: str, user: User = Depends(get_current_user)):
    """
    Rollback capability: Revert active CV document to a previous version (§36).
    Restores parsed_cv state of the target document and logs the audit trail.
    """
    version = await CVVersion.get(version_id)
    if not version or version.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="CV version not found")

    doc = await Document.get(version.document_id)
    if not doc or doc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Parent document not found")

    if not version.parsed_cv:
        raise HTTPException(status_code=400, detail="Cannot rollback to a version without parsed CV data")

    # Revert document parsed_cv to this version's content
    doc.parsed_cv = version.parsed_cv
    await doc.save()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="cv_version_rollback",
        entity_type="cv_version",
        entity_id=version_id,
        document_id=doc.id,
        details={
            "rolled_back_to_version": version.version,
            "version_type": version.version_type,
        },
    ).save()

    return {
        "message": f"Successfully rolled back document to Version {version.version}",
        "version_id": version_id,
        "version_number": version.version,
        "document_id": str(doc.id),
    }


@router.delete("/{version_id}")
async def delete_cv_version(version_id: str, user: User = Depends(get_current_user)):
    """
    Delete a specific CV version (§45).
    """
    version = await CVVersion.get(version_id)
    if not version or version.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="CV version not found")

    v_num = version.version
    await version.delete()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="cv_version_deleted",
        entity_type="cv_version",
        entity_id=version_id,
        details={"version_number": v_num},
    ).save()

    return {
        "message": f"CV version {v_num} deleted successfully",
        "deleted_id": version_id,
    }

