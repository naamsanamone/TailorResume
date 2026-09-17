from fastapi import APIRouter, Depends
from typing import Any

from app.auth import get_current_user
from app.models.user import User
from app.schemas.score import ScoreRequest, ScoreResponse

router = APIRouter(prefix="/score", tags=["score"])

@router.post("/", response_model=ScoreResponse)
async def score_resume(
    request: ScoreRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Calculate ATS score for a resume against a job description.
    """
    # TODO: Integrate with scoring service
    return ScoreResponse(
        score=75,
        breakdown={
            "keyword_match": 80,
            "format_score": 90,
            "impact_score": 60
        },
        missing_skills=["Docker", "Kubernetes"]
    )
