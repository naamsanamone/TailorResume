"""TailorResume — Resume Tailoring API Routes (Auth-free MVP)"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import copy
import json
import logging

from app.schemas.score import TailorRequest, TailorResponse, ScoreBreakdown
from app.schemas.resume import ResumeSection
from app.services.tailor_engine import tailor_resume, _expand_acronyms_in_skills
from app.services.jd_analyzer import analyze_job_description
from app.services.matcher import match_resume_to_jd
from app.services.scorer import calculate_ats_score
from app.services.llm_client import get_llm_client
from app.prompts.templates import TAILOR_BULLETS_PROMPT, TAILOR_SUMMARY_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------- Full Tailor (existing) ----------

@router.post("/", response_model=TailorResponse)
async def tailor_resume_endpoint(request: TailorRequest):
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


# ---------- Per-Section Endpoints ----------

class TailorSummaryRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str = Field(min_length=50)

class TailorSummaryResponse(BaseModel):
    tailored_summary: str
    keywords_incorporated: List[str] = []
    before_score: float = 0
    ats_score: float = 0

class TailorBulletsRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str = Field(min_length=50)
    entry_index: int = 0  # which experience entry to tailor

class TailorBulletsResponse(BaseModel):
    tailored_bullets: List[str] = []
    keywords_incorporated: List[str] = []
    before_score: float = 0
    ats_score: float = 0

class TailorSkillsRequest(BaseModel):
    resume_content: List[ResumeSection]
    job_description: str = Field(min_length=50)

class TailorSkillsResponse(BaseModel):
    tailored_skills: Dict[str, Any] = {}
    keywords_incorporated: List[str] = []


@router.post("/summary", response_model=TailorSummaryResponse)
async def tailor_summary_endpoint(request: TailorSummaryRequest):
    """Tailor only the professional summary section."""
    try:
        sections = [s.model_dump() for s in request.resume_content]
        jd_analysis = await analyze_job_description(request.job_description)

        # Before score
        before_score_data = await calculate_ats_score(sections, request.job_description, jd_analysis)
        before_score = before_score_data.get("ats_score", 0)

        match_results = await match_resume_to_jd(sections, jd_analysis)
        missing_skills = [s for s in match_results.get("missing_skills", []) if isinstance(s, str)]

        # Find summary section
        orig_summary = ""
        for sec in sections:
            if sec.get("type", "").lower() == "summary":
                orig_summary = sec.get("text", "") or ""
                break

        client = get_llm_client(for_content=True)
        prompt = TAILOR_SUMMARY_PROMPT.format(
            original_summary=orig_summary,
            job_title=jd_analysis.get("jobTitle") or "Software Engineer",
            company=jd_analysis.get("company") or "the company",
            hard_skills=", ".join([s for s in (jd_analysis.get("hardSkills") or []) if isinstance(s, str)]),
            soft_skills=", ".join([s for s in (jd_analysis.get("softSkills") or []) if isinstance(s, str)]),
            missing_skills=", ".join(missing_skills[:5])
        )

        result = await client.complete_json(
            prompt,
            "You are an expert resume writer. Do not fabricate experience."
        )

        tailored = result.get("summary", orig_summary) if isinstance(result, dict) else orig_summary
        kw = result.get("keywords_incorporated", []) if isinstance(result, dict) else []

        # Calculate score with updated summary
        updated_sections = copy.deepcopy(sections)
        for sec in updated_sections:
            if sec.get("type", "").lower() == "summary":
                sec["text"] = tailored
                break
        score_data = await calculate_ats_score(updated_sections, request.job_description, jd_analysis)

        return TailorSummaryResponse(
            tailored_summary=tailored,
            keywords_incorporated=[str(k) for k in kw] if isinstance(kw, list) else [],
            before_score=before_score,
            ats_score=score_data.get("ats_score", 0),
        )
    except Exception as e:
        logger.error(f"Failed to tailor summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor summary: {str(e)}")


@router.post("/bullets", response_model=TailorBulletsResponse)
async def tailor_bullets_endpoint(request: TailorBulletsRequest):
    """Tailor bullet points for a specific experience entry."""
    try:
        sections = [s.model_dump() for s in request.resume_content]
        jd_analysis = await analyze_job_description(request.job_description)
        # Before score
        before_score_data = await calculate_ats_score(sections, request.job_description, jd_analysis)
        before_score = before_score_data.get("ats_score", 0)

        match_results = await match_resume_to_jd(sections, jd_analysis)
        missing_skills = [s for s in match_results.get("missing_skills", []) if isinstance(s, str)]

        # Find experience section and specific entry
        exp_section = None
        for sec in sections:
            if sec.get("type", "").lower() == "experience":
                exp_section = sec
                break

        if not exp_section:
            raise HTTPException(status_code=400, detail="No experience section found")

        entries = exp_section.get("entries") or []
        if request.entry_index >= len(entries):
            raise HTTPException(status_code=400, detail=f"Entry index {request.entry_index} out of range (max {len(entries)-1})")

        entry = entries[request.entry_index]
        original_bullets = entry.get("bullets") or []

        client = get_llm_client(for_content=True)
        prompt = TAILOR_BULLETS_PROMPT.format(
            job_title=entry.get("title", "") or "Software Engineer",
            bullets=json.dumps(original_bullets, indent=2),
            missing_skills=", ".join(missing_skills),
            responsibilities=json.dumps(jd_analysis.get("responsibilities") or [], indent=2)
        )

        result = await client.complete_json(
            prompt,
            "You are an expert resume writer. Apply the XYZ formula. Do not fabricate."
        )

        tailored = result.get("bullets", original_bullets) if isinstance(result, dict) else original_bullets
        kw = result.get("keywords_incorporated", []) if isinstance(result, dict) else []

        # Calculate score with updated bullets
        updated_sections = copy.deepcopy(sections)
        for sec in updated_sections:
            if sec.get("type", "").lower() == "experience":
                ents = sec.get("entries") or []
                if request.entry_index < len(ents):
                    ents[request.entry_index]["bullets"] = tailored
                break
        score_data = await calculate_ats_score(updated_sections, request.job_description, jd_analysis)

        return TailorBulletsResponse(
            tailored_bullets=tailored if isinstance(tailored, list) else original_bullets,
            keywords_incorporated=[str(k) for k in kw] if isinstance(kw, list) else [],
            before_score=before_score,
            ats_score=score_data.get("ats_score", 0),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to tailor bullets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor bullets: {str(e)}")


@router.post("/skills", response_model=TailorSkillsResponse)
async def tailor_skills_endpoint(request: TailorSkillsRequest):
    """Reorder and expand skills to match JD (no LLM call needed)."""
    try:
        sections = [s.model_dump() for s in request.resume_content]
        jd_analysis = await analyze_job_description(request.job_description)

        all_jd_skills = []
        for key in ("hardSkills", "softSkills", "tools"):
            val = jd_analysis.get(key) or []
            if isinstance(val, list):
                all_jd_skills.extend([s for s in val if isinstance(s, str)])
        all_jd_lower = set(s.lower() for s in all_jd_skills)

        keywords_added = []
        tailored_skills: Dict[str, Any] = {}

        for sec in sections:
            if sec.get("type", "").lower() != "skills":
                continue

            skill_sec = copy.deepcopy(sec)
            expanded = _expand_acronyms_in_skills(skill_sec)
            keywords_added.extend(expanded)

            cats = skill_sec.get("categories")
            if isinstance(cats, dict):
                for cat_name, cat_val in cats.items():
                    if isinstance(cat_val, str):
                        skills = [s.strip() for s in cat_val.split(",") if s.strip()]
                        skills.sort(key=lambda x: 0 if x.lower() in all_jd_lower else 1)
                        cats[cat_name] = ", ".join(skills)
                tailored_skills = cats

            items = skill_sec.get("items")
            if isinstance(items, list):
                items.sort(key=lambda x: 0 if str(x).lower() in all_jd_lower else 1)
                tailored_skills["items"] = items
            break

        return TailorSkillsResponse(
            tailored_skills=tailored_skills,
            keywords_incorporated=list(dict.fromkeys(keywords_added)),
        )
    except Exception as e:
        logger.error(f"Failed to tailor skills: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor skills: {str(e)}")
