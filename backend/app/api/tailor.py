"""TailorResume — Resume Tailoring API Route"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from app.auth import get_current_user
from app.models.user import User
from app.schemas.score import TailorRequest, TailorResponse, ScoreBreakdown, SkillMatch
from app.services.tailor_engine import tailor_resume

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=TailorResponse)
async def tailor_resume_endpoint(
    request: TailorRequest,
    current_user: User = Depends(get_current_user),
):
    """Tailor a resume to match a specific job description."""
    try:
        sections = [s.model_dump() for s in request.resume_content]
        result = await tailor_resume(sections, request.job_description)
        
        breakdown = ScoreBreakdown(
            keyword_score=result.get("score_breakdown", {}).get("keyword_score", 0),
            semantic_score=result.get("score_breakdown", {}).get("semantic_score", 0),
            format_score=result.get("score_breakdown", {}).get("format_score", 0),
            completeness_score=result.get("score_breakdown", {}).get("completeness_score", 0),
        )
        
        # Convert tailored sections back to ResumeSection schemas
        from app.schemas.resume import ResumeSection
        tailored_sections = [ResumeSection(**s) for s in result.get("tailored_sections", sections)]
        
        return TailorResponse(
            tailored_content=tailored_sections,
            ats_score=result.get("ats_score", 0),
            score_breakdown=breakdown,
            keywords_added=result.get("keywords_added", []),
            changes_summary=result.get("changes_summary", []),
        )
    except Exception as e:
        logger.error(f"Failed to tailor resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor resume: {str(e)}")
