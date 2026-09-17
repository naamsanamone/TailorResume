import re
import logging
from typing import List, Dict, Any
from app.services.embeddings import compute_similarity

logger = logging.getLogger(__name__)

COMMON_ABBREVIATIONS = {
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "react": "reactjs",
    "react.js": "reactjs",
    "node": "nodejs",
    "node.js": "nodejs",
    "vue": "vuejs",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "ui": "user interface",
    "ux": "user experience",
    "db": "database"
}

def normalize_skill(skill: str) -> str:
    """Lowercase, strip whitespace/hyphens/underscores."""
    s = skill.lower().strip()
    s = re.sub(r'[-_]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def fuzzy_match(a: str, b: str) -> bool:
    """Check if normalized versions match (exact, contains, or abbreviated)."""
    norm_a = normalize_skill(a)
    norm_b = normalize_skill(b)
    
    if norm_a == norm_b:
        return True
        
    if COMMON_ABBREVIATIONS.get(norm_a) == norm_b or COMMON_ABBREVIATIONS.get(norm_b) == norm_a:
        return True
        
    if norm_a in norm_b or norm_b in norm_a:
        words_a = set(norm_a.split())
        words_b = set(norm_b.split())
        if words_a.issubset(words_b) or words_b.issubset(words_a):
            return True
            
    return False

def stem_match(a: str, b: str) -> bool:
    """Basic stemming check (manage/managed/managing)."""
    norm_a = normalize_skill(a)
    norm_b = normalize_skill(b)
    
    suffixes = ['ing', 'ed', 's', 'ment', 'ion']
    base_a = norm_a
    base_b = norm_b
    
    for suffix in suffixes:
        if base_a.endswith(suffix):
            base_a = base_a[:-len(suffix)]
        if base_b.endswith(suffix):
            base_b = base_b[:-len(suffix)]
            
    return base_a == base_b and len(base_a) > 2

def _extract_resume_text(resume_sections: List[Dict[str, Any]]) -> str:
    """Helper to extract all text from resume sections."""
    text_parts = []
    for section in resume_sections:
        if "text" in section and section["text"]:
            text_parts.append(section["text"])
        if "items" in section:
            text_parts.extend([item for item in section["items"] if isinstance(item, str)])
        if "entries" in section:
            for entry in section["entries"]:
                if "title" in entry: text_parts.append(entry["title"])
                if "company" in entry: text_parts.append(entry["company"])
                if "bullets" in entry: text_parts.extend(entry["bullets"])
        if "categories" in section:
            for cat in section["categories"]:
                if "items" in cat:
                    text_parts.extend(cat["items"])
    return " ".join(text_parts).lower()

async def match_resume_to_jd(resume_sections: List[Dict[str, Any]], jd_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Perform matching between resume and JD."""
    resume_text = _extract_resume_text(resume_sections)
    
    jd_skills = []
    jd_skills.extend(jd_analysis.get("hardSkills", []))
    jd_skills.extend(jd_analysis.get("softSkills", []))
    jd_skills.extend(jd_analysis.get("tools", []))
    jd_skills.extend([jd_analysis.get("domain", "")])
    jd_skills = [s for s in jd_skills if s.strip()]
    
    matched_skills = []
    partial_matches = []
    missing_skills = []
    
    for jd_skill in set(jd_skills):
        skill_found = False
        
        norm_jd = normalize_skill(jd_skill)
        escaped_skill = re.escape(norm_jd)
        if re.search(rf'\b{escaped_skill}\b', resume_text):
            matched_skills.append({"skill": jd_skill, "match_type": "exact", "confidence": 1.0})
            skill_found = True
            continue
            
        for token in resume_text.split():
            if fuzzy_match(jd_skill, token) or stem_match(jd_skill, token):
                matched_skills.append({"skill": jd_skill, "match_type": "fuzzy", "confidence": 0.9})
                skill_found = True
                break
                
        if skill_found:
            continue
            
        sentences = [s.strip() for s in resume_text.split('.') if len(s.strip()) > 10]
        max_sim = 0.0
        for sentence in sentences:
            sim = compute_similarity(jd_skill, sentence)
            if sim > max_sim:
                max_sim = sim
                
        if max_sim > 0.75:
            matched_skills.append({"skill": jd_skill, "match_type": "semantic", "confidence": max_sim})
        elif max_sim > 0.5:
            partial_matches.append({"skill": jd_skill, "match_type": "semantic", "confidence": max_sim})
        else:
            missing_skills.append(jd_skill)
            
    total_keywords = len(jd_skills)
    keyword_match_rate = len(matched_skills) / total_keywords if total_keywords > 0 else 0.0
    
    jd_full_text = " ".join([str(v) for v in jd_analysis.values() if v])
    overall_semantic_sim = compute_similarity(jd_full_text, resume_text)
    
    return {
        "matched_skills": matched_skills,
        "partial_matches": partial_matches,
        "missing_skills": missing_skills,
        "keyword_match_rate": keyword_match_rate,
        "semantic_similarity": overall_semantic_sim
    }
