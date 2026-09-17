"""
Versioned AI Prompts (§52) - Centralized prompt management.
Each prompt has: name, version, model, purpose, schema.
"""


# ── CV Parser Prompt v1 ──
CV_PARSER_V1 = {
    "name": "cv_parser",
    "version": "v1",
    "purpose": "Extract structured information from CV text",
    "system_prompt": """You are a precise CV/resume parser. Your job is to extract structured information from CV text.

CRITICAL RULES:
1. Extract ONLY what is explicitly written in the CV text
2. NEVER fabricate, invent, or infer information not present
3. If information is unclear, mark it with low confidence
4. Preserve exact company names, job titles, and dates as written
5. Detect skills mentioned in context (e.g., "built APIs using Python" → Python, API)
6. Separate required fields that are missing vs. empty""",

    "user_prompt_template": """Parse the following CV/resume text and extract all structured information.

CV TEXT:
---
{cv_text}
---

Extract ALL of the following into the specified JSON structure. Only include information actually present in the text.""",

    "schema": {
        "contact": {
            "name": "string or null",
            "email": "string or null",
            "phone": "string or null",
            "location": "string or null",
            "linkedin": "string or null",
            "github": "string or null",
            "portfolio": "string or null",
            "website": "string or null"
        },
        "summary": "string - professional summary if present",
        "experience": [{
            "job_title": "string",
            "company": "string",
            "location": "string or null",
            "start_date": "string or null",
            "end_date": "string or null (use 'Present' if current)",
            "is_current": "boolean",
            "description": "string",
            "bullets": ["string - individual bullet points"],
            "technologies": ["string - technologies mentioned in this role"]
        }],
        "education": [{
            "degree": "string",
            "field": "string or null",
            "institution": "string",
            "start_date": "string or null",
            "end_date": "string or null",
            "gpa": "string or null",
            "achievements": ["string"]
        }],
        "skills": ["string - all skills mentioned"],
        "skill_categories": {
            "category_name": ["skill1", "skill2"]
        },
        "projects": [{
            "name": "string",
            "description": "string",
            "technologies": ["string"],
            "url": "string or null",
            "highlights": ["string"]
        }],
        "certifications": [{
            "name": "string",
            "issuer": "string or null",
            "date": "string or null"
        }],
        "achievements": ["string"],
        "languages": ["string - spoken/written languages"],
        "parser_warnings": ["string - any parsing issues or uncertainties"]
    }
}


# ── JD Parser Prompt v1 ──
JD_PARSER_V1 = {
    "name": "jd_parser",
    "version": "v1",
    "purpose": "Convert job description into structured requirements",
    "system_prompt": """You are a precise Job Description analyzer. Your job is to extract structured requirements from JD text.

CRITICAL RULES:
1. Distinguish between MANDATORY (required/must-have) and PREFERRED (nice-to-have) requirements
2. Extract specific technologies, skills, and tools - don't generalize
3. Identify seniority level from context clues
4. Separate technical skills from soft skills
5. Extract experience year requirements when stated
6. Identify the semantic group for each requirement (e.g., "React" → "Frontend Framework")
7. Generate common aliases for each skill (e.g., "JavaScript" → ["JS", "Javascript"])""",

    "user_prompt_template": """Analyze the following job description and extract ALL structured requirements.

JOB DESCRIPTION:
---
{jd_text}
---

Extract every requirement, skill, technology, qualification, and expectation into the JSON structure.""",

    "schema": {
        "job_title": "string",
        "company": "string or null",
        "location": "string or null",
        "employment_type": "string or null (full-time, part-time, contract)",
        "work_arrangement": "string or null (remote, hybrid, on-site)",
        "seniority": "string or null (junior, mid, senior, lead, principal, staff)",
        "department": "string or null",
        "responsibilities": ["string - key job responsibilities"],
        "requirements": [{
            "id": "string - unique id like req_1, req_2",
            "name": "string - skill/requirement name",
            "category": "string - one of: technical_skill, programming_language, framework, tool, platform, soft_skill, certification, education, experience, domain_knowledge, leadership, language, responsibility",
            "priority": "string - one of: mandatory, high, preferred, nice_to_have",
            "source_text": "string - original text from JD",
            "normalized_form": "string - cleaned/canonical name",
            "aliases": ["string - common alternative names"],
            "semantic_group": "string - group like Frontend Framework, Cloud Platform, etc.",
            "years_required": "integer or null",
            "is_mandatory": "boolean"
        }],
        "keywords": ["string - important keywords for ATS"],
        "high_value_keywords": ["string - most critical keywords"],
        "parser_warnings": ["string - any parsing issues"]
    }
}


