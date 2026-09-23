"""TailorResume — Resume Analysis API Route (score without modifying)"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.schemas.score import ScoreBreakdown
from app.schemas.resume import ResumeSection
from app.services.jd_analyzer import analyze_job_description
from app.services.matcher import match_resume_to_jd, match_section_to_jd
from app.services.scorer import calculate_ats_score

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyzeRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str = Field(min_length=50)


class SectionScore(BaseModel):
    score: float = 0
    matched: List[str] = []
    missing: List[str] = []
    recommendation: str = ""


class ExperienceEntryScore(BaseModel):
    title: str = ""
    company: str = ""
    score: float = 0
    matched: List[str] = []
    missing: List[str] = []


class ExperienceSectionScore(SectionScore):
    entries: List[ExperienceEntryScore] = []


class AnalyzeResponse(BaseModel):
    overall_score: float
    breakdown: ScoreBreakdown
    section_scores: Dict[str, Any] = {}
    matched_skills: List[Dict[str, Any]] = []
    partial_matches: List[Dict[str, Any]] = []
    missing_skills: List[str] = []
    jd_analysis: Dict[str, Any] = {}
    recommendations: List[str] = []


@router.post("/", response_model=AnalyzeResponse)
async def analyze_resume_endpoint(request: AnalyzeRequest):
    """Analyze a resume against a job description — returns scores without modifying."""
    try:
        sections = [s.model_dump() for s in request.resume_content]

        # Overall score
        score_data = await calculate_ats_score(sections, request.job_description)
        jd_analysis = score_data.get("jd_analysis", {})

        breakdown = ScoreBreakdown(
            keyword_score=score_data["breakdown"]["keyword_score"],
            semantic_score=score_data["breakdown"]["semantic_score"],
            format_score=score_data["breakdown"]["format_score"],
            completeness_score=score_data["breakdown"]["completeness_score"],
        )

        # Per-section scoring
        section_scores: Dict[str, Any] = {}

        for sec in sections:
            sec_type = (sec.get("type") or "").lower()

            if sec_type == "summary":
                result = await match_section_to_jd(sec, jd_analysis)
                # Check if summary mentions the target role
                target_title = (jd_analysis.get("jobTitle") or "").lower()
                summary_text = (sec.get("text") or "").lower()
                if target_title and target_title not in summary_text:
                    result["recommendation"] = f'Rewrite your summary to mention the target role "{jd_analysis.get("jobTitle", "")}" and incorporate key skills: {", ".join(result["missing"][:3])}'
                elif result["score"] < 50:
                    result["recommendation"] = f'Enhance your summary with JD keywords: {", ".join(result["missing"][:3])}'
                else:
                    result["recommendation"] = "Summary has good keyword coverage."
                section_scores["summary"] = result

            elif sec_type == "experience":
                # Overall experience score
                result = await match_section_to_jd(sec, jd_analysis)
                if result["score"] < 50:
                    result["recommendation"] = "Add more JD-relevant keywords and quantified achievements to your bullet points."
                else:
                    result["recommendation"] = "Experience section has good keyword coverage."

                # Per-entry scoring
                entries = sec.get("entries") or []
                entry_scores = []
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    # Build a mini-section with just this entry's data
                    mini_section = {
                        "type": "experience",
                        "entries": [entry],
                    }
                    entry_result = await match_section_to_jd(mini_section, jd_analysis)
                    entry_scores.append({
                        "title": entry.get("title", ""),
                        "company": entry.get("company", ""),
                        "score": round(entry_result["score"], 1),
                        "matched": entry_result["matched"],
                        "missing": entry_result["missing"],
                    })

                result["entries"] = entry_scores
                section_scores["experience"] = result

            elif sec_type == "skills":
                result = await match_section_to_jd(sec, jd_analysis)
                if result["score"] < 50:
                    result["recommendation"] = f'Add missing skills: {", ".join(result["missing"][:5])}'
                else:
                    result["recommendation"] = "Skills section covers most JD requirements."
                section_scores["skills"] = result

        return AnalyzeResponse(
            overall_score=score_data["ats_score"],
            breakdown=breakdown,
            section_scores=section_scores,
            matched_skills=score_data.get("matched_skills", []),
            partial_matches=score_data.get("partial_matches", []),
            missing_skills=score_data.get("missing_skills", []),
            jd_analysis=jd_analysis,
            recommendations=score_data.get("recommendations", []),
        )
    except Exception as e:
        logger.error(f"Failed to analyze resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze resume: {str(e)}")
