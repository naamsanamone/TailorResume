/**
 * TailorResume — API client for the FastAPI backend (port 8000)
 * No auth required for MVP.
 */

const API_BASE = 'http://localhost:8000/api';

interface ResumeSection {
  name: string;
  type: 'header' | 'summary' | 'experience' | 'education' | 'projects' | 'skills' | 'list' | 'custom';
  fullName?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  headline?: string;
  text?: string;
  categories?: Record<string, string>;
  items?: string[];
  entries?: any[];
}

interface ScoreBreakdown {
  keyword_score: number;
  semantic_score: number;
  format_score: number;
  completeness_score: number;
}

export interface TailorResponse {
  tailored_content: ResumeSection[];
  ats_score: number;
  score_breakdown: ScoreBreakdown;
  keywords_added: string[];
  changes_summary: string[];
}

export interface TailorSummaryResponse {
  tailored_summary: string;
  keywords_incorporated: string[];
  ats_score: number;
}

export interface TailorBulletsResponse {
  tailored_bullets: string[];
  keywords_incorporated: string[];
  ats_score: number;
}

export interface TailorSkillsResponse {
  tailored_skills: Record<string, any>;
  keywords_incorporated: string[];
}

export interface ScoreResponse {
  ats_score: number;
  breakdown: ScoreBreakdown;
  matched_skills: { skill: string; match_type: string; confidence: number }[];
  partial_matches: { skill: string; match_type: string; confidence: number }[];
  missing_skills: { skill: string; match_type: string; confidence: number }[];
  recommendations: string[];
}

async function apiCall<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

/** Full resume tailoring — rewrites summary, bullets, skills */
export async function tailorResume(
  sections: ResumeSection[],
  jobDescription: string
): Promise<TailorResponse> {
  return apiCall<TailorResponse>('/tailor/', {
    resume_content: sections,
    job_description: jobDescription,
  });
}

/** Tailor only the summary section */
export async function tailorSummary(
  sections: ResumeSection[],
  jobDescription: string
): Promise<TailorSummaryResponse> {
  return apiCall<TailorSummaryResponse>('/tailor/summary', {
    resume_content: sections,
    job_description: jobDescription,
  });
}

/** Tailor bullets for a specific experience entry */
export async function tailorBullets(
  sections: ResumeSection[],
  jobDescription: string,
  entryIndex: number
): Promise<TailorBulletsResponse> {
  return apiCall<TailorBulletsResponse>('/tailor/bullets', {
    resume_content: sections,
    job_description: jobDescription,
    entry_index: entryIndex,
  });
}

/** Reorder and expand skills to match JD */
export async function tailorSkills(
  sections: ResumeSection[],
  jobDescription: string
): Promise<TailorSkillsResponse> {
  return apiCall<TailorSkillsResponse>('/tailor/skills', {
    resume_content: sections,
    job_description: jobDescription,
  });
}

/** Score resume against JD without modifying */
export async function scoreResume(
  sections: ResumeSection[],
  jobDescription: string
): Promise<ScoreResponse> {
  return apiCall<ScoreResponse>('/score/', {
    resume_content: sections,
    job_description: jobDescription,
  });
}

/** Health check */
export async function healthCheck(): Promise<{ status: string; llm_provider: string; llm_model: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}
