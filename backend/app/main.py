"""TailorResume — FastAPI Application Entry Point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import create_tables
from app.api import auth, resumes, parse, tailor, score, export, analyze

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting TailorResume API...")
    await create_tables()
    
    # Pre-load embedding model (lazy — loaded on first use)
    logger.info(f"Embedding model: {settings.EMBEDDING_MODEL}")
    logger.info(f"LLM provider: {settings.LLM_PROVIDER} ({settings.LLM_MODEL})")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TailorResume API...")


app = FastAPI(
    title="TailorResume API",
    description="AI-Powered ATS Resume Tailoring Engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(parse.router, prefix="/api/parse", tags=["Parsing"])
app.include_router(tailor.router, prefix="/api/tailor", tags=["Tailoring"])
app.include_router(score.router, prefix="/api/score", tags=["Scoring"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TailorResume API",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
    }


@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
