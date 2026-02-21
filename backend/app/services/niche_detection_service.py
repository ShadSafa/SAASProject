"""Niche detection service using OpenAI structured output for Instagram content."""

from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


# Common Instagram niches
NICHE_OPTIONS = [
    "Fitness & Wellness",
    "Beauty & Cosmetics",
    "Fashion & Styling",
    "Food & Cooking",
    "Travel & Adventure",
    "Technology & Gadgets",
    "Business & Entrepreneurship",
    "Personal Development",
    "Gaming & Esports",
    "Music & Entertainment",
    "Art & Design",
    "Photography",
    "Education & Learning",
    "Parenting & Family",
    "Home & Decor",
    "Automotive",
    "Sports & Fitness",
    "DIY & Crafts",
    "Pets & Animals",
    "Finance & Investing",
    "Comedy & Humor",
    "Motivational & Inspiration",
    "Lifestyle",
    "Sports",
    "Mental Health",
    "Sustainability",
    "Dating & Relationships",
    "Real Estate",
    "Healthcare",
    "Other"
]


class NicheDetectionResult(BaseModel):
    """AI-detected niche for Instagram post/creator"""
    primary_niche: str = Field(
        ...,
        description="Primary niche from NICHE_OPTIONS. Must be one of the defined options."
    )
    secondary_niche: str | None = Field(
        None,
        description="Secondary niche if applicable, or None"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score 0.0-1.0 for niche detection"
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation of why this niche was detected"
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Key indicators that led to niche detection"
    )
