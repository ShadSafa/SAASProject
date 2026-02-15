"""Authentication API routes for signup, login, and email verification."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import VerifyEmailRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import get_user_by_email, create_user, verify_user_email
from app.services.auth import generate_verification_token, verify_verification_token
from app.services.email import send_verification_email
from app.services.security import (
    validate_password_strength,
    verify_password,
    create_access_token,
    verify_token
)
from app.models.user import User
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user and send verification email.

    Requirements covered:
    - AUTH-01: Email/password signup
    - AUTH-02: Email verification sending
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Create user (password hashed automatically in CRUD)
    new_user = await create_user(db, user_data)

    # Generate verification token and send email
    verification_token = generate_verification_token(new_user.email)
    email_result = send_verification_email(new_user.email, verification_token)

    if email_result.get("status") != "sent":
        # Log error but don't fail signup (user can request resend)
        print(f"Warning: Failed to send verification email to {new_user.email}")

    return {
        "message": "Signup successful. Please check your email to verify your account.",
        "email": new_user.email
    }


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user's email address using token from email link.

    Requirements covered:
    - AUTH-03: Email verification requirement
    """
    # Verify token and extract email
    email = verify_verification_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Mark email as verified
    user = await verify_user_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "Email verified successfully. You can now log in.",
        "email": user.email
    }


@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email if user didn't receive it."""
    user = await get_user_by_email(db, email)

    # Don't reveal if email exists (security)
    if not user:
        return {"message": "If that email exists, a verification link has been sent."}

    # Don't resend if already verified
    if user.email_verified:
        return {"message": "Email already verified."}

    # Generate new token and send
    verification_token = generate_verification_token(user.email)
    send_verification_email(user.email, verification_token)

    return {"message": "Verification email sent."}


@router.post("/login", response_model=Token)
async def login(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token in httpOnly cookie.

    Requirements covered:
    - AUTH-04: Login flow
    - AUTH-05: Session persistence (via httpOnly cookie)
    """
    # Get user by email
    user = await get_user_by_email(db, user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify email before allowing login (AUTH-03)
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )

    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token (1 hour expiration)
    access_token_expires = timedelta(hours=1)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )

    # Return token in httpOnly cookie
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "email_verified": user.email_verified
            }
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600,  # 1 hour in seconds
        httponly=True,  # JavaScript cannot access (XSS protection)
        secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
        samesite="strict",  # CSRF protection
    )

    return response


@router.post("/logout")
async def logout():
    """
    Log out user by clearing session cookie.

    Requirements covered:
    - AUTH-06: Logout
    """
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token")
    return response


async def get_current_active_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency for protected routes - validates JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get currently authenticated user's profile."""
    return current_user
