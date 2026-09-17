"""TailorResume - Score Schemas"""

from pydantic import BaseModel
from typing import List, Literal
from .resume import ResumeSection


class ScoreBreakdown(BaseModel):
    keyword_score: float
    semantic_score: float
    format_score: float
    completeness_score: float


class SkillMatch(BaseModel):
    skill: str
    match_type: Literal["exact", "semantic", "missing"]
    confidence: float


class ScoreRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str


class ScoreResponse(BaseModel):
    ats_score: float
    breakdown: ScoreBreakdown
    matched_skills: List[SkillMatch]
    partial_matches: List[SkillMatch]
    missing_skills: List[SkillMatch]
    recommendations: List[str]


class TailorRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str


class TailorResponse(BaseModel):
    tailored_content: List[ResumeSection]
    ats_score: float
    score_breakdown: ScoreBreakdown
    keywords_added: List[str]
    changes_summary: List[str]
