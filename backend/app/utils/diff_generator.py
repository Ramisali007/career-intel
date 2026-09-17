"""
Diff Generator Utility (§38).
Computes visual and structural differences between original and optimized CV content.
"""

from typing import Any
import difflib


def generate_bullet_diff(original_text: str, modified_text: str) -> dict[str, Any]:
    """
    Generate word-level diff between two versions of a bullet point or text.
    """
    if original_text.strip() == modified_text.strip():
        return {
            "type": "unchanged",
            "original_text": original_text,
            "modified_text": modified_text,
            "highlighted_diff": [{"type": "unchanged", "text": modified_text}],
        }

    # Use difflib sequence matcher on words
    orig_words = original_text.split()
    mod_words = modified_text.split()
    matcher = difflib.SequenceMatcher(None, orig_words, mod_words)

    spans = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            spans.append({"type": "unchanged", "text": " ".join(orig_words[i1:i2])})
        elif tag == "replace":
            spans.append({"type": "removed", "text": " ".join(orig_words[i1:i2])})
            spans.append({"type": "added", "text": " ".join(mod_words[j1:j2])})
        elif tag == "delete":
            spans.append({"type": "removed", "text": " ".join(orig_words[i1:i2])})
        elif tag == "insert":
            spans.append({"type": "added", "text": " ".join(mod_words[j1:j2])})

    return {
        "type": "modified",
        "original_text": original_text,
        "modified_text": modified_text,
        "highlighted_diff": spans,
    }


def compare_parsed_cvs(original_cv: dict[str, Any], optimized_cv: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two ParsedCV dictionaries section-by-section and return structured diff (§38).
    """
    diff_report = {
        "summary": None,
        "experience": [],
        "skills": {
            "added": [],
            "removed": [],
            "retained": [],
        },
        "stats": {
            "added_count": 0,
            "modified_count": 0,
            "removed_count": 0,
            "unchanged_count": 0,
        },
    }

    # 1. Summary Diff
    orig_summary = original_cv.get("summary", "") or ""
    opt_summary = optimized_cv.get("summary", "") or ""
    if orig_summary or opt_summary:
        if orig_summary and not opt_summary:
            diff_report["summary"] = {
                "type": "removed",
                "original_text": orig_summary,
                "modified_text": "",
            }
            diff_report["stats"]["removed_count"] += 1
        elif opt_summary and not orig_summary:
            diff_report["summary"] = {
                "type": "added",
                "original_text": "",
                "modified_text": opt_summary,
            }
            diff_report["stats"]["added_count"] += 1
        else:
            diff_res = generate_bullet_diff(orig_summary, opt_summary)
            diff_report["summary"] = diff_res
            if diff_res["type"] == "modified":
                diff_report["stats"]["modified_count"] += 1
            else:
                diff_report["stats"]["unchanged_count"] += 1

    # 2. Experience Bullets Diff
    orig_exps = original_cv.get("experience", []) or []
    opt_exps = optimized_cv.get("experience", []) or []

    for i, opt_exp in enumerate(opt_exps):
        # Match by company or title or index
        orig_exp = orig_exps[i] if i < len(orig_exps) else {}
        exp_entry = {
            "title": opt_exp.get("title", ""),
            "company": opt_exp.get("company", ""),
            "period": f"{opt_exp.get('start_date', '')} - {opt_exp.get('end_date', 'Present')}",
            "bullets": [],
        }

        orig_bullets = orig_exp.get("bullets", []) or []
        opt_bullets = opt_exp.get("bullets", []) or []

        # Compare bullets
        for j, opt_b in enumerate(opt_bullets):
            orig_b = orig_bullets[j] if j < len(orig_bullets) else ""
            if not orig_b:
                b_diff = {
                    "type": "added",
                    "original_text": "",
                    "modified_text": opt_b,
                    "highlighted_diff": [{"type": "added", "text": opt_b}],
                }
                diff_report["stats"]["added_count"] += 1
            else:
                b_diff = generate_bullet_diff(orig_b, opt_b)
                if b_diff["type"] == "modified":
                    diff_report["stats"]["modified_count"] += 1
                else:
                    diff_report["stats"]["unchanged_count"] += 1
            exp_entry["bullets"].append(b_diff)

        diff_report["experience"].append(exp_entry)

    # 3. Skills Diff
    orig_skills = set(s.strip().lower() for s in original_cv.get("skills", []) if s)
    opt_skills = set(s.strip().lower() for s in optimized_cv.get("skills", []) if s)

    orig_skills_map = {s.strip().lower(): s for s in original_cv.get("skills", []) if s}
    opt_skills_map = {s.strip().lower(): s for s in optimized_cv.get("skills", []) if s}

    diff_report["skills"]["added"] = [opt_skills_map[s] for s in (opt_skills - orig_skills)]
    diff_report["skills"]["removed"] = [orig_skills_map[s] for s in (orig_skills - opt_skills)]
    diff_report["skills"]["retained"] = [opt_skills_map[s] for s in (orig_skills & opt_skills)]

    return diff_report
