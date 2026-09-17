"""
Tests for Semantic Normalization Service (§13).
Validates canonical taxonomy, alias resolution, boundary matching, and negative boundary enforcement.
"""

import pytest
from app.services.normalization import normalization_service, SemanticNormalizationService


def test_alias_normalization():
    """Test canonical normalization for common tech aliases."""
    svc = normalization_service
    assert svc.normalize("JS") == "JavaScript"
    assert svc.normalize("javascript") == "JavaScript"
    assert svc.normalize("ts") == "TypeScript"
    assert svc.normalize("typescript") == "TypeScript"
    assert svc.normalize("k8s") == "Kubernetes"
    assert svc.normalize("kubernetes") == "Kubernetes"
    assert svc.normalize("postgres") == "PostgreSQL"
    assert svc.normalize("postgresql") == "PostgreSQL"
    assert svc.normalize("psql") == "PostgreSQL"
    assert svc.normalize("aws") == "AWS"
    assert svc.normalize("amazon web services") == "AWS"
    assert svc.normalize("gcp") == "GCP"
    assert svc.normalize("google cloud") == "GCP"
    assert svc.normalize("golang") == "Go"
    assert svc.normalize("go") == "Go"


def test_equivalence_checking():
    """Test are_equivalent for matching aliases."""
    svc = normalization_service
    assert svc.are_equivalent("JS", "JavaScript") is True
    assert svc.are_equivalent("Postgres", "PostgreSQL") is True
    assert svc.are_equivalent("k8s", "Kubernetes") is True
    assert svc.are_equivalent("Python", "py") is True
    assert svc.are_equivalent("React", "react.js") is True


def test_negative_boundaries():
    """
    CRITICAL §13: Ensure distinct technologies are NEVER conflated.
    Docker ≠ Kubernetes, React ≠ Next.js, Python ≠ Java, etc.
    """
    svc = normalization_service
    assert svc.are_equivalent("Docker", "Kubernetes") is False
    assert svc.are_equivalent("React", "Next.js") is False
    assert svc.are_equivalent("React", "Angular") is False
    assert svc.are_equivalent("Python", "Java") is False
    assert svc.are_equivalent("PostgreSQL", "MongoDB") is False
    assert svc.are_equivalent("SQL", "NoSQL") is False
    assert svc.are_equivalent("AWS", "Azure") is False
    assert svc.are_equivalent("REST APIs", "GraphQL") is False


def test_skill_matching_in_text():
    """Test regex boundary matching in candidate text."""
    svc = normalization_service

    # Candidate has PostgreSQL, JD asked for Postgres
    cv_text = "5 years developing microservices backed by PostgreSQL and Redis."
    assert svc.match_skill_in_text("Postgres", cv_text) is True
    assert svc.match_skill_in_text("PostgreSQL", cv_text) is True
    assert svc.match_skill_in_text("Redis", cv_text) is True
    assert svc.match_skill_in_text("MongoDB", cv_text) is False

    # Special characters: C++, C#, .NET
    cpp_text = "Experienced in C++ and Python high-throughput computing."
    assert svc.match_skill_in_text("C++", cpp_text) is True
    assert svc.match_skill_in_text("Python", cpp_text) is True
    assert svc.match_skill_in_text("C#", cpp_text) is False

    # Short aliases: JS, Go
    go_text = "Built concurrency services using Go and Docker."
    assert svc.match_skill_in_text("Go", go_text) is True
    assert svc.match_skill_in_text("Golang", go_text) is True
    assert svc.match_skill_in_text("Rust", go_text) is False


def test_extract_normalized_skills():
    """Test extraction of canonical skills from text."""
    svc = normalization_service
    bio = "Full-stack engineer skilled in JS, TypeScript, Next.js, Docker, and PostgreSQL."
    extracted = svc.extract_normalized_skills(bio)

    assert "JavaScript" in extracted
    assert "TypeScript" in extracted
    assert "Next.js" in extracted
    assert "Docker" in extracted
    assert "PostgreSQL" in extracted
    assert "Kubernetes" not in extracted
