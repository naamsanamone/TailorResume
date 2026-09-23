"""TailorResume — Resume Analysis API Route (score without modifying)"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.schemas.score import ScoreBreakdown
from app.schemas.resume import ResumeSection
from app.services.jd_analyzer import analyze_job_description
from app.services.matcher import match_resume_to_jd, match_section_to_jd
from app.services.scorer import calculate_ats_score, calculate_section_score

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

        # Per-section scoring using realistic and intuitive scoring formulas
        section_scores: Dict[str, Any] = {}
        for sec in sections:
            sec_type = (sec.get("type") or "").lower()
            if sec_type in ("summary", "experience", "skills"):
                res = await calculate_section_score(sec, jd_analysis)
                section_scores[sec_type] = res

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
