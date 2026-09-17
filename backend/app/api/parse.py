from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List, Any

from app.auth import get_current_user
from app.models.user import User
from app.schemas.parse import ResumeSection, JobDescriptionRequest, JobDescriptionResponse

router = APIRouter(prefix="/parse", tags=["parse"])

@router.post("/resume", response_model=List[ResumeSection])
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Parse a resume file (PDF or DOCX) into structured JSON sections.
    """
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported"
        )
    
    # TODO: Integrate with parser service
    return [
        ResumeSection(type="header", content="John Doe\njohn@example.com"),
        ResumeSection(type="experience", content="Software Engineer at Acme Corp"),
        ResumeSection(type="education", content="B.S. Computer Science")
    ]

@router.post("/jd", response_model=JobDescriptionResponse)
async def parse_job_description(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Extract skills and requirements from a raw job description text.
    """
    # TODO: Integrate with JD extraction service
    return JobDescriptionResponse(
        jobTitle="Software Engineer",
        seniority="Mid-Level",
        domain="Backend",
        hardSkills=["Python", "FastAPI", "SQLAlchemy"],
        softSkills=["Communication", "Teamwork"],
        tools=["Git", "Docker"]
    )
