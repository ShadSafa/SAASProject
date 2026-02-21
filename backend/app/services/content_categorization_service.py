"""Content categorization service for Instagram posts.

Provides:
- Instagram native type classification (Reel, Story, Post, Guide, Video, Carousel)
- Extended format categorization (Tutorial, Comedy, ASMR, Educational, etc.)
- Confidence scoring based on signal clarity
"""

from enum import Enum
from pydantic import BaseModel


class InstagramNativeType(str, Enum):
    """Instagram's native content types"""
    REEL = "Reel"
    STORY = "Story"
    POST = "Post"
    GUIDE = "Guide"
    VIDEO = "Video"
    CAROUSEL = "Carousel"


INSTAGRAM_NATIVE_TYPES = [t.value for t in InstagramNativeType]


class ExtendedFormat(str, Enum):
    """Extended content format categories beyond native Instagram types"""
    TUTORIAL = "Tutorial"
    COMEDY = "Comedy"
    ASMR = "ASMR"
    EDUCATIONAL = "Educational"
    INSPIRATIONAL = "Inspirational"
    ENTERTAINMENT = "Entertainment"
    LIFESTYLE = "Lifestyle"
    MUSIC = "Music"
    FITNESS = "Fitness"
    FOOD = "Food"
    TRAVEL = "Travel"
    FASHION = "Fashion"
    BEAUTY = "Beauty"
    TECH = "Tech"
    BUSINESS = "Business"
    ART = "Art"
    GAMING = "Gaming"
    SPORTS = "Sports"
    NEWS = "News"
    MOTIVATIONAL = "Motivational"
    VLOGS = "Vlogs"
    UNBOXING = "Unboxing"
    REACTION = "Reaction"


EXTENDED_FORMATS = [f.value for f in ExtendedFormat]


class ContentCategory(BaseModel):
    """Content categorization result"""
    instagram_native_type: str  # From INSTAGRAM_NATIVE_TYPES
    extended_formats: list[str] = []  # Multiple formats possible (Tutorial + Comedy, etc.)
    confidence: float  # 0.0-1.0 confidence in this categorization
    reason: str  # Explanation of categorization logic
