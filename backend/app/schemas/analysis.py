from pydantic import BaseModel, Field
from typing import Optional


class AnalysisResponse(BaseModel):
    """Analysis data for a viral post."""
    id: int
    viral_post_id: int
    why_viral_summary: Optional[str] = None
    posting_time_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    hook_strength_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    emotional_trigger: Optional[str] = None
    engagement_velocity_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    save_share_ratio_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    hashtag_performance_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    audience_retention_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_at: str

    class Config:
        from_attributes = True
