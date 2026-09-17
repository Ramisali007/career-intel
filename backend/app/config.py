"""
AI CV Analyzer - Centralized Configuration
All environment variables, scoring weights, AI provider config, and application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── Application ──
    APP_NAME: str = "AI CV Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development | test | staging | production
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    SECRET_KEY: str = Field(
        default="change-this-in-production-use-a-strong-random-key",
        description="JWT secret key. MUST be changed in production.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    def validate_secret_key(self) -> str:
        """Warn if using default secret key."""
        import warnings
        if self.SECRET_KEY == "change-this-in-production-use-a-strong-random-key":
            if self.ENVIRONMENT not in ("development", "test"):
                raise ValueError(
                    "SECRET_KEY must be changed from default in production! "
                    "Set SECRET_KEY environment variable to a secure random string."
                )
            warnings.warn(
                "Using default SECRET_KEY — this is only acceptable in development.",
                stacklevel=2,
            )
        return self.SECRET_KEY

    # ── Database ──
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "cv_analyzer"

    # ── AI Providers ──
    # Google Gemini (Primary - FREE, High Quota & Fast)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.1

    # Groq (Fallback - FREE & Ultra Fast)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    GROQ_MAX_TOKENS: int = 950
    GROQ_TEMPERATURE: float = 0.1

    # AI Routing
    PRIMARY_AI_PROVIDER: str = "gemini"
    FALLBACK_AI_PROVIDER: str = "groq"

    AI_MAX_RETRIES: int = 3
    AI_TIMEOUT_SECONDS: int = 120

    # ── File Upload ──
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]
    ALLOWED_MIME_TYPES: list[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    UPLOAD_DIR: str = "uploads"

    # ── Scoring Weights (Configurable) ──
    # Job Match Score Dimensions
    WEIGHT_REQUIRED_SKILLS: float = 0.25
    WEIGHT_PREFERRED_SKILLS: float = 0.10
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_RESPONSIBILITIES: float = 0.15
    WEIGHT_SENIORITY: float = 0.08
    WEIGHT_EDUCATION: float = 0.07
    WEIGHT_CERTIFICATIONS: float = 0.05
    WEIGHT_DOMAIN_KNOWLEDGE: float = 0.05
    WEIGHT_KEYWORD_COVERAGE: float = 0.05

    # ATS Score Dimensions
    WEIGHT_ATS_PARSING: float = 0.25
    WEIGHT_ATS_STRUCTURE: float = 0.25
    WEIGHT_ATS_KEYWORDS: float = 0.20
    WEIGHT_ATS_FORMATTING: float = 0.15
    WEIGHT_ATS_READABILITY: float = 0.15

    # CV Quality Dimensions
    WEIGHT_QUALITY_CLARITY: float = 0.15
    WEIGHT_QUALITY_WRITING: float = 0.15
    WEIGHT_QUALITY_STRUCTURE: float = 0.15
    WEIGHT_QUALITY_CONCISENESS: float = 0.10
    WEIGHT_QUALITY_IMPACT: float = 0.15
    WEIGHT_QUALITY_RELEVANCE: float = 0.10
    WEIGHT_QUALITY_CONSISTENCY: float = 0.10
    WEIGHT_QUALITY_PROFESSIONALISM: float = 0.10

    # ── Processing ──
    MAX_CV_PAGES: int = 20
    MAX_JD_LENGTH: int = 15000
    MAX_RECOMMENDATIONS: int = 30
    VERIFICATION_MAX_RETRIES: int = 2

    # ── Logging ──
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
