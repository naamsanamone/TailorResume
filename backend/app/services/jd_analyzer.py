import re
import logging
from typing import Dict, Any, List
from app.prompts.templates import PARSE_JD_PROMPT

logger = logging.getLogger(__name__)

# Common tech skills to look for in JDs
TECH_KEYWORDS = {
    "languages": ["python", "java", "javascript", "typescript", "go", "golang", "rust", "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css"],
    "frameworks": ["react", "angular", "vue", "next.js", "nextjs", "django", "flask", "fastapi", "spring", "springboot", "spring boot", "express", "node.js", "nodejs", ".net", "rails", "laravel"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "cloudflare", "digitalocean"],
    "databases": ["postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra", "sqlite", "oracle", "sql server"],
    "devops": ["docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd", "github actions", "gitlab ci", "circleci", "helm", "argocd"],
    "tools": ["git", "github", "gitlab", "jira", "confluence", "figma", "postman", "swagger", "grafana", "prometheus", "datadog", "splunk", "kafka", "rabbitmq", "celery"],
    "concepts": ["microservices", "rest", "restful", "graphql", "grpc", "oauth", "jwt", "websocket", "serverless", "machine learning", "deep learning", "nlp", "computer vision", "agile", "scrum", "tdd", "bdd", "api", "sdk"],
}

SOFT_SKILL_KEYWORDS = [
    "communication", "leadership", "teamwork", "collaboration", "problem-solving",
    "problem solving", "analytical", "critical thinking", "time management",
    "project management", "mentoring", "self-motivated", "detail-oriented",
    "adaptable", "creative", "innovative", "strategic", "customer-focused",
]


def rule_based_jd_analysis(jd_text: str) -> Dict[str, Any]:
    """Extract structured JD data using regex/keyword matching (no LLM)."""
    text_lower = jd_text.lower()

    # Extract hard skills
    hard_skills: List[str] = []
    for category, keywords in TECH_KEYWORDS.items():
        for kw in keywords:
            # Word boundary match
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                hard_skills.append(kw.title() if len(kw) > 3 else kw.upper())

    # Extract soft skills
    soft_skills: List[str] = []
    for skill in SOFT_SKILL_KEYWORDS:
        if skill in text_lower:
            soft_skills.append(skill.title())

    # Extract tools (same as hard skills for now, deduplicated)
    tools = [s for s in hard_skills if s.lower() in sum([TECH_KEYWORDS["tools"], TECH_KEYWORDS["devops"], TECH_KEYWORDS["cloud"]], [])]

    # Try to extract job title
    job_title = ""
    title_patterns = [
        r"(?:job\s+title|position|role)\s*[:\-]\s*(.+?)(?:\n|$)",
        r"^(.+?(?:engineer|developer|architect|analyst|scientist|manager|designer|lead|specialist|consultant))",
    ]
    for pattern in title_patterns:
        match = re.search(pattern, jd_text, re.I | re.M)
        if match:
            job_title = match.group(1).strip()
            break

    # Try to extract company
    company = ""
    company_patterns = [
        r"(?:company|about)\s*[:\-]\s*(.+?)(?:\n|$)",
        r"(?:at|join)\s+([A-Z][A-Za-z\s]+(?:Inc|Corp|Ltd|LLC|Technologies|Tech|Labs|Software|Solutions|Group))",
    ]
    for pattern in company_patterns:
        match = re.search(pattern, jd_text, re.I)
        if match:
            company = match.group(1).strip()
            break

    # Seniority
    seniority = "mid"
    if re.search(r'\b(senior|sr\.?|staff|principal|lead)\b', text_lower):
        seniority = "senior"
    elif re.search(r'\b(junior|jr\.?|entry[\s-]level|intern|graduate)\b', text_lower):
        seniority = "junior"

    # Experience level
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', text_lower)
    experience_level = f"{exp_match.group(1)}+ years" if exp_match else ""

    # Extract requirements (lines with bullet points or "required"/"must")
    requirements: List[str] = []
    responsibilities: List[str] = []
    in_requirements = False
    in_responsibilities = False

    for line in jd_text.split("\n"):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if re.match(r'(?:requirements?|qualifications?|must\s+have|what\s+you.*need)', line_lower):
            in_requirements = True
            in_responsibilities = False
            continue
        elif re.match(r'(?:responsibilities|what\s+you.*do|duties|role\s+description)', line_lower):
            in_responsibilities = True
            in_requirements = False
            continue
        elif re.match(r'^[A-Z].*:$', line_stripped) and len(line_stripped) < 40:
            in_requirements = False
            in_responsibilities = False

        bullet = re.sub(r'^[•\-–·*▪►○]\s*', '', line_stripped)
        if bullet and bullet != line_stripped:
            if in_requirements:
                requirements.append(bullet)
            elif in_responsibilities:
                responsibilities.append(bullet)

    # Extract domain
    domain = ""
    domain_keywords = {
        "fintech": ["fintech", "financial", "banking", "payment"],
        "healthcare": ["healthcare", "medical", "health tech", "biotech"],
        "e-commerce": ["e-commerce", "ecommerce", "retail", "marketplace"],
        "enterprise": ["enterprise", "saas", "b2b"],
        "ai/ml": ["machine learning", "deep learning", "artificial intelligence", "ai/ml", "data science"],
    }
    for d, keywords in domain_keywords.items():
        if any(kw in text_lower for kw in keywords):
            domain = d
            break

    return {
        "hardSkills": hard_skills,
        "softSkills": soft_skills,
        "tools": tools,
        "domain": domain,
        "seniority": seniority,
        "jobTitle": job_title,
        "company": company,
        "experienceLevel": experience_level,
        "responsibilities": responsibilities[:10],
        "requirements": requirements[:10],
    }


async def analyze_job_description(jd_text: str) -> Dict[str, Any]:
    """Analyze JD using LLM with rule-based fallback."""
    # Try LLM first
    try:
        from app.services.llm_client import get_llm_client
        client = get_llm_client(for_content=False)
        system_message = "You are an expert recruiter and job description analyzer. Extract key requirements accurately."
        prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)

        result = await client.complete_json(
            prompt=prompt,
            system_message=system_message,
            temperature=0.1,
        )

        expected_keys = [
            "hardSkills", "softSkills", "tools", "domain",
            "seniority", "jobTitle", "company", "experienceLevel",
            "responsibilities", "requirements",
        ]
        for key in expected_keys:
            if key not in result:
                result[key] = [] if key in ("hardSkills", "softSkills", "tools", "responsibilities", "requirements") else ""

        return result
    except Exception as e:
        logger.warning(f"LLM JD analysis failed, using rule-based fallback: {e}")
        return rule_based_jd_analysis(jd_text)