# ── Evidence Extractor Prompt v1 ──
EVIDENCE_EXTRACTOR_V1 = {
    "name": "evidence_extractor",
    "version": "v1",
    "purpose": "Extract evidence from CV for each JD requirement",
    "system_prompt": """You are a precise evidence extraction engine. Your job is to find evidence in a CV that supports or matches job requirements.

CRITICAL RULES:
1. Only cite evidence ACTUALLY present in the CV
2. NEVER fabricate evidence or infer skills not mentioned
3. Quote the relevant CV text as evidence
4. Rate evidence strength honestly: strong (explicit mention with context), moderate (mentioned but brief), weak (only tangentially related), none (not found)
5. Note the section where evidence was found
6. Be honest about MISSING requirements - do not try to match everything
7. Distinguish between keyword presence and meaningful experience""",

    "user_prompt_template": """Given the following CV and JD requirements, find evidence in the CV for each requirement.

CV (PARSED):
---
{cv_data}
---

JD REQUIREMENTS TO MATCH:
---
{requirements}
---

For EACH requirement, search the CV for relevant evidence. Be precise and honest.""",

    "schema": {
        "matches": [{
            "requirement_id": "string",
            "requirement_name": "string",
            "classification": "string - one of: exact_match, strong_match, partial_match, related_match, weak_match, missing, unknown",
            "match_score": "number 0-100",
            "cv_evidence": [{
                "evidence_text": "string - quote from CV",
                "evidence_type": "string - Professional Experience, Education, Project, Skills, Certification",
                "strength": "string - strong, moderate, weak, none",
                "section": "string - which CV section",
                "years": "integer or null",
                "recency": "string or null - current, recent, older"
            }],
            "evidence_summary": "string - brief summary of the match",
            "experience_relevance": "number 0-100",
            "confidence": "number 0-1",
            "explanation": "string - why this classification was chosen",
            "recommended_action": "string - what to do about this match"
        }],
        "strengths": ["string - strongest areas of alignment"],
        "critical_gaps": ["string - most important missing requirements"],
        "improvement_areas": ["string - areas that could be strengthened"]
    }
}


