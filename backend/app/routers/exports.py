"""
Exports Router - PDF/DOCX generation and download (§41-43, §93).
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.models.cv_version import CVVersion
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user
from app.services.cv_exporter import CVExporter, AVAILABLE_TEMPLATES

router = APIRouter()


@router.get("/templates")
async def list_templates():
    """List available professional, ATS-safe CV templates (§41, §43)."""
    return AVAILABLE_TEMPLATES


async def _get_cv_data(version_or_doc_id: str, user: User) -> tuple[dict, str]:
    """Retrieve parsed CV data from either a CVVersion or a Document."""
    version = await CVVersion.get(version_or_doc_id)
    if version and version.user_id == str(user.id) and version.parsed_cv:
        return version.parsed_cv.model_dump(), f"v{version.version}"

    doc = await Document.get(version_or_doc_id)
    if doc and doc.user_id == str(user.id) and doc.parsed_cv:
        return doc.parsed_cv.model_dump(), "original"

    # Also search by analysis_id for CVVersion
    version_by_analysis = await CVVersion.find(
        CVVersion.analysis_id == version_or_doc_id,
        CVVersion.user_id == str(user.id),
    ).sort("-version").first_or_none()
    if version_by_analysis and version_by_analysis.parsed_cv:
        return version_by_analysis.parsed_cv.model_dump(), f"v{version_by_analysis.version}"

    # Also search by Analysis itself
    from app.models.analysis import Analysis
    analysis = await Analysis.get(version_or_doc_id)
    if analysis and analysis.user_id == str(user.id):
        if analysis.latest_version_id:
            ver = await CVVersion.get(analysis.latest_version_id)
            if ver and ver.parsed_cv:
                return ver.parsed_cv.model_dump(), f"v{ver.version}"
        if analysis.document_id:
            analysis_doc = await Document.get(analysis.document_id)
            if analysis_doc and analysis_doc.parsed_cv:
                return analysis_doc.parsed_cv.model_dump(), "analysis_cv"

    raise HTTPException(status_code=404, detail="CV version or document data not found")


@router.post("/{version_id}/pdf")
async def export_pdf(
    version_id: str,
    template: str = "ats_classic",
    user: User = Depends(get_current_user),
):
    """
    Export a CV version as an ATS-compliant PDF (§41, §93).
    """
    cv_data, label = await _get_cv_data(version_id, user)

    try:
        pdf_bytes = CVExporter.generate_pdf(cv_data, template_id=template)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    # Audit log
    await AuditLog(
        user_id=str(user.id),
        action="cv_exported_pdf",
        entity_type="cv_version",
        entity_id=version_id,
        details={"template": template, "label": label},
    ).save()

    candidate_name = cv_data.get("contact_info", {}).get("name", "Candidate").replace(" ", "_")
    filename = f"{candidate_name}_CV_{template}_{label}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.post("/{version_id}/docx")
async def export_docx(
    version_id: str,
    template: str = "ats_classic",
    user: User = Depends(get_current_user),
):
    """
    Export a CV version as an editable, ATS-compliant DOCX file (§41, §93).
    """
    cv_data, label = await _get_cv_data(version_id, user)

    try:
        docx_bytes = CVExporter.generate_docx(cv_data, template_id=template)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"DOCX export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")

    # Audit log
    await AuditLog(
        user_id=str(user.id),
        action="cv_exported_docx",
        entity_type="cv_version",
        entity_id=version_id,
        details={"template": template, "label": label},
    ).save()

    candidate_name = cv_data.get("contact_info", {}).get("name", "Candidate").replace(" ", "_")
    filename = f"{candidate_name}_CV_{template}_{label}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
