from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InstagramAccountResponse(BaseModel):
    id: int
    instagram_user_id: str
    username: str
    profile_picture: Optional[str] = None
    account_type: Optional[str] = None
    follower_count: Optional[int] = None
    status: str  # "active", "expired", "revoked"
    created_at: datetime

    class Config:
        from_attributes = True


class InstagramAccountCreate(BaseModel):
    instagram_user_id: str
    username: str
    profile_picture: Optional[str] = None
    account_type: Optional[str] = None
    follower_count: Optional[int] = None
