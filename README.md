# TailorResume — AI-Powered ATS Resume Tailoring Engine

TailorResume is an AI-powered engine designed to optimize resumes for Applicant Tracking Systems (ATS). It features a Backend API and a Web Dashboard, along with integration for the LinkedApply Pro Chrome Extension.

## Features

- **ATS Scoring:** Analyze resumes for ATS compatibility.
- **Semantic Matching:** Match resumes with job descriptions semantically.
- **Multi-LLM Support:** Configurable to use various LLMs (OpenAI, Anthropic, Gemini, DeepSeek, Ollama).
- **PDF/DOCX Export:** Generate customized resumes in multiple formats.
- **User Accounts:** Manage user profiles, generated resumes, and preferences.

## Tech Stack

- **Backend:** FastAPI, Python, LiteLLM
- **Frontend:** Next.js, React
- **Database:** PostgreSQL (with pgvector for vector search)
- **Machine Learning / NLP:** sentence-transformers
- **Infrastructure:** Docker Compose

## Quick Start

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
3. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the API documentation at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint             | Description                           |
|--------|----------------------|---------------------------------------|
| GET    | `/`                  | Root endpoint                         |
| POST   | `/api/auth/login`    | User authentication                   |
| POST   | `/api/resume/parse`  | Parse a resume file                   |
| POST   | `/api/resume/tailor` | Tailor a resume to a job description  |

*(More endpoints will be documented as they are built.)*

## License

MIT
