"""TailorResume — Resume & JD Parsing API Routes"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
import logging

from app.auth import get_current_user
from app.models.user import User
from app.services.parser import parse_resume_file
from app.services.jd_analyzer import analyze_job_description
from app.schemas.resume import ResumeSection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/resume", response_model=List[dict])
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Parse a resume file (PDF or DOCX) into structured JSON sections."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = file.filename.lower().split('.')[-1]
    if ext not in ('pdf', 'docx'):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    try:
        file_bytes = await file.read()
        sections = await parse_resume_file(file.filename, file_bytes)
        logger.info(f"Parsed resume '{file.filename}' into {len(sections)} sections for user {current_user.id}")
        return sections
    except Exception as e:
        logger.error(f"Failed to parse resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/jd")
async def parse_job_description(
    body: dict,
    current_user: User = Depends(get_current_user),
):
    """Extract skills and requirements from a raw job description."""
    jd_text = body.get("text", "")
    if not jd_text or len(jd_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description text is too short (min 50 chars)")
    
    try:
        result = await analyze_job_description(jd_text)
        logger.info(f"Analyzed JD for user {current_user.id}: {result.get('jobTitle', 'Unknown')}")
        return result
    except Exception as e:
        logger.error(f"Failed to analyze JD: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze job description: {str(e)}")