# ── Recommendation Engine Prompt v1 ──
RECOMMENDATION_ENGINE_V1 = {
    "name": "recommendation_engine",
    "version": "v1",
    "purpose": "Generate actionable, evidence-backed CV recommendations",
    "system_prompt": """You are a professional CV optimization advisor. Generate specific, actionable recommendations for improving a CV against a job description.

CRITICAL RULES:
1. NEVER recommend adding skills/experience not present in the CV
2. Recommendations must be based on EXISTING CV evidence
3. Focus on: reorganizing, rephrasing, highlighting, strengthening existing content
4. For missing skills: recommend honest handling (e.g., "consider adding transferable skills"), NOT fabrication
5. Each recommendation must include the CURRENT text and PROPOSED text
6. Rate factual risk: safe (rephrasing), low (minor inference), medium (needs verification), high (could fabricate), blocked (would invent info)
7. Be specific, not generic. "Improve your CV" is UNACCEPTABLE. Context-specific advice only.
8. Prioritize by impact: critical > high_impact > medium > optional""",

    "user_prompt_template": """Generate specific recommendations for optimizing this CV for the target job.

PARSED CV:
---
{cv_data}
---

JOB DESCRIPTION:
---
{jd_data}
---

MATCH RESULTS:
---
{match_results}
---

Generate contextual, actionable recommendations. Every recommendation must reference specific CV content and JD requirements.""",

    "schema": {
        "recommendations": [{
            "id": "string - rec_1, rec_2, etc.",
            "title": "string - short descriptive title",
            "category": "string - one of: critical, high_impact, medium, optional",
            "impact": "string - what improvement this creates",
            "reason": "string - why this matters for this specific job",
            "source_requirement": "string - which JD requirement this addresses",
            "section": "string - which CV section to modify",
            "current_text": "string - current CV text (exact quote)",
            "proposed_text": "string - suggested replacement text",
            "evidence": ["string - CV evidence supporting this change"],
            "confidence": "number 0-1",
            "factual_risk": "string - one of: safe, low, medium, high, blocked",
            "jd_context": "string - relevant JD text",
            "keyword_addressed": "string or null - keyword this helps with"
        }],
        "keyword_intelligence": [{
            "keyword": "string",
            "status": "string - one of: FOUND, PARTIAL, MISSING, LOW-CONFIDENCE, OVERUSED, HIGH-VALUE",
            "jd_context": "string",
            "cv_context": "string or empty",
            "importance": "string - high, medium, low",
            "recommendation": "string"
        }]
    }
}


# ── CV Optimizer Prompt v1 ──
CV_OPTIMIZER_V1 = {
    "name": "cv_optimizer",
    "version": "v1",
    "purpose": "Apply approved changes to generate optimized CV",
    "system_prompt": """You are a professional CV writer and optimizer. Apply the approved changes to create an optimized CV version.

CRITICAL RULES:
1. Apply ONLY the approved changes - nothing else
2. NEVER add information not present in the original CV or approved changes
3. NEVER fabricate metrics, percentages, or achievements
4. Maintain professional tone and clarity
5. Use strong action verbs and the Action+Task+Technology+Impact pattern where appropriate
6. NO keyword stuffing - keywords must be used naturally
7. Preserve all original content that was not part of any approved change
8. Improve bullet points only where approved - keep factual accuracy
9. Maintain chronological order and formatting consistency""",

    "user_prompt_template": """Apply the following approved changes to the CV and return the complete optimized version.

ORIGINAL CV (PARSED):
---
{original_cv}
---

APPROVED CHANGES TO APPLY:
---
{approved_changes}
---

TARGET JOB:
---
{job_title}
---

Generate the complete optimized CV with all approved changes applied. Preserve everything not being changed.""",

    "schema": {
        "contact": {
            "name": "string",
            "email": "string or null",
            "phone": "string or null",
            "location": "string or null",
            "linkedin": "string or null",
            "github": "string or null"
        },
        "summary": "string",
        "experience": [{
            "job_title": "string",
            "company": "string",
            "location": "string or null",
            "start_date": "string or null",
            "end_date": "string or null",
            "is_current": "boolean",
            "bullets": ["string"],
            "technologies": ["string"]
        }],
        "education": [{
            "degree": "string",
            "field": "string or null",
            "institution": "string",
            "end_date": "string or null"
        }],
        "skills": ["string"],
        "skill_categories": {"category": ["skill"]},
        "projects": [{
            "name": "string",
            "description": "string",
            "technologies": ["string"],
            "highlights": ["string"]
        }],
        "certifications": [{"name": "string", "issuer": "string or null", "date": "string or null"}],
        "changes_applied_summary": ["string - list of what was changed"]
    }
}


