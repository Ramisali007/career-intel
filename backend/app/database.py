"""
AI CV Analyzer - MongoDB Database Connection
Uses Motor async driver with Beanie ODM for document models.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM."""
    global _client

    from app.models.user import User
    from app.models.document import Document
    from app.models.job_description import JobDescription
    from app.models.analysis import Analysis
    from app.models.recommendation import Recommendation
    from app.models.cv_version import CVVersion
    from app.models.career_profile import CareerProfile
    from app.models.audit_log import AuditLog

    try:
        import certifi
    except ImportError:
        certifi = None

    client_kwargs = {}
    if "mongodb+srv://" in settings.MONGODB_URL or "tls=true" in settings.MONGODB_URL.lower():
        if certifi:
            client_kwargs["tlsCAFile"] = certifi.where()
        else:
            logger.warning("certifi not installed. TLS certificate verification may fail for MongoDB Atlas.")

    _client = AsyncIOMotorClient(settings.MONGODB_URL, **client_kwargs)
    db = _client[settings.MONGODB_DB_NAME]

    await init_beanie(
        database=db,
        allow_index_dropping=True,
        document_models=[
            User,
            Document,
            JobDescription,
            Analysis,
            Recommendation,
            CVVersion,
            CareerProfile,
            AuditLog,
        ],
    )
    logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_db():
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get the database instance."""
    if _client is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _client[settings.MONGODB_DB_NAME]
