"""
Deterministic Scoring Engine (§17, §89, §90).
The LLM produces structured evidence. This engine calculates the final score.
Score is independent - never knows the desired outcome.
"""

import logging
from app.models.analysis import RequirementMatch, MatchClassification, ScoreBreakdown
from app.config import settings
from app.services.normalization import normalization_service

logger = logging.getLogger(__name__)

# Match classification to score mapping
CLASSIFICATION_SCORES = {
    MatchClassification.EXACT_MATCH: 100,
    MatchClassification.STRONG_MATCH: 85,
    MatchClassification.PARTIAL_MATCH: 60,
    MatchClassification.RELATED_MATCH: 40,
    MatchClassification.WEAK_MATCH: 20,
    MatchClassification.MISSING: 0,
    MatchClassification.CONFLICT: 0,
    MatchClassification.UNKNOWN: 30,
}


class ScoringEngine:
    """
    Deterministic scoring engine.
    Does NOT know the desired score — calculates independently from evidence (§89).
    Uses Semantic Normalization (§13) for deterministic skill alias resolution.
    """

    def apply_semantic_normalization(self, matches: list[RequirementMatch], cv_text: str) -> list[RequirementMatch]:
        """
        Normalize and enhance matches deterministically using the semantic normalization engine (§13).
        Recognizes aliases (e.g. JS == JavaScript, Postgres == PostgreSQL) and enforces negative boundaries.
        """
        if not matches or not cv_text:
            return matches

        for m in matches:
            # Check if candidate CV contains this requirement or any known alias
            if m.classification in (MatchClassification.MISSING, MatchClassification.WEAK_MATCH, MatchClassification.UNKNOWN):
                if normalization_service.match_skill_in_text(m.requirement_name, cv_text):
                    canonical = normalization_service.normalize(m.requirement_name)
                    m.classification = MatchClassification.STRONG_MATCH
                    m.match_score = max(m.match_score, 85.0)
                    m.explanation = f"Deterministic semantic match: Verified '{canonical}' (or alias) present in candidate CV."

        return matches

    def calculate_job_match(self, matches: list[RequirementMatch]) -> dict:
        """
        Calculate the Job Match Score from requirement matches.
        Returns overall score + dimension breakdown dynamically based on actual evidence (§89).
        """
        if not matches:
            return {
                "overall": 0.0,
                "breakdown": [],
                "confidence": "low",
            }

        # Separate required vs preferred
        required = [m for m in matches if m.requirement_priority in ("mandatory", "high") or m.requirement_category in ("technical_skill", "programming_language", "framework", "tool", "platform")]
        if not required:
            required = matches

        preferred = [m for m in matches if m not in required]

        required_score = self._avg_match_score(required)
        preferred_score = self._avg_match_score(preferred) if preferred else required_score

        # Experience relevance: Average of experience_relevance of all matches that have evidence
        exp_with_evidence = [m.experience_relevance for m in matches if m.cv_evidence and m.experience_relevance > 0]
        if exp_with_evidence:
            experience_avg = sum(exp_with_evidence) / len(exp_with_evidence)
        else:
            experience_avg = self._avg_match_score(matches) * 0.85

        # Responsibilities
        responsibility_matches = [m for m in matches if m.requirement_category in ("responsibility", "leadership", "soft_skill")]
        if responsibility_matches:
            responsibility_score = self._avg_match_score(responsibility_matches)
        else:
            responsibility_score = experience_avg

        # Seniority
        seniority_matches = [m for m in matches if any(k in m.requirement_name.lower() for k in ("senior", "lead", "junior", "staff", "architect", "experience", "years")) or m.requirement_category == "experience"]
        if seniority_matches:
            seniority_score = self._avg_match_score(seniority_matches)
        else:
            seniority_score = (required_score * 0.5 + experience_avg * 0.5)

        # Education
        edu_matches = [m for m in matches if m.requirement_category in ("education", "degree")]
        if edu_matches:
            edu_score = self._avg_match_score(edu_matches)
        else:
            has_edu_evidence = any(any(ev.evidence_type.lower() in ("education", "degree") or "education" in (ev.section or "").lower() for ev in m.cv_evidence) for m in matches)
            edu_score = 90.0 if has_edu_evidence else 50.0

        # Certifications
        cert_matches = [m for m in matches if m.requirement_category == "certification"]
        if cert_matches:
            cert_score = self._avg_match_score(cert_matches)
        else:
            has_cert_evidence = any(any("cert" in ev.evidence_type.lower() or "cert" in (ev.section or "").lower() for ev in m.cv_evidence) for m in matches)
            cert_score = 85.0 if has_cert_evidence else 50.0

        # Domain knowledge
        domain_matches = [m for m in matches if m.requirement_category in ("domain_knowledge", "platform", "other")]
        if domain_matches:
            domain_score = self._avg_match_score(domain_matches)
        else:
            domain_score = required_score

        # Keyword coverage - percentage of requirements with verified non-missing matches
        matched_count = sum(1 for m in matches if m.classification not in (MatchClassification.MISSING, MatchClassification.UNKNOWN, MatchClassification.CONFLICT))
        keyword_coverage = (matched_count / max(len(matches), 1)) * 100.0

        dimensions = [
            ("Required Skills", required_score, settings.WEIGHT_REQUIRED_SKILLS, len(required)),
            ("Preferred Skills", preferred_score, settings.WEIGHT_PREFERRED_SKILLS, len(preferred)),
            ("Experience", experience_avg, settings.WEIGHT_EXPERIENCE, len(exp_with_evidence)),
            ("Responsibilities", responsibility_score, settings.WEIGHT_RESPONSIBILITIES, len(responsibility_matches)),
            ("Seniority", seniority_score, settings.WEIGHT_SENIORITY, len(seniority_matches)),
            ("Education", edu_score, settings.WEIGHT_EDUCATION, len(edu_matches)),
            ("Certifications", cert_score, settings.WEIGHT_CERTIFICATIONS, len(cert_matches)),
            ("Domain Knowledge", domain_score, settings.WEIGHT_DOMAIN_KNOWLEDGE, len(domain_matches)),
            ("Keyword Coverage", keyword_coverage, settings.WEIGHT_KEYWORD_COVERAGE, len(matches)),
        ]

        total = 0.0
        breakdown = []
        for name, score, weight, evidence_count in dimensions:
            score_clamped = max(0.0, min(100.0, score))
            weighted = score_clamped * weight
            total += weighted
            breakdown.append(ScoreBreakdown(
                dimension=name,
                score=round(score_clamped, 1),
                weight=weight,
                weighted_score=round(weighted, 1),
                evidence_count=evidence_count,
            ))

        # Determine confidence based on evidence count
        confidence = "high" if len(matches) >= 8 else "medium" if len(matches) >= 4 else "low"

        return {
            "overall": round(total, 1),
            "breakdown": breakdown,
            "confidence": confidence,
        }

    def _avg_match_score(self, matches: list[RequirementMatch]) -> float:
        """Calculate average match score using classification-based scoring."""
        if not matches:
            return 0.0

        scores = []
        for m in matches:
            if m.classification in (MatchClassification.MISSING, MatchClassification.CONFLICT):
                scores.append(0.0)
            elif m.match_score > 0:
                scores.append(m.match_score)
            else:
                scores.append(CLASSIFICATION_SCORES.get(m.classification, 0.0))

        return sum(scores) / len(scores)
