import logging
from typing import Dict, Any
from app.services.llm_client import get_llm_client
from app.prompts.templates import PARSE_JD_PROMPT

logger = logging.getLogger(__name__)

async def analyze_job_description(jd_text: str) -> Dict[str, Any]:
    """Use LLM to extract structured data from Job Description text."""
    client = get_llm_client(for_content=False)
    system_message = "You are an expert recruiter and job description analyzer. Extract key requirements accurately."
    prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)
    
    try:
        result = await client.complete_json(
            prompt=prompt,
            system_message=system_message,
            temperature=0.1
        )
        
        expected_keys = [
            "hardSkills", "softSkills", "tools", "domain", 
            "seniority", "jobTitle", "company", "experienceLevel", 
            "responsibilities", "requirements"
        ]
        for key in expected_keys:
            if key not in result:
                if key in ["hardSkills", "softSkills", "tools", "responsibilities", "requirements"]:
                    result[key] = []
                else:
                    result[key] = ""
                    
        return result
    except Exception as e:
        logger.error(f"Error analyzing job description: {str(e)}")
        raise ValueError("Failed to analyze job description.")
