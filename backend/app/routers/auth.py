"""
Auth Router - User registration and login.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from app.models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.audit_log import AuditLog
from app.security.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate):
    """Register a new user."""
    # Check if email already exists
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    await user.save()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="user_registered",
        entity_type="user",
        entity_id=str(user.id),
    ).save()

    token = create_access_token(str(user.id), user.email)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login with email and password."""
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user.last_login = datetime.utcnow()
    await user.save()

    # Audit log (§59)
    await AuditLog(
        user_id=str(user.id),
        action="user_logged_in",
        entity_type="user",
        entity_id=str(user.id),
    ).save()

    token = create_access_token(str(user.id), user.email)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
