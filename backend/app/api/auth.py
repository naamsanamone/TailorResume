"""TailorResume — Authentication API Routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.email)
    logger.info(f"User registered: {user.email}")
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, user.email)
    logger.info(f"User logged in: {user.email}")
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse.model_validate(current_user)
