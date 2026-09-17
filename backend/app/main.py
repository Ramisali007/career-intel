"""
AI CV Analyzer - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.database import init_db, close_db

import json

# Structured JSON Logging (§68)
class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production observability (§68)."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_payload["request_id"] = record.request_id
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)


if settings.ENVIRONMENT in ("production", "staging"):
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
else:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to every request for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle - startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    yield
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered CV analysis, job matching, ATS optimization & intelligent CV tailoring platform",
    lifespan=lifespan,
)

# ── Middleware ──
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (§74)
from app.security.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# ── Routers ──
from app.routers import auth, documents, job_descriptions, analyses, recommendations, cv_versions, exports, profile

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{settings.API_PREFIX}/documents", tags=["Documents"])
app.include_router(job_descriptions.router, prefix=f"{settings.API_PREFIX}/job-descriptions", tags=["Job Descriptions"])
app.include_router(analyses.router, prefix=f"{settings.API_PREFIX}/analyses", tags=["Analyses"])
app.include_router(recommendations.router, prefix=f"{settings.API_PREFIX}/recommendations", tags=["Recommendations"])
app.include_router(cv_versions.router, prefix=f"{settings.API_PREFIX}/cv-versions", tags=["CV Versions"])
app.include_router(exports.router, prefix=f"{settings.API_PREFIX}/exports", tags=["Exports"])
app.include_router(profile.router, prefix=f"{settings.API_PREFIX}/profile", tags=["Career Profile"])


@app.get("/")
async def root():
    """Root status endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
