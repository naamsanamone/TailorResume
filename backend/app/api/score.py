"""TailorResume — ATS Score API Route"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from app.auth import get_current_user
from app.models.user import User
from app.schemas.score import ScoreRequest, ScoreResponse, ScoreBreakdown, SkillMatch
from app.services.scorer import calculate_ats_score

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ScoreResponse)
async def score_resume(
    request: ScoreRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate ATS compatibility score for a resume against a job description."""
    try:
        # Convert Pydantic models to dicts for the service
        sections = [s.model_dump() for s in request.resume_content]
        result = await calculate_ats_score(sections, request.job_description)
        
        # Map service result to response schema
        breakdown = ScoreBreakdown(
            keyword_score=result.get("breakdown", {}).get("keyword_score", 0),
            semantic_score=result.get("breakdown", {}).get("semantic_score", 0),
            format_score=result.get("breakdown", {}).get("format_score", 0),
            completeness_score=result.get("breakdown", {}).get("completeness_score", 0),
        )
        
        def to_skill_matches(items: list, match_type: str) -> list:
            return [SkillMatch(skill=s.get("skill", s) if isinstance(s, dict) else str(s), match_type=match_type, confidence=s.get("confidence", 1.0) if isinstance(s, dict) else 1.0) for s in items]
        
        return ScoreResponse(
            ats_score=result.get("ats_score", 0),
            breakdown=breakdown,
            matched_skills=to_skill_matches(result.get("matched_skills", []), "exact"),
            partial_matches=to_skill_matches(result.get("partial_matches", []), "semantic"),
            missing_skills=to_skill_matches(result.get("missing_skills", []), "missing"),
            recommendations=result.get("recommendations", []),
        )
    except Exception as e:
        logger.error(f"Failed to score resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate ATS score: {str(e)}")
