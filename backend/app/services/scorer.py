import logging
from typing import Dict, Any, List, Optional
from app.services.jd_analyzer import analyze_job_description
from app.services.matcher import match_resume_to_jd

logger = logging.getLogger(__name__)

async def calculate_ats_score(
    resume_sections: List[Dict[str, Any]], 
    jd_text: str, 
    jd_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Calculate composite ATS score for a resume against a JD."""
    
    if not jd_analysis:
        jd_analysis = await analyze_job_description(jd_text)
        
    match_results = await match_resume_to_jd(resume_sections, jd_analysis)
    
    keyword_score = match_results["keyword_match_rate"] * 100
    semantic_score = match_results["semantic_similarity"] * 100
    format_score = 100.0
    completeness_score = 100.0
    
    section_types = [sec.get("type", "").lower() for sec in resume_sections]
    
    expected_sections = ["header", "summary", "skills", "experience", "education"]
    missing_sections = []
    for sec in expected_sections:
        if sec not in section_types:
            completeness_score -= 20.0
            missing_sections.append(sec)
            
    if not any(t == "experience" for t in section_types):
        format_score -= 30.0
    else:
        for sec in resume_sections:
            if sec.get("type") == "experience":
                has_bullets = any(len(entry.get("bullets", [])) > 0 for entry in sec.get("entries", []))
                if not has_bullets:
                    format_score -= 20.0
                    break
                    
    keyword_score = max(0, min(100, keyword_score))
    semantic_score = max(0, min(100, semantic_score))
    format_score = max(0, min(100, format_score))
    completeness_score = max(0, min(100, completeness_score))
    
    composite = (keyword_score * 0.50) + (semantic_score * 0.25) + (format_score * 0.15) + (completeness_score * 0.10)
    composite = max(0, min(100, composite))
    
    recommendations = []
    if missing_sections:
        recommendations.append(f"Add missing standard sections: {', '.join(missing_sections).title()}")
    
    missing_skills = match_results["missing_skills"]
    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append(f"Incorporate missing keywords naturally: {', '.join(top_missing)}")
        
    if format_score < 100:
        recommendations.append("Ensure your experience section uses bullet points starting with action verbs.")
        
    return {
        "ats_score": round(composite, 1),
        "breakdown": {
            "keyword_score": round(keyword_score, 1),
            "semantic_score": round(semantic_score, 1),
            "format_score": round(format_score, 1),
            "completeness_score": round(completeness_score, 1)
        },
        "matched_skills": match_results["matched_skills"],
        "partial_matches": match_results["partial_matches"],
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "jd_analysis": jd_analysis
    }
