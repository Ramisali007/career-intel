"""
Job Descriptions Router - JD submission and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.user import User
from app.models.job_description import JobDescription
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user
from app.security.file_validator import sanitize_text_input

router = APIRouter()


class JDCreateRequest(BaseModel):
    """Request to create a job description."""
    text: str = Field(min_length=50, max_length=15000)
    title: str = Field(default="", max_length=200)
    source_url: str = Field(default="", max_length=500)


@router.post("/")
async def create_job_description(
    data: JDCreateRequest,
    user: User = Depends(get_current_user),
):
    """Submit a job description for analysis."""
    sanitized_text = sanitize_text_input(data.text, max_length=15000)

    jd = JobDescription(
        user_id=str(user.id),
        title=data.title or "Untitled Job Description",
        raw_text=sanitized_text,
        source_url=data.source_url or None,
    )
    await jd.save()

    await AuditLog(
        user_id=str(user.id),
        action="jd_created",
        entity_type="job_description",
        entity_id=str(jd.id),
    ).save()

    return {
        "id": str(jd.id),
        "title": jd.title,
        "text_length": len(sanitized_text),
        "created_at": jd.created_at.isoformat(),
    }


@router.get("/")
async def list_job_descriptions(
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """List all job descriptions for the current user with pagination (§74)."""
    query = JobDescription.find(JobDescription.user_id == str(user.id))
    total = await query.count()
    jds = await query.sort("-created_at").skip(skip).limit(min(limit, 50)).to_list()

    items = [
        {
            "id": str(jd.id),
            "title": jd.title,
            "company": jd.parsed_jd.company if jd.parsed_jd else jd.company,
            "job_title": jd.parsed_jd.job_title if jd.parsed_jd else "",
            "is_parsed": jd.is_parsed,
            "created_at": jd.created_at.isoformat(),
        }
        for jd in jds
    ]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{jd_id}")
async def get_job_description(jd_id: str, user: User = Depends(get_current_user)):
    """Get a specific job description."""
    jd = await JobDescription.get(jd_id)
    if not jd or jd.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Job description not found")

    return {
        "id": str(jd.id),
        "title": jd.title,
        "raw_text": jd.raw_text,
        "parsed_jd": jd.parsed_jd.model_dump() if jd.parsed_jd else None,
        "is_parsed": jd.is_parsed,
        "created_at": jd.created_at.isoformat(),
    }


@router.delete("/{jd_id}")
async def delete_job_description(jd_id: str, user: User = Depends(get_current_user)):
    """Delete a job description (§45, §59)."""
    jd = await JobDescription.get(jd_id)
    if not jd or jd.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Job description not found")

    title = jd.title
    await jd.delete()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="jd_deleted",
        entity_type="job_description",
        entity_id=jd_id,
        details={"title": title},
    ).save()

    return {"message": "Job description deleted successfully", "deleted_id": jd_id}
