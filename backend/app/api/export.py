"""TailorResume — PDF & DOCX Export API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from typing import List
import logging

from app.auth import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeSection
from app.services.pdf_export import generate_pdf, render_html
from app.services.docx_export import generate_docx

logger = logging.getLogger(__name__)

router = APIRouter()


class ExportRequest:
    """Request body for export endpoints."""
    pass


from pydantic import BaseModel

class ExportRequestBody(BaseModel):
    sections: List[ResumeSection]
    template: str = "jake_classic"


@router.post("/pdf")
async def export_pdf(
    body: ExportRequestBody,
    current_user: User = Depends(get_current_user),
):
    """Generate an ATS-friendly PDF from resume sections."""
    try:
        sections = [s.model_dump() for s in body.sections]
        pdf_bytes = await generate_pdf(sections, body.template)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.pdf"},
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/docx")
async def export_docx(
    body: ExportRequestBody,
    current_user: User = Depends(get_current_user),
):
    """Generate an ATS-friendly DOCX from resume sections."""
    try:
        sections = [s.model_dump() for s in body.sections]
        docx_bytes = await generate_docx(sections)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.docx"},
        )
    except Exception as e:
        logger.error(f"DOCX generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")


@router.post("/html")
async def export_html(
    body: ExportRequestBody,
    current_user: User = Depends(get_current_user),
):
    """Generate an ATS-friendly standalone HTML file from resume sections (Jake's Resume style)."""
    try:
        sections = [s.model_dump() for s in body.sections]
        html_content = render_html(sections, body.template)
        return Response(
            content=html_content,
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.html"},
        )
    except Exception as e:
        logger.error(f"HTML generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML: {str(e)}")
