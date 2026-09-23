"""TailorResume - Resume Schemas"""

from pydantic import BaseModel
from typing import List, Optional, Literal, Any, Dict
from datetime import datetime


class ExperienceEntry(BaseModel):
    company: str
    location: Optional[str] = None
    title: str
    duration: str
    bullets: List[str]


class ProjectEntry(BaseModel):
    name: str
    techStack: Optional[List[str]] = None
    duration: Optional[str] = None
    bullets: List[str]


class EducationEntry(BaseModel):
    institution: str
    location: Optional[str] = None
    degree: str
    year: str


class ResumeSection(BaseModel):
    name: str
    type: Literal["header", "summary", "experience", "education", "projects", "skills", "list", "custom"]
    
    # Header specific
    fullName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    headline: Optional[str] = None
    
    # Summary/custom specific
    text: Optional[str] = None
    
    # Skills specific
    categories: Optional[Dict[str, str]] = None
    items: Optional[List[str]] = None
    
    # Entries specific
    entries: Optional[List[Any]] = None


class ResumeCreate(BaseModel):
    title: str
    content: List[ResumeSection]
    template_id: Optional[str] = None


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[List[ResumeSection]] = None
    template_id: Optional[str] = None


class ResumeResponse(BaseModel):
    id: int
    title: str
    content: List[ResumeSection]
    template_id: Optional[str]
    is_base: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    id: int
    title: str
    is_base: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
