"""
Documents Router - CV upload and management (§8, §46).
"""

import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from datetime import datetime

from app.models.user import User
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.audit_log import AuditLog
from app.security.auth import get_current_user
from app.security.file_validator import validate_upload, validate_file_content, validate_file_size
from app.services.document_parser import DocumentParserService
from app.config import settings

router = APIRouter()
parser = DocumentParserService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Upload a CV/resume document (§8)."""
    # Validate upload
    validation = validate_upload(file)

    # Ensure upload directory exists
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id))
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, validation["safe_filename"])
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
            )
        await f.write(content)

    # Validate file content (magic bytes)
    mime_type = validate_file_content(file_path, validation["extension"])

    # Compute hash for deduplication (§57)
    content_hash = parser.compute_file_hash(file_path)

    # Check for duplicate
    existing = await Document.find_one(
        Document.user_id == str(user.id),
        Document.content_hash == content_hash,
    )
    if existing:
        os.remove(file_path)  # Clean up duplicate
        return {
            "message": "This document has already been uploaded",
            "document_id": str(existing.id),
            "is_duplicate": True,
        }

    # Parse document
    try:
        if validation["extension"] == ".pdf":
            parsed_cv = parser.parse_pdf(file_path)
        elif validation["extension"] == ".docx":
            parsed_cv = parser.parse_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {str(e)}")

    # Create document record
    doc = Document(
        user_id=str(user.id),
        filename=validation["safe_filename"],
        original_filename=validation["original_filename"],
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=mime_type,
        extension=validation["extension"],
        content_hash=content_hash,
        document_type=DocumentType.CV,
        status=DocumentStatus.PARSED,
        parsed_cv=parsed_cv,
        raw_text=parsed_cv.raw_text,
        is_scanned=any("image-based" in w.lower() for w in parsed_cv.parser_warnings),
        parsed_at=datetime.utcnow(),
    )
    await doc.save()

    # Audit log (no PII)
    await AuditLog(
        user_id=str(user.id),
        action="document_uploaded",
        entity_type="document",
        entity_id=str(doc.id),
        details={"extension": validation["extension"], "page_count": parsed_cv.page_count},
    ).save()

    return {
        "document_id": str(doc.id),
        "filename": validation["original_filename"],
        "status": doc.status,
        "page_count": parsed_cv.page_count,
        "sections_detected": len(parsed_cv.sections),
        "skills_found": len(parsed_cv.skills),
        "experience_entries": len(parsed_cv.experience),
        "warnings": parsed_cv.parser_warnings,
        "is_duplicate": False,
    }


@router.get("/")
async def list_documents(
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """List all documents for the current user with pagination (§74)."""
    query = Document.find(Document.user_id == str(user.id))
    total = await query.count()
    docs = await query.sort("-uploaded_at").skip(skip).limit(min(limit, 50)).to_list()

    items = [
        {
            "id": str(d.id),
            "filename": d.original_filename,
            "status": d.status,
            "uploaded_at": d.uploaded_at.isoformat(),
            "page_count": d.parsed_cv.page_count if d.parsed_cv else 0,
            "is_scanned": d.is_scanned,
        }
        for d in docs
    ]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{document_id}")
async def get_document(document_id: str, user: User = Depends(get_current_user)):
    """Get a specific document with parsed data."""
    doc = await Document.get(document_id)
    if not doc or doc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(doc.id),
        "filename": doc.original_filename,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "parsed_cv": doc.parsed_cv.model_dump() if doc.parsed_cv else None,
        "warnings": doc.parsed_cv.parser_warnings if doc.parsed_cv else [],
        "is_scanned": doc.is_scanned,
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str, user: User = Depends(get_current_user)):
    """Delete a document and its file (§45)."""
    doc = await Document.get(document_id)
    if not doc or doc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await doc.delete()

    await AuditLog(
        user_id=str(user.id),
        action="document_deleted",
        entity_type="document",
        entity_id=document_id,
    ).save()

    return {"message": "Document deleted successfully"}
