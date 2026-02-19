from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Request body for triggering a time-range viral content scan."""
    time_range: str = Field(
        ...,
        pattern=r"^(12h|24h|48h|7d)$",
        description="Time range for viral post discovery: 12h, 24h, 48h, or 7d",
    )


class AnalyzeUrlRequest(BaseModel):
    """Request body for analyzing a specific Instagram post URL."""
    instagram_url: str = Field(
        ...,
        description="Full Instagram post URL (e.g. https://www.instagram.com/p/SHORTCODE/)",
    )


class EngagementResponse(BaseModel):
    likes: int
    comments: int
    saves: int
    shares: int


class ViralPostResponse(BaseModel):
    id: int
    instagram_post_id: str
    instagram_url: Optional[str]
    post_type: Optional[str]
    thumbnail_url: Optional[str]     # S3 URL if cached; falls back to Instagram URL
    creator_username: Optional[str]
    creator_follower_count: Optional[int]
    engagement: EngagementResponse
    viral_score: Optional[float]
    post_age_hours: Optional[float]

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    scan_id: int
    status: str  # pending, running, completed, failed
    scan_type: str
    time_range: Optional[str]
    target_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    results: List[ViralPostResponse] = []

    class Config:
        from_attributes = True


class ScanTriggerResponse(BaseModel):
    scan_id: int
    status: str
    message: str


class ScanHistoryItem(BaseModel):
    scan_id: int
    status: str
    scan_type: str
    time_range: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    post_count: int

    class Config:
        from_attributes = True