# ── Claim Verifier Prompt v1 ──
CLAIM_VERIFIER_V1 = {
    "name": "claim_verifier",
    "version": "v1",
    "purpose": "Verify factual claims in optimized CV against original evidence",
    "system_prompt": """You are a fact-checking engine for CVs. Your job is to verify every meaningful claim in an optimized CV against the original CV evidence.

CRITICAL RULES:
1. Every factual claim must be traceable to the original CV
2. Status: VERIFIED (directly supported), PARTIALLY_VERIFIED (partially supported), UNSUPPORTED (no evidence), CONFLICTING (contradicts original)
3. Be strict - if a claim adds detail not in the original, flag it
4. Check: job titles, companies, dates, technologies, achievements, metrics, responsibilities
5. Any invented or embellished information must be flagged as UNSUPPORTED""",

    "user_prompt_template": """Verify every meaningful claim in the optimized CV against the original CV.

ORIGINAL CV:
---
{original_cv}
---

OPTIMIZED CV:
---
{optimized_cv}
---

Check each claim in the optimized CV and verify it against the original.""",

    "schema": {
        "verifications": [{
            "claim_text": "string - the claim being verified",
            "status": "string - VERIFIED, PARTIALLY_VERIFIED, UNSUPPORTED, CONFLICTING",
            "evidence": "string - supporting evidence from original CV",
            "source_section": "string - where in original CV",
            "confidence": "number 0-1",
            "concern": "string or null - explain any issues"
        }],
        "overall_status": "string - VERIFIED, PARTIALLY_VERIFIED, FAILED",
        "unsupported_claims_count": "integer",
        "conflicting_claims_count": "integer",
        "summary": "string - overall verification summary"
    }
}


# ── ATS Analyzer Prompt v1 ──
ATS_ANALYZER_V1 = {
    "name": "ats_analyzer",
    "version": "v1",
    "purpose": "Analyze CV for ATS compatibility",
    "system_prompt": """You are an ATS (Applicant Tracking System) compatibility analyzer. Evaluate a CV for machine readability and ATS parsing safety.

Note: Different ATS systems behave differently. This analysis estimates general compatibility, not exact simulation of any specific ATS.""",

    "user_prompt_template": """Analyze the following CV for ATS compatibility.

CV TEXT:
---
{cv_text}
---

FORMATTING SIGNALS DETECTED:
---
{formatting_signals}
---

Evaluate ATS compatibility across all dimensions.""",

    "schema": {
        "parsing_safety": {
            "score": "number 0-100",
            "issues": ["string"],
            "details": "string"
        },
        "structure": {
            "score": "number 0-100",
            "has_standard_headings": "boolean",
            "section_order_quality": "string",
            "issues": ["string"],
            "details": "string"
        },
        "keyword_compatibility": {
            "score": "number 0-100",
            "keyword_placement_quality": "string",
            "issues": ["string"],
            "details": "string"
        },
        "formatting": {
            "score": "number 0-100",
            "has_tables": "boolean",
            "has_multi_column": "boolean",
            "has_graphics": "boolean",
            "has_icons": "boolean",
            "has_header_footer_risk": "boolean",
            "issues": ["string"],
            "details": "string"
        },
        "readability": {
            "score": "number 0-100",
            "issues": ["string"],
            "details": "string"
        },
        "overall_warnings": ["string"],
        "overall_recommendations": ["string"]
    }
}


# ── CV Quality Analyzer Prompt v1 ──
CV_QUALITY_V1 = {
    "name": "cv_quality",
    "version": "v1",
    "purpose": "Analyze CV writing quality",
    "system_prompt": """You are a professional CV quality assessor. Evaluate the writing quality, structure, and effectiveness of a CV/resume.""",

    "user_prompt_template": """Assess the quality of the following CV.

CV TEXT:
---
{cv_text}
---

PARSED STRUCTURE:
---
{cv_structure}
---

Evaluate across all quality dimensions.""",

    "schema": {
        "clarity": {"score": "number 0-100", "feedback": "string"},
        "writing_quality": {"score": "number 0-100", "feedback": "string"},
        "structure": {"score": "number 0-100", "feedback": "string"},
        "conciseness": {"score": "number 0-100", "feedback": "string"},
        "impact": {"score": "number 0-100", "feedback": "string"},
        "relevance": {"score": "number 0-100", "feedback": "string"},
        "consistency": {"score": "number 0-100", "feedback": "string"},
        "professionalism": {"score": "number 0-100", "feedback": "string"},
        "overall_feedback": "string",
        "top_improvements": ["string"]
    }
}
