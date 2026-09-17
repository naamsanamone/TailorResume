from fastapi import APIRouter, Depends
from typing import Any

from app.auth import get_current_user
from app.models.user import User
from app.schemas.tailor import TailorRequest, TailorResponse

router = APIRouter(prefix="/tailor", tags=["tailor"])

@router.post("/", response_model=TailorResponse)
async def tailor_resume(
    request: TailorRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Tailor a resume based on a job description.
    """
    # TODO: Integrate with tailoring pipeline service
    return TailorResponse(
        tailored_content=request.resume_content,
        score=85,
        changes_made=["Added Python to skills", "Highlighted backend experience"]
    )
