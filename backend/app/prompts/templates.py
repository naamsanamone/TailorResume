PARSE_RESUME_PROMPT = """
You are an expert resume parser. Given the raw text extracted from a resume document, convert it into a structured JSON format.
The output MUST strictly conform to the provided JSON schema.

Raw Resume Text:
{raw_text}

JSON Schema structure expected for 'sections':
[
  {{
    "name": "Header",
    "type": "header",
    "fullName": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "github": "string",
    "portfolio": "string"
  }},
  {{
    "name": "Summary",
    "type": "summary",
    "text": "string"
  }},
  {{
    "name": "Experience",
    "type": "experience",
    "entries": [
      {{
        "title": "string",
        "company": "string",
        "location": "string",
        "date": "string",
        "bullets": ["string"]
      }}
    ]
  }},
  {{
    "name": "Education",
    "type": "education",
    "entries": [
      {{
        "degree": "string",
        "institution": "string",
        "location": "string",
        "date": "string"
      }}
    ]
  }},
  {{
    "name": "Skills",
    "type": "skills",
    "categories": [
      {{
        "name": "string",
        "items": ["string"]
      }}
    ]
  }}
]

Respond ONLY with valid JSON. Example: {{"sections": [...]}}
"""

PARSE_JD_PROMPT = """
Analyze the following Job Description and extract structured information.

Job Description:
{jd_text}

Extract and return a JSON object with the following fields:
- jobTitle: string
- company: string (if available, else empty)
- seniority: string (e.g. Junior, Senior, Lead)
- experienceLevel: string (e.g. 3-5 years)
- domain: string (e.g. Fintech, Healthcare)
- hardSkills: array of strings
- softSkills: array of strings
- tools: array of strings
- responsibilities: array of strings
- requirements: array of strings

Respond ONLY with valid JSON.
"""

TAILOR_BULLETS_PROMPT = """
You are an expert resume writer. Rewrite the provided bullet points for a candidate to better match a target job.

Role: {job_title}
Original Bullets:
{bullets}

Missing JD Keywords to incorporate if possible (DO NOT fabricate experience): {missing_skills}
Target Job Responsibilities for context: {responsibilities}

Rules:
1. Use the XYZ formula (Accomplished [X] as measured by [Y], by doing [Z]).
2. Start with strong action verbs.
3. Quantify achievements where possible.
4. Incorporate the missing keywords naturally, ONLY if they fit the context of the original bullet.
5. DO NOT fabricate skills or achievements the candidate does not have.

Output JSON format:
{{
  "bullets": ["rewritten bullet 1", "rewritten bullet 2"],
  "keywords_incorporated": ["keyword1", "keyword2"]
}}
"""

TAILOR_SUMMARY_PROMPT = """
You are an expert resume writer. Rewrite the candidate's professional summary to align perfectly with the target role.

Original Summary: {original_summary}
Target Role: {job_title} at {company}

Key JD Skills (Hard): {hard_skills}
Key JD Skills (Soft): {soft_skills}
Missing Keywords to Target: {missing_skills}

Rules:
1. Keep it to 3-4 sentences.
2. Highlight relevant experience that matches the target role.
3. Incorporate missing keywords naturally without fabricating.
4. Keep the tone professional, impactful, and concise.

Output JSON format:
{{
  "summary": "The rewritten summary text...",
  "keywords_incorporated": ["keyword1", "keyword2"]
}}
"""
