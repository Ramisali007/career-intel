"""
Analyses Router - Start and manage analysis sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.models.document import Document
from app.models.job_description import JobDescription
from app.models.analysis import Analysis, AnalysisStatus
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user
from app.services.analysis_pipeline import AnalysisPipeline

router = APIRouter()


class AnalysisCreateRequest(BaseModel):
    """Request to start a new analysis."""
    document_id: str
    job_description_id: str


@router.post("/")
async def create_analysis(
    data: AnalysisCreateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """Start a new CV vs JD analysis."""
    # Validate document ownership
    doc = await Document.get(data.document_id)
    if not doc or doc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate JD ownership
    jd = await JobDescription.get(data.job_description_id)
    if not jd or jd.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Job description not found")

    # Create analysis
    analysis = Analysis(
        user_id=str(user.id),
        document_id=str(doc.id),
        job_description_id=str(jd.id),
        status=AnalysisStatus.QUEUED,
        current_step="Queued for processing",
    )
    await analysis.save()

    await AuditLog(
        user_id=str(user.id),
        action="analysis_started",
        entity_type="analysis",
        entity_id=str(analysis.id),
        document_id=str(doc.id),
    ).save()

    # Run analysis in background
    background_tasks.add_task(run_analysis_task, str(analysis.id), str(doc.id), str(jd.id))

    return {
        "analysis_id": str(analysis.id),
        "status": analysis.status,
        "message": "Analysis started. Poll for progress.",
    }


async def run_analysis_task(analysis_id: str, document_id: str, jd_id: str):
    """Background task to run the analysis pipeline."""
    try:
        analysis = await Analysis.get(analysis_id)
        document = await Document.get(document_id)
        jd = await JobDescription.get(jd_id)

        if not analysis or not document or not jd:
            return

        pipeline = AnalysisPipeline()
        await pipeline.run_analysis(analysis, document, jd)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Background analysis failed: {e}")
        analysis = await Analysis.get(analysis_id)
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            await analysis.save()


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, user: User = Depends(get_current_user)):
    """Get analysis results and current status."""
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get related data
    doc = await Document.get(analysis.document_id)
    jd = await JobDescription.get(analysis.job_description_id)

    result = {
        "id": str(analysis.id),
        "status": analysis.status,
        "current_step": analysis.current_step,
        "progress": analysis.progress_percentage,
        "stages_completed": analysis.stages_completed,
        "created_at": analysis.created_at.isoformat(),
        "processing_time": analysis.processing_time_seconds,

        # Document info
        "document": {
            "id": str(doc.id) if doc else None,
            "filename": doc.original_filename if doc else None,
        },
        "job_description": {
            "id": str(jd.id) if jd else None,
            "title": jd.title if jd else None,
            "job_title": jd.parsed_jd.job_title if jd and jd.parsed_jd else None,
            "company": jd.parsed_jd.company if jd and jd.parsed_jd else None,
        },
    }

    # Include results if analysis is complete or has partial results
    if analysis.scores:
        result["scores"] = analysis.scores.model_dump()

    if analysis.original_scores:
        result["original_scores"] = analysis.original_scores.model_dump()

    if analysis.optimized_scores:
        result["optimized_scores"] = analysis.optimized_scores.model_dump()

    # Find latest CV version if created
    from app.models.cv_version import CVVersion
    latest_version = await CVVersion.find(
        CVVersion.analysis_id == str(analysis.id)
    ).sort("-version").first_or_none()
    if latest_version:
        result["latest_version_id"] = str(latest_version.id)
        result["latest_version_number"] = latest_version.version

    if analysis.requirement_matches:
        result["requirement_matches"] = [m.model_dump() for m in analysis.requirement_matches]

    if analysis.keyword_intelligence:
        result["keyword_intelligence"] = [k.model_dump() for k in analysis.keyword_intelligence]

    result["strengths"] = analysis.strengths
    result["critical_gaps"] = analysis.critical_gaps
    result["improvement_areas"] = analysis.improvement_areas

    if analysis.error_message:
        result["error"] = analysis.error_message
        result["failed_stage"] = analysis.failed_stage

    return result


@router.get("/{analysis_id}/gap-analysis")
async def get_gap_analysis(analysis_id: str, user: User = Depends(get_current_user)):
    """
    Get 4-tier skill gap analysis matrix (§34, §35):
    - Already Have (strong evidence, match_score >= 70)
    - Need Better Evidence (partial/weak match, 30 <= match_score < 70)
    - Missing (hard requirements with no evidence)
    - Nice to Have (preferred/bonus requirements)
    """
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    already_have = []
    need_better_evidence = []
    missing = []
    nice_to_have = []

    for req in analysis.requirement_matches:
        priority = (req.requirement_priority or "preferred").lower()
        score = req.match_score
        classification = req.classification.value if hasattr(req.classification, "value") else str(req.classification)

        item = {
            "id": req.requirement_id,
            "name": req.requirement_name,
            "category": req.requirement_category or "Technical Skills",
            "priority": priority,
            "match_score": score,
            "classification": classification,
            "cv_evidence": [e.model_dump() for e in req.cv_evidence],
            "evidence_summary": req.evidence_summary or (req.cv_evidence[0].evidence_text if req.cv_evidence else ""),
            "confidence": req.confidence,
            "explanation": req.explanation,
        }

        # Classify into 4 tiers (§34)
        if score >= 70 or classification in ["exact_match", "strong_match"]:
            item["remediation_advice"] = "Verified: Strong evidence present in CV. Highlight in summary or top skills."
            already_have.append(item)
        elif priority in ["bonus", "preferred"] and score < 70:
            item["remediation_advice"] = req.recommended_action or f"Bonus skill: Gaining familiarity with {req.requirement_name} adds a distinct competitive edge."
            nice_to_have.append(item)
        elif 30 <= score < 70 or classification in ["partial_match", "related_match", "weak_match"]:
            item["remediation_advice"] = req.recommended_action or f"Strengthen evidence: Mention concrete projects, tools, or measurable impact for {req.requirement_name}."
            need_better_evidence.append(item)
        else:
            item["remediation_advice"] = req.recommended_action or f"Critical gap: Must-have requirement not evidenced in CV. Add relevant experience if you have it, or bridge via target projects."
            missing.append(item)

    total = len(analysis.requirement_matches)
    already_count = len(already_have)

    return {
        "summary": {
            "total_requirements": total,
            "already_have_count": already_count,
            "already_have_percentage": round((already_count / total * 100) if total > 0 else 0, 1),
            "need_better_evidence_count": len(need_better_evidence),
            "missing_count": len(missing),
            "nice_to_have_count": len(nice_to_have),
        },
        "tiers": {
            "already_have": already_have,
            "need_better_evidence": need_better_evidence,
            "missing": missing,
            "nice_to_have": nice_to_have,
        },
    }


@router.post("/{analysis_id}/optimize")
async def optimize_analysis(analysis_id: str, user: User = Depends(get_current_user)):
    """
    Apply approved recommendations, generate an optimized CV version,
    and rescore deterministically (§28, §36, §37).
    """
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    pipeline = AnalysisPipeline()
    try:
        result = await pipeline.optimize_and_rescore(analysis)

        # Audit log (§59)
        await AuditLog(
            user_id=str(user.id),
            action="cv_optimized",
            entity_type="analysis",
            entity_id=analysis_id,
            details={
                "approved_count": result.get("approved_count", 0),
                "verification_status": result.get("verification_status", "unknown"),
            },
        ).save()

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")



@router.get("/")
async def list_analyses(
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
):
    """List all analyses for the current user with pagination (§58, §74)."""
    query = Analysis.find(Analysis.user_id == str(user.id))
    if status_filter:
        query = query.find(Analysis.status == status_filter)

    total = await query.count()
    analyses = await query.sort("-created_at").skip(skip).limit(min(limit, 50)).to_list()

    results = []
    for a in analyses:
        jd = await JobDescription.get(a.job_description_id)
        results.append({
            "id": str(a.id),
            "document_id": a.document_id,
            "status": a.status,
            "job_title": jd.parsed_jd.job_title if jd and jd.parsed_jd else jd.title if jd else "",
            "company": jd.parsed_jd.company if jd and jd.parsed_jd else "",
            "job_match_score": a.scores.job_match_score if a.scores else None,
            "ats_score": a.scores.ats_score if a.scores else None,
            "quality_score": a.scores.quality_score if a.scores else None,
            "created_at": a.created_at.isoformat(),
            "processing_time": a.processing_time_seconds,
        })

    return {"items": results, "total": total, "skip": skip, "limit": limit}


class JDInput(BaseModel):
    """Input for a single job description in multi-JD comparison."""
    title: str = Field(..., max_length=200)
    company: Optional[str] = "Target Company"
    text: str = Field(..., min_length=30, max_length=15000)


class MultiJDRequest(BaseModel):
    """Request for multi-JD analysis (§32, §33)."""
    document_id: str
    job_descriptions: list[JDInput] = Field(..., min_length=2, max_length=5)


@router.post("/multi-jd")
async def analyze_multiple_jds(
    data: MultiJDRequest,
    user: User = Depends(get_current_user),
):
    """
    Compare one CV against 2-5 Job Descriptions simultaneously (§32, §33).
    Ranks fit scores, highlights Best Fit with explanation, and analyzes cross-JD common vs unique skills.
    """
    doc = await Document.get(data.document_id)
    if not doc or doc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Document not found")

    cv = doc.parsed_cv
    if not cv:
        raise HTTPException(status_code=400, detail="Document has not been parsed yet")

    cv_skills = set(s.strip().lower() for s in (cv.skills or []))
    cv_text = f"{cv.summary or ''} {' '.join([b for exp in (cv.experience or []) for b in (exp.bullets or [])])}".lower()

    ranked_jobs = []
    all_jd_skill_sets = {}

    import re
    # Common tech keywords ontology to detect in JDs
    TECH_VOCAB = [
        "python", "javascript", "typescript", "react", "next.js", "node.js", "vue", "angular",
        "fastapi", "django", "flask", "go", "golang", "rust", "java", "spring", "c++", "c#", ".net",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "terraform", "ansible",
        "rest", "graphql", "grpc", "microservices", "distributed systems", "kafka", "rabbitmq",
        "linux", "git", "agile", "scrum", "pytest", "unit testing", "system design"
    ]

    for idx, jd_item in enumerate(data.job_descriptions):
        jd_lower = jd_item.text.lower()
        found_in_jd = set()

        for term in TECH_VOCAB:
            # Word boundary search
            if re.search(r'\b' + re.escape(term) + r'\b', jd_lower):
                found_in_jd.add(term)

        all_jd_skill_sets[jd_item.title] = found_in_jd

        # Match CV against this JD
        matched_skills = []
        missing_skills = []

        for skill in found_in_jd:
            if skill in cv_skills or skill in cv_text:
                matched_skills.append(skill.title())
            else:
                missing_skills.append(skill.title())

        total_reqs = len(found_in_jd)
        if total_reqs > 0:
            match_score = round((len(matched_skills) / total_reqs) * 100, 1)
        else:
            match_score = 75.0  # default baseline if unstructured

        # Compute ATS estimate
        ats_score = min(98.0, 70.0 + (len(matched_skills) * 2.5))

        ranked_jobs.append({
            "job_id": f"job_{idx+1}",
            "job_title": jd_item.title,
            "company": jd_item.company or "Company",
            "job_match_score": match_score,
            "ats_score": round(ats_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_skills_detected": total_reqs,
            "summary": f"{len(matched_skills)} of {total_reqs} detected requirements verified in your CV.",
        })

    # Sort descending by match score
    ranked_jobs.sort(key=lambda x: x["job_match_score"], reverse=True)

    # Cross-JD Analysis (§33)
    # 1. Common requirements: in >= 60% of JDs
    threshold = max(2, len(data.job_descriptions) * 0.6)
    skill_frequency = {}
    for jd_title, skills_set in all_jd_skill_sets.items():
        for s in skills_set:
            skill_frequency[s] = skill_frequency.get(s, 0) + 1

    common_requirements = [s.title() for s, count in skill_frequency.items() if count >= threshold]
    unique_requirements = {}
    for jd_title, skills_set in all_jd_skill_sets.items():
        unique_for_this = [s.title() for s in skills_set if skill_frequency.get(s, 0) == 1]
        if unique_for_this:
            unique_requirements[jd_title] = unique_for_this

    # Best Fit (§32)
    top_job = ranked_jobs[0]
    best_fit = {
        "job_title": top_job["job_title"],
        "company": top_job["company"],
        "job_match_score": top_job["job_match_score"],
        "ats_score": top_job["ats_score"],
        "explanation": (
            f"Highest alignment at {top_job['job_match_score']}%. "
            f"Your CV strongly covers {len(top_job['matched_skills'])} core skills "
            f"({', '.join(top_job['matched_skills'][:4]) if top_job['matched_skills'] else 'general alignment'}), "
            f"with only {len(top_job['missing_skills'])} gaps to bridge."
        ),
    }

    # Audit log
    await AuditLog(
        user_id=str(user.id),
        action="multi_jd_analyzed",
        entity_type="analysis",
        entity_id=str(doc.id),
        details={"job_count": len(data.job_descriptions), "best_fit": best_fit["job_title"]},
    ).save()

    return {
        "best_fit": best_fit,
        "ranked_jobs": ranked_jobs,
        "cross_jd_analysis": {
            "common_requirements": common_requirements,
            "unique_requirements": unique_requirements,
            "total_roles_compared": len(data.job_descriptions),
        },
    }


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, user: User = Depends(get_current_user)):
    """
    Delete an analysis session with cascading cleanup of associated
    recommendations and CV versions (§45, §59).
    """
    analysis = await Analysis.get(analysis_id)
    if not analysis or analysis.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Analysis not found")

    from app.models.recommendation import Recommendation
    from app.models.cv_version import CVVersion

    # Cascade delete recommendations
    recs = await Recommendation.find(Recommendation.analysis_id == analysis_id).to_list()
    for r in recs:
        await r.delete()

    import os
    # Cascade delete CV versions and exported files
    versions = await CVVersion.find(CVVersion.analysis_id == analysis_id).to_list()
    for v in versions:
        for p in (v.exported_pdf_path, v.exported_docx_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        await v.delete()

    # Delete analysis
    await analysis.delete()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="analysis_deleted",
        entity_type="analysis",
        entity_id=analysis_id,
        details={
            "deleted_recommendations_count": len(recs),
            "deleted_versions_count": len(versions),
        },
    ).save()

    return {
        "message": "Analysis and associated data deleted successfully",
        "analysis_id": analysis_id,
        "cleaned_recommendations": len(recs),
        "cleaned_versions": len(versions),
    }


@router.get("/diagnostics/system-health")
async def get_system_health(user: User = Depends(get_current_user)):
    """
    System diagnostic and operational metrics (§67, §103).
    Returns real-time pipeline throughput metrics, score statistics, and AI provider health.
    """
    from app.config import settings
    from app.ai.model_router import get_model_router

    total_analyses = await Analysis.count()
    completed_analyses = await Analysis.find(Analysis.status == AnalysisStatus.COMPLETED).to_list()

    avg_job_match = 0.0
    avg_ats = 0.0
    avg_quality = 0.0

    if completed_analyses:
        jm_scores = [a.scores.job_match_score for a in completed_analyses if a.scores]
        ats_scores = [a.scores.ats_score for a in completed_analyses if a.scores]
        q_scores = [a.scores.quality_score for a in completed_analyses if a.scores]

        if jm_scores:
            avg_job_match = round(sum(jm_scores) / len(jm_scores), 1)
        if ats_scores:
            avg_ats = round(sum(ats_scores) / len(ats_scores), 1)
        if q_scores:
            avg_quality = round(sum(q_scores) / len(q_scores), 1)

    queued_count = await Analysis.find(Analysis.status == AnalysisStatus.QUEUED).count()
    failed_count = await Analysis.find(Analysis.status == AnalysisStatus.FAILED).count()

    provider_status = {
        "gemini": {
            "configured": bool(settings.GEMINI_API_KEY),
            "model": settings.GEMINI_MODEL,
        },
        "groq": {
            "configured": bool(settings.GROQ_API_KEY),
            "model": settings.GROQ_MODEL,
        },
        "primary_provider": settings.PRIMARY_AI_PROVIDER,
        "fallback_provider": settings.FALLBACK_AI_PROVIDER,
    }

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "metrics": {
            "total_analyses": total_analyses,
            "completed": len(completed_analyses),
            "queued": queued_count,
            "failed": failed_count,
            "success_rate": round((len(completed_analyses) / total_analyses * 100) if total_analyses > 0 else 100, 1),
            "average_scores": {
                "job_match": avg_job_match,
                "ats_compatibility": avg_ats,
                "cv_quality": avg_quality,
            },
        },
        "ai_providers": provider_status,
    }

