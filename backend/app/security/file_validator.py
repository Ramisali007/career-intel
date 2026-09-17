"""
File Validation & Security (§46).
MIME validation, extension checks, safe filenames, path traversal protection.
"""

import re
import uuid
try:
    import magic
except ImportError:
    magic = None
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.config import settings


def validate_upload(file: UploadFile) -> dict:
    """
    Validate an uploaded file for security (§46).
    Returns validated metadata or raises HTTPException.
    """
    # Extension validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = Path(file.filename).suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Content-Type validation
    content_type = file.content_type or ""
    if content_type not in settings.ALLOWED_MIME_TYPES:
        # Allow through but will verify with magic bytes later
        pass

    # Generate safe filename (path traversal protection §46)
    safe_filename = generate_safe_filename(file.filename, extension)

    return {
        "original_filename": file.filename,
        "safe_filename": safe_filename,
        "extension": extension,
        "content_type": content_type,
    }


def validate_file_content(file_path: str, expected_extension: str) -> str:
    """
    Validate file content matches expected type using magic bytes.
    Never trust a file merely because its extension says PDF (§46).
    """
    try:
        # Try to detect MIME type from file content
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)

        if expected_extension == ".pdf":
            # Check PDF magic bytes
            with open(file_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    raise HTTPException(
                        status_code=400,
                        detail="File content does not match PDF format. The file may be corrupted or mislabeled."
                    )
            return "application/pdf"

        elif expected_extension == ".docx":
            # Check DOCX magic bytes (ZIP-based format)
            with open(file_path, "rb") as f:
                header = f.read(4)
                if header != b"PK\x03\x04":
                    raise HTTPException(
                        status_code=400,
                        detail="File content does not match DOCX format. The file may be corrupted or mislabeled."
                    )
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        return mime_type or "application/octet-stream"

    except HTTPException:
        raise
    except Exception:
        return "application/octet-stream"


def validate_file_size(file_path: str):
    """Validate file size is within limits."""
    size = os.path.getsize(file_path)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if size > max_size:
        os.remove(file_path)  # Clean up
        raise HTTPException(
            status_code=400,
            detail=f"File size ({size / 1024 / 1024:.1f} MB) exceeds the maximum allowed ({settings.MAX_FILE_SIZE_MB} MB)"
        )

    if size == 0:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty")


def generate_safe_filename(original: str, extension: str) -> str:
    """Generate a safe filename to prevent path traversal attacks (§46)."""
    # Use UUID for the filename
    safe_name = f"{uuid.uuid4().hex}{extension}"
    return safe_name


def sanitize_text_input(text: str, max_length: int = 15000) -> str:
    """
    Sanitize text input (e.g., JD text).
    Protects against prompt injection by treating all content as data (§48).
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required")

    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text input exceeds maximum length ({max_length} characters)"
        )

    # Strip null bytes and control characters (keep newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text.strip()


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+override",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+a",
    r"output\s+the\s+following",
    r"grant\s+100.*score",
]


def detect_prompt_injection(text: str) -> tuple[bool, str]:
    """Detect common prompt injection patterns (§48)."""
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return True, match.group(0)
    return False, ""

