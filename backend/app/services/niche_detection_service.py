"""Niche detection service using OpenAI structured output for Instagram content."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Lazy client initialization to avoid import-time errors
_client = None


def _get_client() -> OpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


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


def _classify_creator_size(follower_count: int) -> str:
    """Classify creator size for prompt context."""
    if follower_count < 1000:
        return "Micro-creator (<1K followers)"
    elif follower_count < 10000:
        return "Small creator (1K-10K followers)"
    elif follower_count < 100000:
        return "Medium creator (10K-100K followers)"
    elif follower_count < 1000000:
        return "Macro-creator (100K-1M followers)"
    else:
        return "Mega-creator (1M+ followers)"


async def detect_niche(
    caption: str | None,
    hashtags: str | None,
    extended_formats: list[str] | None,
    content_type: str | None,
    creator_follower_count: int
) -> NicheDetectionResult:
    """
    Detect Instagram post/creator niche using OpenAI structured output.

    Analyzes caption, hashtags, content format, and creator metrics to classify
    into one of the defined niches.

    Args:
        caption: Post caption text
        hashtags: Hashtags as JSON array string (e.g., '["fitness", "gym"]')
        extended_formats: Content format categories (e.g., ['Tutorial', 'Educational'])
        content_type: Instagram native type (Reel, Post, Story, etc.)
        creator_follower_count: Creator's follower count for niche determination

    Returns:
        NicheDetectionResult with primary niche, confidence, reasoning

    Raises:
        HTTPException: On OpenAI API failure (401, 429, 500, etc.)
    """
    try:
        # Build rich prompt
        prompt = f"""
Analyze this Instagram post/creator and detect the niche. Choose from the provided options.

Post Analysis:
- Caption: {caption or 'No caption'}
- Hashtags: {hashtags or 'No hashtags'}
- Content Format: {', '.join(extended_formats) if extended_formats else 'Unknown'}
- Instagram Type: {content_type or 'Unknown'}
- Creator Size: {_classify_creator_size(creator_follower_count)}

Available Niches:
{chr(10).join(f"- {niche}" for niche in NICHE_OPTIONS)}

Based on the post analysis, determine:
1. Primary niche (must be from the list above)
2. Secondary niche if applicable (from list, or null)
3. Confidence score (0.0 = not confident, 1.0 = very confident)
4. Brief reasoning explaining the niche choice
5. Key indicators/keywords that led to this niche

Return structured JSON matching the NicheDetectionResult schema.
"""

        client = _get_client()
        message = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=NicheDetectionResult,
            temperature=0.3  # Lower temperature for consistent niche detection
        )

        result = message.choices[0].message.parsed
        logger.info(f"Niche detected: {result.primary_niche} (confidence: {result.confidence:.2f})")
        return result

    except Exception as e:
        logger.error(f"Niche detection failed: {str(e)}")
        # Return fallback "Other" niche instead of crashing
        return NicheDetectionResult(
            primary_niche="Other",
            secondary_niche=None,
            confidence=0.3,
            reasoning="Detection failed, defaulting to Other",
            keywords=[]
        )
