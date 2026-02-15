"""
Authentication Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data schema."""
    email: str | None = None


class VerifyEmailRequest(BaseModel):
    """Email verification request schema."""
    token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str
