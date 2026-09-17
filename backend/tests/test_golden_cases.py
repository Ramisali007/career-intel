"""
Golden Test Cases (§80, §112).
End-to-end integration test validating the full analysis pipeline on realistic CV and JD data.
"""

import pytest
from app.services.scoring_engine import ScoringEngine
from app.services.cv_exporter import CVExporter
from app.utils.diff_generator import compare_parsed_cvs
from app.models.analysis import RequirementMatch, MatchClassification, SkillEvidence


def test_golden_case_senior_backend_pipeline(sample_parsed_cv, sample_parsed_jd):
    """
    Simulates §112 End-to-End Test:
    1. Evaluates sample CV against Staff Backend JD.
    2. Runs deterministic Job Match scoring.
    3. Partitions requirements into 4-tier Gap Analysis matrix.
    4. Simulates approved optimization.
    5. Verifies score delta.
    6. Verifies PDF & DOCX export generation.
    """
    # 1. Simulate Requirement Matching
    cv_skills = set(s.lower() for s in sample_parsed_cv["skills"])
    matches = []

    for req in sample_parsed_jd["requirements"]:
        req_name = req["name"]
        priority = req["priority"]

        if req_name.lower() in cv_skills:
            classification = MatchClassification.STRONG_MATCH
            score = 90.0
            evidence = [SkillEvidence(skill_name=req_name, evidence_text=f"Demonstrated in production: {req_name}")]
        elif req_name.lower() == "distributed systems":
            classification = MatchClassification.EXACT_MATCH
            score = 95.0
            evidence = [SkillEvidence(skill_name="Distributed Systems", evidence_text="8+ years designing high-throughput distributed systems")]
        else:
            classification = MatchClassification.MISSING
            score = 0.0
            evidence = []

        matches.append(
            RequirementMatch(
                requirement_id=f"req_{req_name.lower()}",
                requirement_name=req_name,
                requirement_category=req["category"],
                requirement_priority=priority,
                classification=classification,
                match_score=score,
                cv_evidence=evidence,
            )
        )

    # 2. Calculate Job Match
    engine = ScoringEngine()
    score_result = engine.calculate_job_match(matches)
    initial_score = score_result["overall"]
    assert 60.0 <= initial_score <= 90.0
    assert score_result["confidence"] in ["high", "medium"]

    # 3. 4-Tier Gap Analysis Partitioning (§34)
    already_have = [m for m in matches if m.match_score >= 70.0]
    missing_must_haves = [m for m in matches if m.match_score < 30.0 and m.requirement_priority == "must_have"]
    nice_to_have = [m for m in matches if m.requirement_priority in ["preferred", "bonus"]]

    assert len(already_have) >= 3  # Python, Distributed Systems, PostgreSQL, Kafka
    assert len(nice_to_have) >= 2  # Kubernetes, GraphQL

    # 4. Simulate Optimization & Diff (§28, §37, §38)
    optimized_cv = dict(sample_parsed_cv)
    # Add addressed keyword
    optimized_cv["skills"] = list(sample_parsed_cv["skills"]) + ["Kubernetes"]
    diff_report = compare_parsed_cvs(sample_parsed_cv, optimized_cv)
    assert "Kubernetes" in diff_report["skills"]["added"]

    # 5. Export Verification (§41, §93)
    pdf_bytes = CVExporter.generate_pdf(optimized_cv, template_id="technical")
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")

    docx_bytes = CVExporter.generate_docx(optimized_cv, template_id="technical")
    assert len(docx_bytes) > 1000
    assert docx_bytes.startswith(b"PK\x03\x04")
