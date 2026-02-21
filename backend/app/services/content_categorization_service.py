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


def categorize_content(
    post_type: str,
    caption: str | None,
    hashtags: str | None,
    creator_follower_count: int
) -> ContentCategory:
    """
    Categorize content by Instagram native type and extended formats.

    Args:
        post_type: From ViralPost.post_type (Reel, Story, Post, Video, Carousel, Photo)
        caption: From ViralPost.caption (text to analyze for format clues)
        hashtags: From ViralPost.hashtags (JSON array string to analyze)
        creator_follower_count: For confidence adjustment

    Returns:
        ContentCategory with native type, extended formats, and confidence
    """
    # 1. Normalize post_type to Instagram native type
    native_type = _normalize_instagram_type(post_type)

    # 2. Analyze caption and hashtags for extended formats
    extended_formats = _infer_extended_formats(caption, hashtags)

    # 3. Calculate confidence based on clarity of signals
    confidence = _calculate_categorization_confidence(
        caption, hashtags, len(extended_formats)
    )

    reason = f"Post is {native_type} with {', '.join(extended_formats) if extended_formats else 'no clear extended format'}"

    return ContentCategory(
        instagram_native_type=native_type,
        extended_formats=extended_formats,
        confidence=confidence,
        reason=reason
    )


def _normalize_instagram_type(post_type: str) -> str:
    """
    Map post_type to Instagram native type.

    Examples:
    - "Reel" -> InstagramNativeType.REEL
    - "Video" -> InstagramNativeType.VIDEO
    - "Photo" -> InstagramNativeType.POST
    - Unknown -> InstagramNativeType.POST (default)
    """
    post_type_lower = post_type.lower() if post_type else ""

    type_mapping = {
        "reel": InstagramNativeType.REEL,
        "story": InstagramNativeType.STORY,
        "post": InstagramNativeType.POST,
        "photo": InstagramNativeType.POST,
        "guide": InstagramNativeType.GUIDE,
        "video": InstagramNativeType.VIDEO,
        "carousel": InstagramNativeType.CAROUSEL,
    }

    return type_mapping.get(post_type_lower, InstagramNativeType.POST).value


def _infer_extended_formats(caption: str | None, hashtags: str | None) -> list[str]:
    """
    Infer extended content formats from caption text and hashtags.

    Rules:
    - Tutorial: Keywords: "how to", "tutorial", "step by step", "#howto"
    - Comedy: Keywords: "funny", "lol", "joke", "#comedy", "#funny"
    - ASMR: Keywords: "asmr", "relaxing", "satisfying", "#asmr"
    - Educational: Keywords: "learn", "education", "tip", "#education"
    - Fitness: Keywords: "workout", "fitness", "gym", "#fitness"
    - Etc.

    Returns: List of matched extended formats (can be multiple)
    """
    formats = set()
    text_to_search = (caption or "").lower() + " " + (hashtags or "").lower()

    # Tutorial keywords
    if any(kw in text_to_search for kw in ["how to", "tutorial", "step by step", "#howto", "#tutorial"]):
        formats.add(ExtendedFormat.TUTORIAL.value)

    # Comedy keywords
    if any(kw in text_to_search for kw in ["funny", "lol", "joke", "#comedy", "#funny", "#humor"]):
        formats.add(ExtendedFormat.COMEDY.value)

    # ASMR keywords
    if any(kw in text_to_search for kw in ["asmr", "satisfying", "#asmr"]):
        formats.add(ExtendedFormat.ASMR.value)

    # Educational keywords
    if any(kw in text_to_search for kw in ["learn", "education", "tip", "#education", "#learning"]):
        formats.add(ExtendedFormat.EDUCATIONAL.value)

    # Fitness keywords
    if any(kw in text_to_search for kw in ["workout", "fitness", "gym", "exercise", "#fitness", "#workout"]):
        formats.add(ExtendedFormat.FITNESS.value)

    # Food keywords
    if any(kw in text_to_search for kw in ["recipe", "food", "cooking", "#food", "#recipe", "#foodie"]):
        formats.add(ExtendedFormat.FOOD.value)

    # Travel keywords
    if any(kw in text_to_search for kw in ["travel", "trip", "destination", "#travel", "#adventure"]):
        formats.add(ExtendedFormat.TRAVEL.value)

    # Fashion keywords
    if any(kw in text_to_search for kw in ["fashion", "outfit", "style", "#fashion", "#ootd"]):
        formats.add(ExtendedFormat.FASHION.value)

    # Beauty keywords
    if any(kw in text_to_search for kw in ["beauty", "makeup", "skincare", "#beauty", "#makeup"]):
        formats.add(ExtendedFormat.BEAUTY.value)

    # Music keywords
    if any(kw in text_to_search for kw in ["music", "song", "singing", "#music", "#musician"]):
        formats.add(ExtendedFormat.MUSIC.value)

    # Tech keywords
    if any(kw in text_to_search for kw in ["tech", "technology", "gadget", "#tech", "#technology"]):
        formats.add(ExtendedFormat.TECH.value)

    # Business keywords
    if any(kw in text_to_search for kw in ["business", "entrepreneur", "startup", "#business", "#entrepreneur"]):
        formats.add(ExtendedFormat.BUSINESS.value)

    # Art keywords
    if any(kw in text_to_search for kw in ["art", "artist", "drawing", "painting", "#art", "#artist"]):
        formats.add(ExtendedFormat.ART.value)

    # Gaming keywords
    if any(kw in text_to_search for kw in ["gaming", "game", "gamer", "#gaming", "#gamer"]):
        formats.add(ExtendedFormat.GAMING.value)

    # Sports keywords
    if any(kw in text_to_search for kw in ["sport", "athlete", "training", "#sports", "#athlete"]):
        formats.add(ExtendedFormat.SPORTS.value)

    # Inspirational keywords
    if any(kw in text_to_search for kw in ["inspire", "inspiration", "motivated", "#inspiration", "#inspired"]):
        formats.add(ExtendedFormat.INSPIRATIONAL.value)

    # Motivational keywords
    if any(kw in text_to_search for kw in ["motivat", "success", "goals", "#motivation", "#motivational"]):
        formats.add(ExtendedFormat.MOTIVATIONAL.value)

    # Vlogs keywords
    if any(kw in text_to_search for kw in ["vlog", "day in", "daily", "#vlog", "#vlogger"]):
        formats.add(ExtendedFormat.VLOGS.value)

    # Unboxing keywords
    if any(kw in text_to_search for kw in ["unbox", "haul", "#unboxing", "#haul"]):
        formats.add(ExtendedFormat.UNBOXING.value)

    # Reaction keywords
    if any(kw in text_to_search for kw in ["reaction", "react", "reacting", "#reaction", "#react"]):
        formats.add(ExtendedFormat.REACTION.value)

    return sorted(list(formats))


def _calculate_categorization_confidence(caption: str | None, hashtags: str | None, format_count: int) -> float:
    """
    Calculate confidence in categorization based on signal clarity.

    Factors:
    - More clear keywords = higher confidence
    - Multiple matching formats = medium confidence (unclear which primary)
    - No keywords = low confidence (generic post)
    """
    text_length = len((caption or "") + (hashtags or ""))

    if format_count > 2:
        confidence = 0.5  # Multiple formats suggests unclear categorization
    elif format_count == 0:
        confidence = 0.3  # No keywords found, generic post
    elif text_length > 200:
        confidence = 0.85  # Rich description with keywords
    elif text_length > 50:
        confidence = 0.70  # Some description with keywords
    else:
        confidence = 0.50  # Minimal text

    return min(1.0, max(0.0, confidence))
