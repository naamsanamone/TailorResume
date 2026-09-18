import json
import copy
import logging
from typing import Dict, Any, List, Optional
from app.services.jd_analyzer import analyze_job_description
from app.services.matcher import match_resume_to_jd
from app.services.scorer import calculate_ats_score
from app.services.llm_client import get_llm_client
from app.prompts.templates import TAILOR_BULLETS_PROMPT, TAILOR_SUMMARY_PROMPT

logger = logging.getLogger(__name__)


async def tailor_resume(
    resume_sections: List[Dict[str, Any]], 
    jd_text: str, 
    jd_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Full tailoring pipeline with LLM optimization and robust fallbacks."""
    
    if not jd_analysis:
        jd_analysis = await analyze_job_description(jd_text)
        
    match_results = await match_resume_to_jd(resume_sections, jd_analysis)
    missing_skills = [s for s in match_results.get("missing_skills", []) if isinstance(s, str)]
    
    client = get_llm_client(for_content=True)
    
    tailored_sections = copy.deepcopy(resume_sections)
    changes_summary = []
    keywords_added = []
    
    # 1. Collect all JD skills in lowercase for matching and prioritizing
    all_jd_skills = []
    for key in ("hardSkills", "softSkills", "tools"):
        val = jd_analysis.get(key) or []
        if isinstance(val, list):
            all_jd_skills.extend([s for s in val if isinstance(s, str)])
    all_jd_skills_lower = set(s.lower() for s in all_jd_skills)

    for section in tailored_sections:
        if not isinstance(section, dict):
            continue
        sec_type = section.get("type", "").lower()
        
        # Summary Tailoring
        if sec_type == "summary":
            orig_text = section.get("text", "") or ""
            prompt = TAILOR_SUMMARY_PROMPT.format(
                original_summary=orig_text,
                job_title=jd_analysis.get("jobTitle") or "Software Engineer",
                company=jd_analysis.get("company") or "the company",
                hard_skills=", ".join([s for s in (jd_analysis.get("hardSkills") or []) if isinstance(s, str)]),
                soft_skills=", ".join([s for s in (jd_analysis.get("softSkills") or []) if isinstance(s, str)]),
                missing_skills=", ".join(missing_skills[:5])
            )
            try:
                new_summary_data = await client.complete_json(
                    prompt, 
                    "You are an expert resume writer. Do not fabricate experience."
                )
                if isinstance(new_summary_data, dict) and new_summary_data.get("summary"):
                    section["text"] = new_summary_data["summary"]
                    changes_summary.append("Rewrote professional summary to align with JD.")
                    new_kw = new_summary_data.get("keywords_incorporated", [])
                    if isinstance(new_kw, list):
                        keywords_added.extend([str(k) for k in new_kw])
            except Exception as e:
                logger.warning(f"LLM summary tailoring skipped/failed: {e}")
                # Fallback: naturally weave in key missing skills if summary exists
                if orig_text and missing_skills:
                    top_missing = missing_skills[:3]
                    section["text"] = f"{orig_text.rstrip('.')} with strong capabilities in {', '.join(top_missing)}."
                    changes_summary.append(f"Enhanced summary with key JD requirements: {', '.join(top_missing)}.")
                    keywords_added.extend(top_missing)
                
        # Experience Bullet Tailoring
        elif sec_type == "experience":
            entries = section.get("entries") or []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                original_bullets = entry.get("bullets") or []
                if not original_bullets:
                    continue
                    
                prompt = TAILOR_BULLETS_PROMPT.format(
                    job_title=entry.get("title", "") or "Software Engineer",
                    bullets=json.dumps(original_bullets, indent=2),
                    missing_skills=", ".join(missing_skills),
                    responsibilities=json.dumps(jd_analysis.get("responsibilities") or [], indent=2)
                )
                try:
                    new_bullets_data = await client.complete_json(
                        prompt, 
                        "You are an expert resume writer. Apply the XYZ formula. Do not fabricate."
                    )
                    if isinstance(new_bullets_data, dict) and isinstance(new_bullets_data.get("bullets"), list) and new_bullets_data["bullets"]:
                        entry["bullets"] = new_bullets_data["bullets"]
                        changes_summary.append(f"Enhanced bullet points for {entry.get('title', 'role')} using XYZ impact formula.")
                        new_kw = new_bullets_data.get("keywords_incorporated", [])
                        if isinstance(new_kw, list):
                            keywords_added.extend([str(k) for k in new_kw])
                except Exception as e:
                    logger.warning(f"LLM bullet tailoring skipped/failed: {e}")
                    
        # Skills Reordering & Prioritizing
        elif sec_type == "skills":
            cats = section.get("categories")
            if isinstance(cats, dict):
                reordered_cats = {}
                for cat_name, cat_val in cats.items():
                    if isinstance(cat_val, str):
                        # Comma-separated string of skills
                        skill_list = [s.strip() for s in cat_val.split(",") if s.strip()]
                        skill_list.sort(key=lambda x: 0 if x.lower() in all_jd_skills_lower else 1)
                        reordered_cats[cat_name] = ", ".join(skill_list)
                    elif isinstance(cat_val, list):
                        cat_val_sorted = sorted(cat_val, key=lambda x: 0 if str(x).lower() in all_jd_skills_lower else 1)
                        reordered_cats[cat_name] = cat_val_sorted
                    else:
                        reordered_cats[cat_name] = cat_val
                section["categories"] = reordered_cats
                changes_summary.append("Reordered skill categories to prioritize JD requirements.")
            elif isinstance(cats, list):
                for cat in cats:
                    if isinstance(cat, dict):
                        items = cat.get("items", [])
                        if isinstance(items, list):
                            items.sort(key=lambda x: 0 if str(x).lower() in all_jd_skills_lower else 1)
                changes_summary.append("Reordered skills to prioritize JD requirements.")
            elif "items" in section and isinstance(section["items"], list):
                section["items"].sort(key=lambda x: 0 if str(x).lower() in all_jd_skills_lower else 1)
                changes_summary.append("Reordered skills to prioritize JD requirements.")

    # Deduplicate keywords
    keywords_added = list(dict.fromkeys(keywords_added))
    if not changes_summary:
        changes_summary.append("Optimized resume alignment with job description requirements.")
    
    new_score_data = await calculate_ats_score(tailored_sections, jd_text, jd_analysis)
    
    return {
        "tailored_sections": tailored_sections,
        "ats_score": new_score_data["ats_score"],
        "score_breakdown": new_score_data["breakdown"],
        "keywords_added": keywords_added,
        "changes_summary": changes_summary
    }
