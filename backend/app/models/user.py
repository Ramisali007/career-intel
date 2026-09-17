"""
User Model - Authentication and user management.
"""

from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class User(Document):
    """User account for authentication and authorization."""

    email: EmailStr
    hashed_password: str
    full_name: str = ""
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # OAuth
    oauth_provider: Optional[str] = None  # google, github
    oauth_id: Optional[str] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
        ]


class UserResponse(BaseModel):
    """Public user response (no password)."""

    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    """User registration input."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)


class UserLogin(BaseModel):
    """User login input."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
