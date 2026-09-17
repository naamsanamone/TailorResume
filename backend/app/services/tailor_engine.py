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
    """Full tailoring pipeline."""
    
    if not jd_analysis:
        jd_analysis = await analyze_job_description(jd_text)
        
    match_results = await match_resume_to_jd(resume_sections, jd_analysis)
    missing_skills = match_results["missing_skills"]
    
    client = get_llm_client(for_content=True)
    
    tailored_sections = copy.deepcopy(resume_sections)
    changes_summary = []
    keywords_added = []
    
    for section in tailored_sections:
        sec_type = section.get("type", "").lower()
        
        if sec_type == "summary":
            prompt = TAILOR_SUMMARY_PROMPT.format(
                original_summary=section.get("text", ""),
                job_title=jd_analysis.get("jobTitle", "the role"),
                company=jd_analysis.get("company", "the company"),
                hard_skills=", ".join(jd_analysis.get("hardSkills", [])),
                soft_skills=", ".join(jd_analysis.get("softSkills", [])),
                missing_skills=", ".join(missing_skills[:5])
            )
            try:
                new_summary_data = await client.complete_json(prompt, "You are an expert resume writer. Do not fabricate experience.")
                section["text"] = new_summary_data.get("summary", section["text"])
                changes_summary.append("Rewrote professional summary to align with JD.")
                keywords_added.extend(new_summary_data.get("keywords_incorporated", []))
            except Exception as e:
                logger.error(f"Error tailoring summary: {e}")
                
        elif sec_type == "experience":
            for entry in section.get("entries", []):
                original_bullets = entry.get("bullets", [])
                if not original_bullets:
                    continue
                    
                prompt = TAILOR_BULLETS_PROMPT.format(
                    job_title=entry.get("title", ""),
                    bullets=json.dumps(original_bullets, indent=2),
                    missing_skills=", ".join(missing_skills),
                    responsibilities=json.dumps(jd_analysis.get("responsibilities", []), indent=2)
                )
                try:
                    new_bullets_data = await client.complete_json(prompt, "You are an expert resume writer. Apply the XYZ formula. Do not fabricate.")
                    entry["bullets"] = new_bullets_data.get("bullets", original_bullets)
                    changes_summary.append(f"Enhanced bullet points for {entry.get('title', 'role')}.")
                    keywords_added.extend(new_bullets_data.get("keywords_incorporated", []))
                except Exception as e:
                    logger.error(f"Error tailoring bullets: {e}")
                    
        elif sec_type == "skills":
            all_jd_skills_lower = set([s.lower() for s in jd_analysis.get("hardSkills", []) + jd_analysis.get("softSkills", [])])
            if "categories" in section:
                for cat in section["categories"]:
                    items = cat.get("items", [])
                    items.sort(key=lambda x: 0 if x.lower() in all_jd_skills_lower else 1)
            elif "items" in section:
                section["items"].sort(key=lambda x: 0 if x.lower() in all_jd_skills_lower else 1)
            changes_summary.append("Reordered skills to prioritize JD requirements.")

    keywords_added = list(set(keywords_added))
    
    new_score_data = await calculate_ats_score(tailored_sections, jd_text, jd_analysis)
    
    return {
        "tailored_sections": tailored_sections,
        "ats_score": new_score_data["ats_score"],
        "score_breakdown": new_score_data["breakdown"],
        "keywords_added": keywords_added,
        "changes_summary": changes_summary
    }
