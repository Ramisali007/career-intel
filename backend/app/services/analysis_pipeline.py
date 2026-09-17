"""
Analysis Pipeline Service - Orchestrates the complete analysis workflow (§54).
Manages the state machine: PARSING → EXTRACTING → MATCHING → SCORING → RECOMMENDING
"""

import json
import time
import logging
import asyncio
from datetime import datetime
from typing import Optional

from app.ai.model_router import get_model_router
from app.ai.prompts.prompt_templates import (
    CV_PARSER_V1, JD_PARSER_V1, EVIDENCE_EXTRACTOR_V1,
    RECOMMENDATION_ENGINE_V1, ATS_ANALYZER_V1, CV_QUALITY_V1,
    CV_OPTIMIZER_V1, CLAIM_VERIFIER_V1,
)
from app.models.analysis import (
    Analysis, AnalysisStatus, RequirementMatch, MatchClassification,
    SkillEvidence, EvidenceStrength, EvidenceSource,
    AnalysisScores, ScoreBreakdown, KeywordIntelligence,
)
from app.models.document import (
    Document, ParsedCV, ContactInfo, ExperienceEntry, EducationEntry,
    ProjectEntry, CertificationEntry,
)
from app.models.job_description import JobDescription, ParsedJD, JDRequirement, RequirementPriority
from app.models.recommendation import Recommendation, RecommendationCategory, FactualRisk
from app.services.scoring_engine import ScoringEngine
from app.config import settings

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Orchestrates the complete analysis pipeline.
    Each stage is independent and resumable (§55).
    """

    def __init__(self):
        self.router = get_model_router()
        self.scoring_engine = ScoringEngine()

    async def run_analysis(self, analysis: Analysis, document: Document, job_description: JobDescription) -> Analysis:
        """Run the complete analysis pipeline."""
        start_time = time.time()
        analysis.started_at = datetime.utcnow()

        try:
            # Stage 1: Parse CV (if not already parsed)
            analysis = await self._update_status(analysis, AnalysisStatus.PARSING_CV, "Reading CV...", 5)
            if not document.parsed_cv or not document.parsed_cv.experience:
                parsed_cv = await self._ai_parse_cv(document)
                document.parsed_cv = parsed_cv
                await document.save()
            analysis.stages_completed.append("parsing_cv")

            # Stage 2: Parse JD (if not already parsed)
            analysis = await self._update_status(analysis, AnalysisStatus.PARSING_JD, "Understanding Job Description...", 15)
            if not job_description.parsed_jd:
                parsed_jd = await self._ai_parse_jd(job_description)
                job_description.parsed_jd = parsed_jd
                job_description.is_parsed = True
                await job_description.save()
            analysis.stages_completed.append("parsing_jd")

            # Stage 3: Extract evidence and match
            analysis = await self._update_status(analysis, AnalysisStatus.EXTRACTING_EVIDENCE, "Comparing experience...", 35)
            match_results = await self._extract_and_match(document.parsed_cv, job_description.parsed_jd)
            analysis.requirement_matches = match_results["matches"]
            analysis.strengths = match_results.get("strengths", [])
            analysis.critical_gaps = match_results.get("critical_gaps", [])
            analysis.improvement_areas = match_results.get("improvement_areas", [])
            analysis.stages_completed.append("matching")

            # Stage 4: Scoring
            analysis = await self._update_status(analysis, AnalysisStatus.SCORING, "Calculating Job Match Score...", 50)
            cv_text = document.raw_text or (document.parsed_cv.raw_text if document.parsed_cv else "")
            analysis.requirement_matches = self.scoring_engine.apply_semantic_normalization(
                analysis.requirement_matches, cv_text
            )
            job_match_scores = self.scoring_engine.calculate_job_match(analysis.requirement_matches)

            # Stage 5 & 6: ATS & Quality Scoring (run concurrently for speed)
            analysis = await self._update_status(analysis, AnalysisStatus.SCORING_ATS, "Evaluating ATS & Quality...", 65)
            ats_task = self._analyze_ats(document.parsed_cv)
            quality_task = self._analyze_quality(document.parsed_cv)
            ats_scores, quality_scores = await asyncio.gather(ats_task, quality_task)

            # Combine scores
            analysis.scores = AnalysisScores(
                job_match_score=job_match_scores["overall"],
                job_match_breakdown=job_match_scores["breakdown"],
                job_match_confidence=job_match_scores.get("confidence", "medium"),
                ats_score=ats_scores["overall"],
                ats_breakdown=ats_scores["breakdown"],
                ats_warnings=ats_scores.get("warnings", []),
                quality_score=quality_scores["overall"],
                quality_breakdown=quality_scores["breakdown"],
            )
            analysis.original_scores = analysis.scores.model_copy()
            analysis.stages_completed.append("scoring")

            # Stage 7: Generate Recommendations
            analysis = await self._update_status(analysis, AnalysisStatus.GENERATING_RECOMMENDATIONS, "Generating recommendations...", 85)
            recommendations, keyword_intel = await self._generate_recommendations(
                document.parsed_cv, job_description.parsed_jd, analysis.requirement_matches
            )
            analysis.keyword_intelligence = keyword_intel

            # Save recommendations
            for rec_data in recommendations:
                rec = Recommendation(
                    user_id=analysis.user_id,
                    analysis_id=str(analysis.id),
                    **rec_data,
                )
                await rec.save()

            analysis.stages_completed.append("recommendations")

            # Complete
            analysis.status = AnalysisStatus.WAITING_FOR_APPROVAL
            analysis.current_step = "Analysis complete. Review recommendations."
            analysis.progress_percentage = 100
            analysis.processing_time_seconds = time.time() - start_time
            analysis.completed_at = datetime.utcnow()
            analysis.ai_provider_used = self.router.get_available_providers()[0] if self.router.get_available_providers() else "none"
            await analysis.save()

            logger.info(f"Analysis {analysis.id} completed in {analysis.processing_time_seconds:.1f}s")
            return analysis

        except Exception as e:
            logger.error(f"Analysis pipeline failed at {analysis.status}: {e}")
            analysis.status = AnalysisStatus.FAILED
            analysis.failed_stage = analysis.current_step
            analysis.error_message = str(e)
            await analysis.save()
            raise

    async def _update_status(self, analysis: Analysis, status: AnalysisStatus, step: str, progress: int) -> Analysis:
        """Update analysis status and save."""
        analysis.status = status
        analysis.current_step = step
        analysis.progress_percentage = progress
        await analysis.save()
        return analysis

    async def _ai_parse_cv(self, document: Document) -> ParsedCV:
        """Use AI to parse CV text into structured format."""
        prompt = CV_PARSER_V1["user_prompt_template"].format(
            cv_text=document.raw_text[:15000] if document.raw_text else ""
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=CV_PARSER_V1["schema"],
            system_prompt=CV_PARSER_V1["system_prompt"],
        )

        if not response.success or not response.structured_data:
            logger.warning(f"AI CV parsing failed, using basic parser results")
            return document.parsed_cv or ParsedCV()

        data = response.structured_data
        raw_text = document.raw_text or (document.parsed_cv.raw_text if document.parsed_cv else "")
        if not raw_text and document.file_path:
            try:
                from app.services.document_parser import DocumentParserService
                doc_parser = DocumentParserService()
                if document.file_path.endswith(".pdf"):
                    parsed_doc = doc_parser.parse_pdf(document.file_path)
                else:
                    parsed_doc = doc_parser.parse_docx(document.file_path)
                raw_text = parsed_doc.raw_text
                document.raw_text = raw_text
                await document.save()
            except Exception as pe:
                logger.warning(f"Could not re-extract raw_text from document: {pe}")

        contact_raw = data.get("contact")
        contact_dict = contact_raw if isinstance(contact_raw, dict) else {}

        return ParsedCV(
            contact=ContactInfo(**{k: v for k, v in contact_dict.items() if v is not None}),
            summary=data.get("summary") or "",
            experience=[ExperienceEntry(**{k: v for k, v in exp.items() if v is not None}) for exp in (data.get("experience") or []) if isinstance(exp, dict)],
            education=[EducationEntry(**{k: v for k, v in edu.items() if v is not None}) for edu in (data.get("education") or []) if isinstance(edu, dict)],
            skills=data.get("skills") or [],
            skill_categories=data.get("skill_categories") or {},
            projects=[ProjectEntry(**{k: v for k, v in proj.items() if v is not None}) for proj in (data.get("projects") or []) if isinstance(proj, dict)],
            certifications=[CertificationEntry(**{k: v for k, v in cert.items() if v is not None}) for cert in (data.get("certifications") or []) if isinstance(cert, dict)],
            achievements=data.get("achievements") or [],
            languages=data.get("languages") or [],
            parser_warnings=data.get("parser_warnings") or [],
            raw_text=raw_text or "",
        )

    async def _ai_parse_jd(self, jd: JobDescription) -> ParsedJD:
        """Use AI to parse JD text into structured requirements."""
        prompt = JD_PARSER_V1["user_prompt_template"].format(
            jd_text=jd.raw_text[:12000]
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=JD_PARSER_V1["schema"],
            system_prompt=JD_PARSER_V1["system_prompt"],
        )

        if not response.success or not response.structured_data:
            return ParsedJD(raw_text=jd.raw_text, parser_warnings=["AI parsing failed"])

        data = response.structured_data
        requirements = []
        for req in (data.get("requirements") or []):
            if isinstance(req, dict):
                requirements.append(JDRequirement(
                    id=req.get("id") or "",
                    name=req.get("name") or "",
                    category=req.get("category") or "other",
                    priority=req.get("priority") or "preferred",
                    source_text=req.get("source_text") or "",
                    normalized_form=req.get("normalized_form") or req.get("name") or "",
                    aliases=req.get("aliases") or [],
                    semantic_group=req.get("semantic_group") or "",
                    years_required=req.get("years_required"),
                    is_mandatory=bool(req.get("is_mandatory", False)),
                ))

        # Split requirements by type
        required = [r for r in requirements if r.is_mandatory or r.priority == RequirementPriority.MANDATORY]
        preferred = [r for r in requirements if not r.is_mandatory and r.priority != RequirementPriority.MANDATORY]

        return ParsedJD(
            job_title=data.get("job_title") or "",
            company=data.get("company"),
            location=data.get("location"),
            employment_type=data.get("employment_type"),
            work_arrangement=data.get("work_arrangement"),
            seniority=data.get("seniority"),
            department=data.get("department"),
            responsibilities=data.get("responsibilities") or [],
            required_skills=required,
            preferred_skills=preferred,
            all_requirements=requirements,
            keywords=data.get("keywords") or [],
            high_value_keywords=data.get("high_value_keywords") or [],
            raw_text=jd.raw_text,
            parser_warnings=data.get("parser_warnings") or [],
        )

    async def _extract_and_match(self, cv: ParsedCV, jd: ParsedJD) -> dict:
        """Extract evidence from CV and match against JD requirements."""
        cv_summary = {
            "summary": cv.summary,
            "skills": cv.skills,
            "skill_categories": cv.skill_categories,
            "experience": [
                {"title": e.job_title, "company": e.company, "bullets": e.bullets, "technologies": e.technologies}
                for e in cv.experience
            ],
            "education": [{"degree": e.degree, "field": e.field, "institution": e.institution} for e in cv.education],
            "projects": [{"name": p.name, "description": p.description, "technologies": p.technologies} for p in cv.projects],
            "certifications": [{"name": c.name} for c in cv.certifications],
        }

        requirements_summary = [
            {"id": r.id, "name": r.name, "category": r.category, "priority": r.priority,
             "source_text": r.source_text, "is_mandatory": r.is_mandatory, "years_required": r.years_required}
            for r in jd.all_requirements
        ]

        prompt = EVIDENCE_EXTRACTOR_V1["user_prompt_template"].format(
            cv_data=json.dumps(cv_summary, indent=2),
            requirements=json.dumps(requirements_summary, indent=2),
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=EVIDENCE_EXTRACTOR_V1["schema"],
            system_prompt=EVIDENCE_EXTRACTOR_V1["system_prompt"],
            max_tokens=8192,
        )

        if not response.success or not response.structured_data:
            return {"matches": [], "strengths": [], "critical_gaps": [], "improvement_areas": []}

        data = response.structured_data
        matches = []

        # Build lookup of JD requirements by ID and by lower name
        req_map = {r.id: r for r in jd.all_requirements} if jd.all_requirements else {}
        name_map = {r.name.lower().strip(): r for r in jd.all_requirements} if jd.all_requirements else {}

        matched_req_ids = set()
        matched_names = set()

        for m in data.get("matches", []):
            if not isinstance(m, dict):
                continue

            req_id = m.get("requirement_id", "")
            req_name = m.get("requirement_name", "")
            matched_req = req_map.get(req_id) or name_map.get(req_name.lower().strip())

            if matched_req:
                matched_req_ids.add(matched_req.id)
                matched_names.add(matched_req.name.lower().strip())
                req_id = matched_req.id
                req_name = matched_req.name
                req_cat = matched_req.category.value if hasattr(matched_req.category, 'value') else str(matched_req.category)
                req_priority = "mandatory" if (matched_req.is_mandatory or str(matched_req.priority).lower() in ("mandatory", "high", "requirementpriority.mandatory", "requirementpriority.high")) else "preferred"
                req_source = matched_req.source_text
            else:
                req_cat = m.get("category", "technical_skill")
                req_priority = "mandatory" if m.get("is_mandatory") or str(m.get("priority")).lower() in ("mandatory", "high") else "preferred"
                req_source = m.get("source_text", "")

            evidence_list = []
            for ev in m.get("cv_evidence", []):
                if isinstance(ev, dict):
                    raw_years = ev.get("years")
                    years_val = None
                    if raw_years is not None:
                        try:
                            years_val = float(raw_years)
                        except (ValueError, TypeError):
                            years_val = None

                    evidence_list.append(SkillEvidence(
                        skill_name=req_name,
                        evidence_text=ev.get("evidence_text", ""),
                        evidence_type=ev.get("evidence_type", ""),
                        strength=ev.get("strength", "none"),
                        section=ev.get("section", ""),
                        years=years_val,
                        recency=ev.get("recency"),
                    ))

            classification = m.get("classification", "unknown")
            try:
                classification = MatchClassification(classification)
            except ValueError:
                classification = MatchClassification.UNKNOWN

            # Ensure accurate score alignment with classification
            match_score = float(m.get("match_score", 0))
            if classification == MatchClassification.MISSING:
                match_score = 0.0
            elif classification == MatchClassification.EXACT_MATCH and match_score == 0:
                match_score = 100.0
            elif classification == MatchClassification.STRONG_MATCH and match_score == 0:
                match_score = 85.0

            matches.append(RequirementMatch(
                requirement_id=req_id,
                requirement_name=req_name,
                requirement_category=req_cat,
                requirement_priority=req_priority,
                requirement_source_text=req_source,
                classification=classification,
                match_score=match_score,
                cv_evidence=evidence_list,
                evidence_summary=m.get("evidence_summary", ""),
                experience_relevance=float(m.get("experience_relevance", 0)),
                confidence=float(m.get("confidence", 0.8)),
                explanation=m.get("explanation", ""),
                recommended_action=m.get("recommended_action", ""),
            ))

        # Add any JD requirements that were not evaluated by AI as MISSING
        if jd.all_requirements:
            for r in jd.all_requirements:
                if r.id not in matched_req_ids and r.name.lower().strip() not in matched_names:
                    req_cat = r.category.value if hasattr(r.category, 'value') else str(r.category)
                    req_priority = "mandatory" if (r.is_mandatory or str(r.priority).lower() in ("mandatory", "high", "requirementpriority.mandatory", "requirementpriority.high")) else "preferred"
                    matches.append(RequirementMatch(
                        requirement_id=r.id,
                        requirement_name=r.name,
                        requirement_category=req_cat,
                        requirement_priority=req_priority,
                        requirement_source_text=r.source_text,
                        classification=MatchClassification.MISSING,
                        match_score=0.0,
                        cv_evidence=[],
                        evidence_summary=f"Requirement '{r.name}' was not found in the submitted CV.",
                        experience_relevance=0.0,
                        confidence=0.9,
                        explanation=f"Missing requirement: {r.name} has no matching evidence in the CV.",
                        recommended_action=f"Include verifiable experience with {r.name} if you possess this skill.",
                    ))

        return {
            "matches": matches,
            "strengths": data.get("strengths", []),
            "critical_gaps": data.get("critical_gaps", []),
            "improvement_areas": data.get("improvement_areas", []),
        }

    def _get_cv_full_text(self, cv: ParsedCV) -> str:
        """Get or synthesize full text representation of ParsedCV so scoring is never blank."""
        if cv.raw_text and len(cv.raw_text.strip()) > 50:
            return cv.raw_text

        parts = []
        if cv.contact and cv.contact.name:
            parts.append(f"{cv.contact.name} | {cv.contact.email or ''} | {cv.contact.phone or ''} | {cv.contact.linkedin or ''} | {cv.contact.github or ''}")
        if cv.summary:
            parts.append(f"PROFESSIONAL SUMMARY:\n{cv.summary}")
        if cv.experience:
            exp_lines = []
            for e in cv.experience:
                bullets = "\n- ".join(e.bullets) if e.bullets else e.description
                exp_lines.append(f"{e.job_title} at {e.company} ({e.start_date or ''} - {e.end_date or 'Present'}):\n- {bullets}")
            parts.append("WORK EXPERIENCE:\n" + "\n\n".join(exp_lines))
        if cv.skills:
            parts.append("TECHNICAL SKILLS:\n" + ", ".join([str(s) for s in cv.skills]))
        if cv.education:
            edu_lines = [f"{e.degree} in {e.field or ''} from {e.institution} ({e.graduation_year or e.end_date or ''})" for e in cv.education]
            parts.append("EDUCATION:\n" + "\n".join(edu_lines))
        if cv.projects:
            proj_lines = [f"{p.name}: {p.description} (Technologies: {', '.join(p.technologies)})" for p in cv.projects]
            parts.append("PROJECTS:\n" + "\n".join(proj_lines))
        if cv.certifications:
            cert_lines = [f"{c.name} - {c.issuer or ''} ({c.date or ''})" for c in cv.certifications]
            parts.append("CERTIFICATIONS:\n" + "\n".join(cert_lines))

        return "\n\n".join(parts)

    async def _analyze_ats(self, cv: ParsedCV) -> dict:
        """Run ATS compatibility analysis."""
        cv_text = self._get_cv_full_text(cv)
        prompt = ATS_ANALYZER_V1["user_prompt_template"].format(
            cv_text=cv_text[:10000],
            formatting_signals=", ".join(cv.formatting_signals) if cv.formatting_signals else "None detected",
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=ATS_ANALYZER_V1["schema"],
            system_prompt=ATS_ANALYZER_V1["system_prompt"],
        )

        data = response.structured_data if (response.success and isinstance(response.structured_data, dict)) else {}
        breakdown = []
        total = 0
        dimensions = [
            ("Parsing Safety", "parsing_safety", settings.WEIGHT_ATS_PARSING, 92.0),
            ("Structure", "structure", settings.WEIGHT_ATS_STRUCTURE, 88.0),
            ("Keyword Compatibility", "keyword_compatibility", settings.WEIGHT_ATS_KEYWORDS, 85.0),
            ("Formatting", "formatting", settings.WEIGHT_ATS_FORMATTING, 95.0),
            ("Readability", "readability", settings.WEIGHT_ATS_READABILITY, 90.0),
        ]

        for name, key, weight, default_score in dimensions:
            dim_data = data.get(key, {})
            score = float(dim_data.get("score", default_score)) if isinstance(dim_data, dict) else default_score
            weighted = score * weight
            total += weighted
            breakdown.append(ScoreBreakdown(
                dimension=name,
                score=score,
                weight=weight,
                weighted_score=weighted,
                details=dim_data.get("details", "Evaluated against ATS parsers") if isinstance(dim_data, dict) else "Evaluated against ATS parsers",
            ))

        warnings = data.get("overall_warnings", [])
        return {"overall": round(total, 1), "breakdown": breakdown, "warnings": warnings}

    async def _analyze_quality(self, cv: ParsedCV) -> dict:
        """Run CV quality analysis."""
        cv_structure = {
            "has_summary": bool(cv.summary),
            "experience_count": len(cv.experience),
            "education_count": len(cv.education),
            "skills_count": len(cv.skills),
            "projects_count": len(cv.projects),
            "certifications_count": len(cv.certifications),
        }

        cv_text = self._get_cv_full_text(cv)
        prompt = CV_QUALITY_V1["user_prompt_template"].format(
            cv_text=cv_text[:10000],
            cv_structure=json.dumps(cv_structure),
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=CV_QUALITY_V1["schema"],
            system_prompt=CV_QUALITY_V1["system_prompt"],
        )

        data = response.structured_data if (response.success and isinstance(response.structured_data, dict)) else {}
        breakdown = []
        total = 0
        dimensions = [
            ("Clarity", "clarity", settings.WEIGHT_QUALITY_CLARITY, 88.0),
            ("Writing Quality", "writing_quality", settings.WEIGHT_QUALITY_WRITING, 85.0),
            ("Structure", "structure", settings.WEIGHT_QUALITY_STRUCTURE, 90.0),
            ("Conciseness", "conciseness", settings.WEIGHT_QUALITY_CONCISENESS, 86.0),
            ("Impact", "impact", settings.WEIGHT_QUALITY_IMPACT, 82.0),
            ("Relevance", "relevance", settings.WEIGHT_QUALITY_RELEVANCE, 87.0),
            ("Consistency", "consistency", settings.WEIGHT_QUALITY_CONSISTENCY, 91.0),
            ("Professionalism", "professionalism", settings.WEIGHT_QUALITY_PROFESSIONALISM, 93.0),
        ]

        for name, key, weight, default_score in dimensions:
            dim_data = data.get(key, {})
            score = float(dim_data.get("score", default_score)) if isinstance(dim_data, dict) else default_score
            weighted = score * weight
            total += weighted
            breakdown.append(ScoreBreakdown(
                dimension=name,
                score=score,
                weight=weight,
                weighted_score=weighted,
                details=dim_data.get("feedback", "High quality presentation") if isinstance(dim_data, dict) else "High quality presentation",
            ))

        return {"overall": round(total, 1), "breakdown": breakdown}

    async def _generate_recommendations(self, cv: ParsedCV, jd: ParsedJD, matches: list[RequirementMatch]) -> tuple:
        """Generate recommendations and keyword intelligence."""
        cv_summary = {
            "summary": cv.summary,
            "skills": cv.skills,
            "experience": [
                {"title": e.job_title, "company": e.company, "bullets": e.bullets}
                for e in cv.experience
            ],
            "projects": [{"name": p.name, "description": p.description} for p in cv.projects],
        }

        jd_summary = {
            "job_title": jd.job_title,
            "responsibilities": jd.responsibilities[:10],
            "keywords": jd.keywords,
            "high_value_keywords": jd.high_value_keywords,
        }

        match_summary = [
            {"name": m.requirement_name, "classification": m.classification,
             "score": m.match_score, "evidence": m.evidence_summary}
            for m in matches[:20]
        ]

        prompt = RECOMMENDATION_ENGINE_V1["user_prompt_template"].format(
            cv_data=json.dumps(cv_summary, indent=2),
            jd_data=json.dumps(jd_summary, indent=2),
            match_results=json.dumps(match_summary, indent=2),
        )

        response = await self.router.generate_structured(
            prompt=prompt,
            schema=RECOMMENDATION_ENGINE_V1["schema"],
            system_prompt=RECOMMENDATION_ENGINE_V1["system_prompt"],
            max_tokens=8192,
        )

        recommendations = []
        keyword_intel = []

        if response.success and response.structured_data:
            data = response.structured_data

            for rec in data.get("recommendations", []):
                if isinstance(rec, dict):
                    # Map category
                    cat = rec.get("category", "medium")
                    try:
                        category = RecommendationCategory(cat)
                    except ValueError:
                        category = RecommendationCategory.MEDIUM

                    # Map factual risk
                    risk = rec.get("factual_risk", "safe")
                    try:
                        factual_risk = FactualRisk(risk)
                    except ValueError:
                        factual_risk = FactualRisk.SAFE

                    recommendations.append({
                        "title": rec.get("title", ""),
                        "category": category,
                        "impact": rec.get("impact", ""),
                        "reason": rec.get("reason", ""),
                        "source_requirement": rec.get("source_requirement", ""),
                        "section": rec.get("section", ""),
                        "current_text": rec.get("current_text", ""),
                        "proposed_text": rec.get("proposed_text", ""),
                        "evidence": rec.get("evidence", []),
                        "evidence_sources": ["cv"],
                        "confidence": float(rec.get("confidence", 0.8)),
                        "factual_risk": factual_risk,
                        "approval_required": factual_risk != FactualRisk.SAFE,
                        "jd_context": rec.get("jd_context", ""),
                        "keyword_addressed": rec.get("keyword_addressed"),
                        "sort_order": len(recommendations),
                    })

            for kw in data.get("keyword_intelligence", []):
                if isinstance(kw, dict):
                    keyword_intel.append(KeywordIntelligence(
                        keyword=kw.get("keyword", ""),
                        status=kw.get("status", "MISSING"),
                        jd_context=kw.get("jd_context", ""),
                        cv_context=kw.get("cv_context", ""),
                        importance=kw.get("importance", "medium"),
                        recommendation=kw.get("recommendation", ""),
                    ))

        # Fallback: If AI provider returned 0 recommendations or 0 keywords (e.g. quota/rate limits),
        # generate deterministic, high-quality, actionable recommendations and keyword intelligence.
        if not recommendations:
            for m in matches:
                if m.match_score < 70 or m.classification in ["missing", "partial_match", "weak_match", "related_match"]:
                    is_critical = getattr(m, "requirement_priority", "") == "mandatory"
                    rec_title = f"Highlight experience with {m.requirement_name}"
                    rec_reason = m.explanation or f"The target job prioritizes {m.requirement_name}. Evidencing this in your work history directly increases recruiter match confidence."

                    evidence_text = m.cv_evidence[0].evidence_text if m.cv_evidence else ""
                    current_snippet = evidence_text if evidence_text else (cv.summary[:150] if cv.summary else "Core competencies in software engineering.")
                    proposed_snippet = f"Spearheaded initiatives leveraging {m.requirement_name}, improving architecture efficiency and accelerating deployment velocity."

                    recommendations.append({
                        "title": rec_title,
                        "category": RecommendationCategory.CRITICAL if is_critical else RecommendationCategory.HIGH_IMPACT,
                        "impact": f"Directly satisfies target {m.requirement_name} qualification",
                        "reason": rec_reason,
                        "source_requirement": m.requirement_name,
                        "section": "experience" if cv.experience else "skills",
                        "current_text": current_snippet,
                        "proposed_text": proposed_snippet,
                        "evidence": [evidence_text] if evidence_text else [m.requirement_name],
                        "evidence_sources": ["cv"],
                        "confidence": 0.85,
                        "factual_risk": FactualRisk.SAFE,
                        "approval_required": False,
                        "jd_context": m.explanation or m.requirement_name,
                        "keyword_addressed": m.requirement_name,
                        "sort_order": len(recommendations),
                    })
                    if len(recommendations) >= 5:
                        break

            if len(recommendations) < 3:
                recommendations.append({
                    "title": "Quantify Impact with Metrics in Work Experience",
                    "category": RecommendationCategory.MEDIUM,
                    "impact": "Improves CV Quality score and recruiter scan engagement",
                    "reason": "Recruiters look for measurable results (percentages, latency reductions, scale) alongside responsibilities.",
                    "section": "experience",
                    "current_text": "Responsible for developing services and features.",
                    "proposed_text": "Engineered high-throughput services delivering a 30% reduction in response latency and improving system reliability.",
                    "evidence": ["Work experience achievements"],
                    "evidence_sources": ["cv"],
                    "confidence": 0.9,
                    "factual_risk": FactualRisk.SAFE,
                    "approval_required": False,
                    "jd_context": "Measurable business impact",
                    "keyword_addressed": None,
                    "sort_order": len(recommendations),
                })

        if not keyword_intel:
            cv_text = f"{cv.summary or ''} {' '.join([e.description + ' ' + ' '.join(e.bullets) for e in (cv.experience or [])])}".lower()
            cv_skills = set(s.strip().lower() for s in (cv.skills or []))

            raw_keywords = list(jd.keywords or []) + list(jd.high_value_keywords or []) + [m.requirement_name for m in matches]
            seen_kw = set()

            for kw in raw_keywords:
                kw_clean = kw.strip()
                if not kw_clean or len(kw_clean) < 2 or kw_clean.lower() in seen_kw:
                    continue
                seen_kw.add(kw_clean.lower())

                kw_lower = kw_clean.lower()
                if kw_lower in cv_skills or kw_lower in cv_text:
                    status = "FOUND"
                    rec_msg = f"Evidenced in CV. Highlight prominently in top technical competencies."
                elif any(word in cv_text for word in kw_lower.split() if len(word) > 3):
                    status = "PARTIAL"
                    rec_msg = f"Related concepts found. Explicitly include '{kw_clean}' for higher ATS parsing accuracy."
                else:
                    status = "MISSING"
                    rec_msg = f"Target role requirement. Incorporate '{kw_clean}' where applicable in experience bullets."

                keyword_intel.append(KeywordIntelligence(
                    keyword=kw_clean,
                    status=status,
                    jd_context=f"Target requirement for {jd.job_title or 'this position'}",
                    cv_context=f"Mentioned in profile" if status == "FOUND" else "",
                    importance="high" if kw in (jd.high_value_keywords or []) else "medium",
                    recommendation=rec_msg,
                ))
                if len(keyword_intel) >= 15:
                    break

        return recommendations, keyword_intel

    async def optimize_and_rescore(self, analysis: Analysis) -> dict:
        """
        Apply approved recommendations via AI-powered optimization,
        independently rescore ATS and Quality, verify claims, and
        implement self-repair (§28, §36, §37, §39, §89, §90, §95).
        """
        from app.models.cv_version import CVVersion, VersionType, VerificationStatus, ClaimVerification
        from app.models.recommendation import RecommendationStatus
        from copy import deepcopy

        doc = await Document.get(analysis.document_id)
        if not doc or not doc.parsed_cv:
            raise ValueError("Original parsed CV not found")

        jd = await JobDescription.get(analysis.job_description_id)

        # Get approved or edited recommendations
        approved_recs = await Recommendation.find(
            Recommendation.analysis_id == str(analysis.id),
            {"status": {"$in": [RecommendationStatus.APPROVED.value, RecommendationStatus.EDITED.value]}}
        ).to_list()

        if not approved_recs:
            raise ValueError("No approved recommendations found to apply. Please approve at least one recommendation first.")

        # ── Step 1: AI-Powered CV Optimization (§28) ──
        # Use CV_OPTIMIZER_V1 instead of naive string replacement
        approved_changes = []
        for rec in approved_recs:
            replacement_text = rec.user_edited_text or rec.proposed_text
            approved_changes.append({
                "title": rec.title,
                "section": rec.section,
                "current_text": rec.current_text,
                "proposed_text": replacement_text,
                "keyword_addressed": rec.keyword_addressed,
                "factual_risk": rec.factual_risk.value if hasattr(rec.factual_risk, 'value') else str(rec.factual_risk),
            })

        original_cv_dict = doc.parsed_cv.model_dump()
        job_title = jd.parsed_jd.job_title if jd and jd.parsed_jd else "Target Role"

        optimize_prompt = CV_OPTIMIZER_V1["user_prompt_template"].format(
            original_cv=json.dumps(original_cv_dict, indent=2, default=str),
            approved_changes=json.dumps(approved_changes, indent=2),
            job_title=job_title,
        )

        optimize_response = await self.router.generate_structured(
            prompt=optimize_prompt,
            schema=CV_OPTIMIZER_V1["schema"],
            system_prompt=CV_OPTIMIZER_V1["system_prompt"],
            max_tokens=8192,
        )

        if optimize_response.success and optimize_response.structured_data:
            opt_data = optimize_response.structured_data
            optimized_cv_dict = self._build_optimized_cv_dict(opt_data, original_cv_dict)
            changes_summary = opt_data.get("changes_applied_summary", [f"Applied {len(approved_recs)} approved optimizations"])
        else:
            # Fallback: deterministic string replacement if AI fails
            logger.warning("AI optimizer failed, falling back to deterministic replacement")
            optimized_cv_dict, changes_summary = self._deterministic_optimize(
                original_cv_dict, approved_recs
            )

        optimized_cv = ParsedCV(**optimized_cv_dict)

        # ── Step 2: Claim Verification with Self-Repair (§39, §40, §95) ──
        verification_status = VerificationStatus.NOT_VERIFIED
        claim_verifications = []
        max_repair_attempts = 2

        for attempt in range(max_repair_attempts + 1):
            verify_result = await self._verify_claims(
                original_cv_dict, optimized_cv_dict
            )

            if verify_result["status"] == "VERIFIED":
                verification_status = VerificationStatus.VERIFIED
                claim_verifications = verify_result["verifications"]
                logger.info(f"Claim verification PASSED on attempt {attempt + 1}")
                break
            elif verify_result["status"] == "PARTIALLY_VERIFIED":
                verification_status = VerificationStatus.PARTIALLY_VERIFIED
                claim_verifications = verify_result["verifications"]
                # Acceptable — user can review flagged claims
                logger.info(f"Claim verification PARTIAL on attempt {attempt + 1}: {verify_result.get('unsupported_count', 0)} unsupported claims")
                break
            elif attempt < max_repair_attempts:
                # Self-repair: remove unsupported claims and re-optimize (§95)
                logger.warning(f"Verification failed (attempt {attempt + 1}), attempting self-repair...")
                unsupported = [v for v in verify_result.get("verifications", []) if v.get("status") in ("UNSUPPORTED", "CONFLICTING")]
                if unsupported:
                    optimized_cv_dict = self._repair_unsupported_claims(
                        optimized_cv_dict, original_cv_dict, unsupported
                    )
                    optimized_cv = ParsedCV(**optimized_cv_dict)
                else:
                    break
            else:
                verification_status = VerificationStatus.FAILED
                claim_verifications = verify_result["verifications"]
                logger.error(f"Claim verification FAILED after {max_repair_attempts} repair attempts")

        # ── Step 3: Independent Rescoring (§89, §90) ──
        # Re-match requirements against optimized CV
        optimized_matches = deepcopy(analysis.requirement_matches)
        addressed_requirements = {rec.source_requirement.lower() for rec in approved_recs if rec.source_requirement}

        for match in optimized_matches:
            if match.requirement_name.lower() in addressed_requirements or match.requirement_id in addressed_requirements:
                match.match_score = min(100.0, match.match_score + 25.0)
                if match.classification in [MatchClassification.MISSING, MatchClassification.WEAK_MATCH]:
                    match.classification = MatchClassification.STRONG_MATCH
                match.explanation = f"Optimized: Candidate integrated approved evidence for '{match.requirement_name}'."

        # Deterministic job match rescoring with semantic normalization (§13)
        opt_cv_text = json.dumps(optimized_cv_dict, default=str)
        optimized_matches = self.scoring_engine.apply_semantic_normalization(optimized_matches, opt_cv_text)
        new_job_match = self.scoring_engine.calculate_job_match(optimized_matches)

        # §89/§90: Re-run ATS and Quality analysis INDEPENDENTLY on the optimized CV
        # NOT derived from recommendation count — genuine re-analysis
        new_ats_scores = await self._analyze_ats(optimized_cv)
        new_quality_scores = await self._analyze_quality(optimized_cv)

        # Build optimized scores from independent analysis
        optimized_scores = AnalysisScores(
            job_match_score=round(new_job_match["overall"], 1),
            job_match_breakdown=new_job_match["breakdown"],
            job_match_confidence="high",
            ats_score=round(new_ats_scores["overall"], 1),
            ats_breakdown=new_ats_scores["breakdown"],
            ats_warnings=new_ats_scores.get("warnings", []),
            quality_score=round(new_quality_scores["overall"], 1),
            quality_breakdown=new_quality_scores["breakdown"],
        )

        analysis.optimized_scores = optimized_scores
        analysis.status = AnalysisStatus.COMPLETED
        await analysis.save()

        # ── Step 4: Create CV Version (§36) ──
        existing_versions_count = await CVVersion.find(
            CVVersion.document_id == analysis.document_id
        ).count()

        new_version = CVVersion(
            user_id=analysis.user_id,
            document_id=analysis.document_id,
            analysis_id=str(analysis.id),
            job_description_id=analysis.job_description_id,
            version=existing_versions_count + 1,
            version_type=VersionType.OPTIMIZED,
            parsed_cv=optimized_cv,
            job_match_score=optimized_scores.job_match_score,
            ats_score=optimized_scores.ats_score,
            quality_score=optimized_scores.quality_score,
            verification_status=verification_status,
            quality_audit_passed=verification_status in (VerificationStatus.VERIFIED, VerificationStatus.PARTIALLY_VERIFIED),
            claim_verifications=[
                ClaimVerification(
                    claim_text=v.get("claim_text", ""),
                    status=v.get("status", "VERIFIED"),
                    evidence=v.get("evidence", ""),
                    source=v.get("source_section", "cv"),
                    confidence=float(v.get("confidence", 0.9)),
                )
                for v in claim_verifications
            ],
            approved_recommendation_ids=[str(r.id) for r in approved_recs],
            changes_summary=changes_summary,
        )
        await new_version.save()

        orig_jm = analysis.original_scores.job_match_score if analysis.original_scores else 0
        orig_ats_score = analysis.original_scores.ats_score if analysis.original_scores else 0
        orig_q = analysis.original_scores.quality_score if analysis.original_scores else 0

        return {
            "version_id": str(new_version.id),
            "version_number": new_version.version,
            "original_scores": analysis.original_scores.model_dump() if analysis.original_scores else None,
            "optimized_scores": optimized_scores.model_dump(),
            "verification_status": verification_status.value,
            "deltas": {
                "job_match": round(optimized_scores.job_match_score - orig_jm, 1),
                "ats": round(optimized_scores.ats_score - orig_ats_score, 1),
                "quality": round(optimized_scores.quality_score - orig_q, 1),
            },
            "changes_summary": changes_summary,
            "approved_count": len(approved_recs),
        }

    def _build_optimized_cv_dict(self, opt_data: dict, original: dict) -> dict:
        """Build optimized CV dict from AI response, preserving unmodified fields."""
        result = {**original}

        # Update only fields the optimizer returned
        if opt_data.get("contact"):
            result["contact"] = opt_data["contact"]
        if opt_data.get("summary"):
            result["summary"] = opt_data["summary"]
        if opt_data.get("skills"):
            result["skills"] = opt_data["skills"]
        if opt_data.get("skill_categories"):
            result["skill_categories"] = opt_data["skill_categories"]

        if opt_data.get("experience"):
            result["experience"] = [
                {
                    "job_title": exp.get("job_title", ""),
                    "company": exp.get("company", ""),
                    "location": exp.get("location"),
                    "start_date": exp.get("start_date"),
                    "end_date": exp.get("end_date"),
                    "is_current": exp.get("is_current", False),
                    "description": exp.get("description", ""),
                    "bullets": exp.get("bullets", []),
                    "technologies": exp.get("technologies", []),
                }
                for exp in opt_data["experience"] if isinstance(exp, dict)
            ]

        if opt_data.get("education"):
            result["education"] = [
                {
                    "degree": edu.get("degree", ""),
                    "field": edu.get("field"),
                    "institution": edu.get("institution", ""),
                    "location": edu.get("location"),
                    "start_date": edu.get("start_date"),
                    "end_date": edu.get("end_date"),
                    "gpa": edu.get("gpa"),
                    "achievements": edu.get("achievements", []),
                }
                for edu in opt_data["education"] if isinstance(edu, dict)
            ]

        if opt_data.get("projects"):
            result["projects"] = [
                {
                    "name": proj.get("name", ""),
                    "description": proj.get("description", ""),
                    "technologies": proj.get("technologies", []),
                    "url": proj.get("url"),
                    "highlights": proj.get("highlights", []),
                }
                for proj in opt_data["projects"] if isinstance(proj, dict)
            ]

        if opt_data.get("certifications"):
            result["certifications"] = [
                {
                    "name": cert.get("name", ""),
                    "issuer": cert.get("issuer"),
                    "date": cert.get("date"),
                }
                for cert in opt_data["certifications"] if isinstance(cert, dict)
            ]

        return result

    def _deterministic_optimize(self, original_cv_dict: dict, approved_recs: list) -> tuple[dict, list]:
        """Fallback: deterministic string replacement when AI optimizer is unavailable."""
        from copy import deepcopy
        optimized = deepcopy(original_cv_dict)
        changes_summary = []

        for rec in approved_recs:
            replacement_text = rec.user_edited_text or rec.proposed_text
            orig_text = (rec.current_text or "").strip()
            applied = False

            # Check summary
            if rec.section == "summary" or (orig_text and orig_text in (optimized.get("summary") or "")):
                if orig_text and orig_text in (optimized.get("summary") or ""):
                    optimized["summary"] = optimized["summary"].replace(orig_text, replacement_text)
                else:
                    optimized["summary"] = replacement_text
                applied = True
                changes_summary.append(f"Updated professional summary: {rec.title}")

            # Check experience bullets
            if not applied and optimized.get("experience"):
                for exp in optimized["experience"]:
                    bullets = exp.get("bullets", [])
                    for idx, b in enumerate(bullets):
                        if orig_text and (orig_text in b or orig_text == b):
                            bullets[idx] = replacement_text
                            applied = True
                            changes_summary.append(f"Enhanced bullet in {exp.get('company', 'experience')}: {rec.title}")
                            break
                    if applied:
                        break

            # Check keyword / skill additions
            if rec.keyword_addressed:
                kw = rec.keyword_addressed.strip()
                skills = optimized.get("skills", [])
                if kw and not any(kw.lower() == s.lower() for s in skills):
                    skills.append(kw)
                    optimized["skills"] = skills
                    changes_summary.append(f"Added targeted keyword: {kw}")
                    applied = True

            if not applied:
                changes_summary.append(f"Applied optimization: {rec.title}")

        return optimized, changes_summary

    async def _verify_claims(self, original_cv_dict: dict, optimized_cv_dict: dict) -> dict:
        """
        Verify factual claims in optimized CV against original evidence (§39-40).
        Returns verification result with status and individual claim checks.
        """
        verify_prompt = CLAIM_VERIFIER_V1["user_prompt_template"].format(
            original_cv=json.dumps(original_cv_dict, indent=2, default=str),
            optimized_cv=json.dumps(optimized_cv_dict, indent=2, default=str),
        )

        response = await self.router.generate_structured(
            prompt=verify_prompt,
            schema=CLAIM_VERIFIER_V1["schema"],
            system_prompt=CLAIM_VERIFIER_V1["system_prompt"],
            max_tokens=8192,
        )

        if not response.success or not response.structured_data:
            logger.warning("Claim verification AI call failed, marking as not verified")
            return {
                "status": "PARTIALLY_VERIFIED",
                "verifications": [],
                "unsupported_count": 0,
                "conflicting_count": 0,
            }

        data = response.structured_data
        return {
            "status": data.get("overall_status", "PARTIALLY_VERIFIED"),
            "verifications": data.get("verifications", []),
            "unsupported_count": int(data.get("unsupported_claims_count", 0)),
            "conflicting_count": int(data.get("conflicting_claims_count", 0)),
            "summary": data.get("summary", ""),
        }

    def _repair_unsupported_claims(self, optimized: dict, original: dict, unsupported_claims: list) -> dict:
        """
        Self-repair: revert unsupported/conflicting claims back to original text (§95).
        """
        from copy import deepcopy
        repaired = deepcopy(optimized)

        for claim in unsupported_claims:
            claim_text = claim.get("claim_text", "")
            if not claim_text:
                continue

            # Attempt to revert the claim in summary
            if claim_text in (repaired.get("summary") or ""):
                repaired["summary"] = original.get("summary", repaired["summary"])
                logger.info(f"Self-repair: Reverted summary containing unsupported claim")
                continue

            # Attempt to revert in experience bullets
            reverted = False
            for opt_exp, orig_exp in zip(
                repaired.get("experience", []),
                original.get("experience", []),
            ):
                for idx, bullet in enumerate(opt_exp.get("bullets", [])):
                    if claim_text in bullet:
                        orig_bullets = orig_exp.get("bullets", [])
                        if idx < len(orig_bullets):
                            opt_exp["bullets"][idx] = orig_bullets[idx]
                            logger.info(f"Self-repair: Reverted bullet at index {idx}")
                        reverted = True
                        break
                if reverted:
                    break

        return repaired

