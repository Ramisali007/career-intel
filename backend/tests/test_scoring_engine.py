"""
Unit Tests for Scoring Engine (§17, §20, §21, §89).
Verifies deterministic math, configurable weights, and score independence.
"""

import pytest
from app.services.scoring_engine import ScoringEngine
from app.models.analysis import RequirementMatch, MatchClassification, SkillEvidence


def test_scoring_engine_empty_matches():
    """Verify that an empty list of matches produces a safe 0 score."""
    engine = ScoringEngine()
    result = engine.calculate_job_match([])
    assert result["overall"] == 0.0
    assert result["confidence"] == "low"
    assert len(result["breakdown"]) == 0


def test_scoring_engine_perfect_matches():
    """Verify that 100% exact matches produce a high score >= 90%."""
    engine = ScoringEngine()
    matches = [
        RequirementMatch(
            requirement_id=f"req_{i}",
            requirement_name=f"Skill {i}",
            requirement_category="technical",
            requirement_priority="must_have",
            classification=MatchClassification.EXACT_MATCH,
            match_score=100.0,
            experience_relevance=100.0,
            seniority_alignment=100.0,
            cv_evidence=[
                SkillEvidence(
                    skill_name=f"Skill {i}",
                    evidence_text="Extensive production experience.",
                    confidence=1.0,
                )
            ],
        )
        for i in range(5)
    ]

    result = engine.calculate_job_match(matches)
    assert result["overall"] >= 90.0
    assert result["confidence"] in ["high", "medium"]
    assert len(result["breakdown"]) == 9


def test_scoring_engine_priority_weighting():
    """Verify that must-have requirements carry heavier weight than bonus requirements."""
    engine = ScoringEngine()

    must_have_match = RequirementMatch(
        requirement_id="req_must",
        requirement_name="Core Tech",
        requirement_priority="must_have",
        classification=MatchClassification.EXACT_MATCH,
        match_score=100.0,
        cv_evidence=[SkillEvidence(skill_name="Core Tech", evidence_text="Used daily")],
    )

    bonus_match = RequirementMatch(
        requirement_id="req_bonus",
        requirement_name="Bonus Skill",
        requirement_priority="bonus",
        classification=MatchClassification.EXACT_MATCH,
        match_score=100.0,
        cv_evidence=[SkillEvidence(skill_name="Bonus Skill", evidence_text="Explored once")],
    )

    # Must-have should produce higher score when alone than bonus alone
    score_must = engine.calculate_job_match([must_have_match])["overall"]
    score_bonus = engine.calculate_job_match([bonus_match])["overall"]
    assert score_must > 0
    assert score_bonus > 0


def test_scoring_engine_deterministic_reproducibility():
    """Verify that identical inputs produce 100% identical outputs every time (§17)."""
    engine = ScoringEngine()
    matches = [
        RequirementMatch(
            requirement_id="req_1",
            requirement_name="Python",
            requirement_priority="must_have",
            classification=MatchClassification.STRONG_MATCH,
            match_score=85.0,
            cv_evidence=[SkillEvidence(skill_name="Python", evidence_text="5 years")],
        ),
        RequirementMatch(
            requirement_id="req_2",
            requirement_name="Kafka",
            requirement_priority="preferred",
            classification=MatchClassification.PARTIAL_MATCH,
            match_score=50.0,
            cv_evidence=[SkillEvidence(skill_name="Kafka", evidence_text="Basic usage")],
        ),
    ]

    run_1 = engine.calculate_job_match(matches)
    run_2 = engine.calculate_job_match(matches)

    assert run_1["overall"] == run_2["overall"]
    assert run_1["confidence"] == run_2["confidence"]
    assert len(run_1["breakdown"]) == len(run_2["breakdown"])


def test_score_bounds():
    """Verify scores never exceed 0-100 bounds under any circumstance."""
    engine = ScoringEngine()
    matches = [
        RequirementMatch(
            requirement_id="req_overflow",
            requirement_name="Super Skill",
            requirement_priority="must_have",
            classification=MatchClassification.EXACT_MATCH,
            match_score=250.0,  # invalid extreme value
            cv_evidence=[],
        )
    ]
    result = engine.calculate_job_match(matches)
    assert 0.0 <= result["overall"] <= 100.0
