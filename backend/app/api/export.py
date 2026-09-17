from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import Any
import io

from app.auth import get_current_user
from app.models.user import User
from app.schemas.export import ExportRequest

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/pdf")
async def export_pdf(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Export a resume as a PDF file.
    """
    # TODO: Integrate with PDF generation service
    # Stub response
    file_content = b"PDF placeholder content"
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"}
    )

@router.post("/docx")
async def export_docx(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Export a resume as a DOCX file.
    """
    # TODO: Integrate with DOCX generation service
    # Stub response
    file_content = b"DOCX placeholder content"
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=resume.docx"}
    )
