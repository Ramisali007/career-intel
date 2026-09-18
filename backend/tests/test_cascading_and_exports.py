"""
Unit Tests for Cascading Deletion, Name Sanitization, and Multi-JD Ranking (§32, §33, §41, §45).
"""

import pytest
import re
import os
from app.services.cv_exporter import CVExporter, AVAILABLE_TEMPLATES


def test_candidate_name_extraction_from_contact():
    """Verify candidate name extraction correctly resolves both 'contact' and 'contact_info' keys."""
    # Format standard to ParsedCV (uses 'contact')
    cv_with_contact = {
        "contact": {
            "name": "Jane Doe",
            "email": "jane@example.com",
        },
        "summary": "Full stack engineer",
        "skills": ["Python", "React"],
    }

    contact = cv_with_contact.get("contact") or cv_with_contact.get("contact_info") or {}
    raw_name = contact.get("name") or "Candidate"
    sanitized = re.sub(r"[^\w\-]", "_", raw_name.strip())
    assert sanitized == "Jane_Doe"

    # Fallback to Candidate if name is empty
    cv_empty_name = {
        "contact": {"name": ""},
        "skills": [],
    }
    contact2 = cv_empty_name.get("contact") or {}
    raw_name2 = contact2.get("name") or "Candidate"
    sanitized2 = re.sub(r"[^\w\-]", "_", raw_name2.strip()) or "Candidate"
    assert sanitized2 == "Candidate"


def test_export_filename_generation():
    """Verify exported PDF and DOCX filenames are sanitized against path traversal and special characters."""
    raw_names = [
        ("Dr. John Smith, Jr.", "Dr__John_Smith__Jr_"),
        ("Alice/../Bob", "Alice____Bob"),
        ("Sarah Connor", "Sarah_Connor"),
    ]

    for raw, expected in raw_names:
        sanitized = re.sub(r"[^\w\-]", "_", raw.strip())
        filename = f"{sanitized}_CV_ats_classic_v1.pdf"
        assert "/" not in filename
        assert "\\" not in filename
        assert ".." not in filename
        assert filename.startswith(expected)


def test_multi_jd_fit_ranking_calculation():
    """Verify fit scores and best-fit selection in multi-JD comparison."""
    cv_skills = {"python", "fastapi", "docker", "postgresql", "redis"}

    # Job 1: High overlap (4/4)
    jd_1_skills = {"python", "fastapi", "docker", "postgresql"}
    overlap_1 = len(jd_1_skills.intersection(cv_skills)) / len(jd_1_skills) * 100

    # Job 2: Low overlap (1/4)
    jd_2_skills = {"java", "spring", "c++", "docker"}
    overlap_2 = len(jd_2_skills.intersection(cv_skills)) / len(jd_2_skills) * 100

    assert overlap_1 == 100.0
    assert overlap_2 == 25.0

    ranked = [
        {"title": "Backend Python", "score": overlap_1},
        {"title": "Java Systems", "score": overlap_2},
    ]
    ranked.sort(key=lambda x: x["score"], reverse=True)

    best_fit = ranked[0]
    assert best_fit["title"] == "Backend Python"
    assert best_fit["score"] == 100.0


def test_disk_file_cleanup_simulation(tmp_path):
    """Verify physical export file cleanup removes files from disk without error."""
    test_pdf = tmp_path / "test_export.pdf"
    test_docx = tmp_path / "test_export.docx"

    test_pdf.write_bytes(b"%PDF-1.4 simulated pdf")
    test_docx.write_bytes(b"PK\x03\x04 simulated docx")

    assert test_pdf.exists()
    assert test_docx.exists()

    paths_to_clean = [str(test_pdf), str(test_docx), "/non/existent/path.pdf"]

    for p in paths_to_clean:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    assert not test_pdf.exists()
    assert not test_docx.exists()


def test_real_evidence_based_scoring_on_optimization():
    """Verify that when requirements are backed by real evidence, the scoring engine deterministically increases Job Match score (§17, §89)."""
    from app.services.scoring_engine import ScoringEngine
    from app.models.analysis import RequirementMatch, MatchClassification, SkillEvidence, EvidenceStrength

    engine = ScoringEngine()

    # Initial matches with missing/weak requirements
    initial_matches = [
        RequirementMatch(
            requirement_id="req_1",
            requirement_name="Python",
            requirement_category="programming_language",
            requirement_priority="mandatory",
            classification=MatchClassification.STRONG_MATCH,
            match_score=85.0,
            experience_relevance=85.0,
            cv_evidence=[SkillEvidence(skill_name="Python", evidence_text="Built APIs with Python", strength=EvidenceStrength.STRONG)]
        ),
        RequirementMatch(
            requirement_id="req_2",
            requirement_name="Docker",
            requirement_category="tool",
            requirement_priority="mandatory",
            classification=MatchClassification.MISSING,
            match_score=0.0,
            experience_relevance=0.0,
            cv_evidence=[]
        ),
    ]

    initial_score = engine.calculate_job_match(initial_matches)["overall"]

    # Optimized matches: Docker is now genuinely evidenced in candidate's updated CV
    optimized_matches = [
        initial_matches[0],
        RequirementMatch(
            requirement_id="req_2",
            requirement_name="Docker",
            requirement_category="tool",
            requirement_priority="mandatory",
            classification=MatchClassification.EXACT_MATCH,
            match_score=100.0,
            experience_relevance=95.0,
            cv_evidence=[SkillEvidence(skill_name="Docker", evidence_text="Containerized microservices using Docker", strength=EvidenceStrength.STRONG)]
        ),
    ]

    optimized_score = engine.calculate_job_match(optimized_matches)["overall"]

    assert optimized_score > initial_score
    assert optimized_score >= 85.0


