"""
User Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation (signup)."""
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates (all fields optional)."""
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(UserBase):
    """Schema for user response (public data only)."""
    id: int
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class ProfileUpdateRequest(BaseModel):
    """Schema for profile update requests (email or password change)."""
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None


class ProfileResponse(BaseModel):
    """Schema for profile response (authenticated user data)."""
    id: int
    email: str
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
