"""
Unit Tests for Visual Diff Generator and CV Exporter (§38, §41-43, §93).
"""

import pytest
from app.utils.diff_generator import generate_bullet_diff, compare_parsed_cvs
from app.services.cv_exporter import CVExporter, AVAILABLE_TEMPLATES


def test_bullet_diff_identical():
    """Verify unchanged bullet points are marked 'unchanged'."""
    text = "Managed team of 5 backend engineers."
    diff = generate_bullet_diff(text, text)
    assert diff["type"] == "unchanged"
    assert diff["original_text"] == text
    assert diff["modified_text"] == text


def test_bullet_diff_modification():
    """Verify modified bullets produce word-level diff spans."""
    orig = "Built REST APIs with Django."
    mod = "Architected high-throughput REST APIs with FastAPI, reducing response time by 40%."
    diff = generate_bullet_diff(orig, mod)
    assert diff["type"] == "modified"
    assert any(span["type"] == "added" for span in diff["highlighted_diff"])
    assert any(span["type"] == "removed" for span in diff["highlighted_diff"])


def test_compare_parsed_cvs(sample_parsed_cv):
    """Verify full section-by-section diff report calculation."""
    modified_cv = dict(sample_parsed_cv)
    modified_cv["summary"] = "Staff Backend Engineer specialized in event-driven systems and microservices."
    modified_cv["skills"] = list(sample_parsed_cv["skills"]) + ["Rust", "GraphQL"]

    diff_report = compare_parsed_cvs(sample_parsed_cv, modified_cv)
    assert "summary" in diff_report
    assert diff_report["summary"]["type"] == "modified"
    assert "Rust" in diff_report["skills"]["added"]
    assert "GraphQL" in diff_report["skills"]["added"]
    assert "Python" in diff_report["skills"]["retained"]


def test_export_pdf_generation(sample_parsed_cv):
    """Verify PDF export generates valid PDF stream with standard magic bytes (§41)."""
    for tmpl in AVAILABLE_TEMPLATES:
        pdf_bytes = CVExporter.generate_pdf(sample_parsed_cv, template_id=tmpl["id"])
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 500
        # Standard PDF magic header
        assert pdf_bytes.startswith(b"%PDF-")


def test_export_docx_generation(sample_parsed_cv):
    """Verify DOCX export generates valid Office Open XML ZIP package (§41)."""
    for tmpl in AVAILABLE_TEMPLATES:
        docx_bytes = CVExporter.generate_docx(sample_parsed_cv, template_id=tmpl["id"])
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 500
        # Standard ZIP package magic header for .docx
        assert docx_bytes.startswith(b"PK\x03\x04")
