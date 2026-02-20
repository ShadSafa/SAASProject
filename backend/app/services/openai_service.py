"""OpenAI API service for viral post analysis with structured output."""

import json
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

from app.config import settings
from app.models.viral_post import ViralPost


class ViralAnalysisResult(BaseModel):
    """Complete AI analysis of a viral post with 7 algorithm factors."""

    why_viral_summary: str = Field(
        ..., description="2-3 sentence explanation of why this post went viral"
    )
    posting_time_score: float = Field(
        ..., ge=0.0, le=100.0, description="Score for posting time optimization (0-100)"
    )
    hook_strength: float = Field(
        ..., ge=0.0, le=100.0, description="Score for hook strength in first 3 seconds/caption opening (0-100)"
    )
    emotional_trigger: str = Field(
        ..., description="Primary emotional trigger: joy|awe|anger|surprise|sadness|fear"
    )
    engagement_velocity_score: float = Field(
        ..., ge=0.0, le=100.0, description="Score for how quickly engagement was gained (0-100)"
    )
    save_share_ratio_score: float = Field(
        ..., ge=0.0, le=100.0, description="Score for saves/shares vs likes ratio (high saves=high value) (0-100)"
    )
    hashtag_performance: float = Field(
        ..., ge=0.0, le=100.0, description="Score for hashtag relevance and trending status (0-100)"
    )
    audience_retention: float = Field(
        ..., ge=0.0, le=100.0, description="Score for audience retention throughout content (0-100)"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the analysis (0.0-1.0)"
    )


def analyze_viral_post(viral_post: ViralPost) -> ViralAnalysisResult:
    """
    Analyze a viral Instagram post and score 7 algorithm factors.

    Uses OpenAI's GPT-4o model with structured output to generate reliable,
    validated JSON responses matching the ViralAnalysisResult schema.

    Args:
        viral_post: ViralPost ORM object with engagement metrics, caption, etc.

    Returns:
        ViralAnalysisResult: Analysis with 7 algorithm factors scored 0-100

    Raises:
        HTTPException: On API errors (auth, rate limit, timeout)
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Build analysis prompt with all available post data
    prompt = f"""Analyze this viral Instagram post and score 7 algorithm factors (0-100 each).

POST DETAILS:
- Caption: {viral_post.caption or "(No caption)"}
- Hashtags: {viral_post.hashtags or "(No hashtags)"}
- Post Type: {viral_post.post_type}
- Creator: @{viral_post.creator_username} ({viral_post.creator_follower_count:,} followers)
- Age: {viral_post.post_age_hours:.1f} hours old
- Engagement:
  - Likes: {viral_post.likes_count:,}
  - Comments: {viral_post.comments_count:,}
  - Saves: {viral_post.saves_count:,}
  - Shares: {viral_post.shares_count:,}

SCORING GUIDANCE:
1. Posting Time (0-100): Is posting time optimal for audience timezone and engagement window?
2. Hook Strength (0-100): How strong is the hook in first 3 seconds or caption opening?
3. Emotional Trigger (joy|awe|anger|surprise|sadness|fear): What primary emotion does it evoke?
4. Engagement Velocity (0-100): How quickly did it gain engagement? (rapid = high score)
5. Save/Share Ratio (0-100): High saves relative to likes = high value = high score (0-100)
6. Hashtag Performance (0-100): How relevant and trending are the hashtags? (0-100)
7. Audience Retention (0-100): Does content hold attention throughout? (0-100)

Provide a 2-3 sentence summary of why this post went viral, then score each factor.
Also provide a confidence score (0.0-1.0) for how confident you are in this analysis."""

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Instagram viral content analyst. Analyze posts and provide structured, data-driven scoring of viral factors."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=ViralAnalysisResult
        )

        # Extract and validate the parsed response
        analysis = response.choices[0].message.parsed

        if not analysis:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse OpenAI response"
            )

        return analysis

    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=f"OpenAI authentication failed. Check your API key. Error: {str(e)}"
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail=f"OpenAI rate limit exceeded. Try again later. Error: {str(e)}"
        )
    except APIConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to OpenAI API. Service may be down. Error: {str(e)}"
        )
    except APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during analysis: {str(e)}"
        )
