"""
Tests for Data Deletion (§45), CV Rollback (§36), and Scoring Integration.
"""

import pytest
from app.models.analysis import RequirementMatch, MatchClassification
from app.services.scoring_engine import ScoringEngine
from app.services.normalization import normalization_service


def test_scoring_engine_semantic_enhancement():
    """
    Test that ScoringEngine.apply_semantic_normalization deterministically upgrades
    missing requirements when candidate CV text contains recognized aliases (§13, §17).
    """
    engine = ScoringEngine()

    matches = [
        RequirementMatch(
            requirement_id="req_1",
            requirement_name="Postgres",
            requirement_category="Database",
            requirement_priority="mandatory",
            classification=MatchClassification.MISSING,
            match_score=0.0,
            confidence=0.5,
        ),
        RequirementMatch(
            requirement_id="req_2",
            requirement_name="Docker",
            requirement_category="DevOps",
            requirement_priority="mandatory",
            classification=MatchClassification.MISSING,
            match_score=0.0,
            confidence=0.5,
        ),
    ]

    # CV mentions PostgreSQL (alias of Postgres) and Kubernetes (NOT Docker - negative boundary)
    cv_text = "Experienced backend engineer utilizing PostgreSQL for primary data storage and Kubernetes for deployment."

    enhanced_matches = engine.apply_semantic_normalization(matches, cv_text)

    # req_1 (Postgres) should be upgraded because PostgreSQL is in the CV
    assert enhanced_matches[0].classification == MatchClassification.STRONG_MATCH
    assert enhanced_matches[0].match_score >= 85.0
    assert "PostgreSQL" in enhanced_matches[0].explanation or "Postgres" in enhanced_matches[0].explanation

    # req_2 (Docker) should REMAIN MISSING because Kubernetes is NOT Docker (negative boundary)
    assert enhanced_matches[1].classification == MatchClassification.MISSING
    assert enhanced_matches[1].match_score == 0.0


def test_deterministic_scoring_calculation():
    """Test deterministic calculation of job match score with breakdowns."""
    engine = ScoringEngine()

    matches = [
        RequirementMatch(
            requirement_id="req_1",
            requirement_name="Python",
            requirement_category="Required Skills",
            requirement_priority="mandatory",
            classification=MatchClassification.EXACT_MATCH,
            match_score=100.0,
            experience_relevance=95.0,
        ),
        RequirementMatch(
            requirement_id="req_2",
            requirement_name="AWS",
            requirement_category="Required Skills",
            requirement_priority="high",
            classification=MatchClassification.STRONG_MATCH,
            match_score=85.0,
            experience_relevance=80.0,
        ),
    ]

    result = engine.calculate_job_match(matches)
    assert result["overall"] > 0
    assert len(result["breakdown"]) == 9
    assert result["confidence"] in ("low", "medium", "high")
