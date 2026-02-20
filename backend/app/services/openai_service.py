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

    Incorporates pre-calculated algorithm factors (engagement velocity, save/share ratio,
    hashtag performance, posting time) in the prompt for AI refinement and validation.

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

    # Pre-calculate algorithm factors (instant, no API call needed)
    from app.services.algorithm_factors import (
        calculate_engagement_velocity_score,
        calculate_save_share_ratio_score,
        calculate_hashtag_performance_score,
        calculate_posting_time_score
    )

    velocity_score = calculate_engagement_velocity_score(viral_post)
    save_share_score = calculate_save_share_ratio_score(viral_post)
    hashtag_score = calculate_hashtag_performance_score(viral_post.hashtags)
    posting_time_score = calculate_posting_time_score(viral_post.created_at, viral_post.creator_follower_count)

    # Build analysis prompt with pre-calculated factors
    prompt = f"""Analyze this viral Instagram post and provide AI-enhanced analysis.

POST DATA:
- Caption: {viral_post.caption or "(No caption)"}
- Hashtags: {viral_post.hashtags or "(No hashtags)"}
- Post Type: {viral_post.post_type}
- Creator: @{viral_post.creator_username} ({viral_post.creator_follower_count:,} followers)
- Engagement: {viral_post.likes_count:,} likes, {viral_post.comments_count:,} comments, {viral_post.saves_count:,} saves, {viral_post.shares_count:,} shares
- Post Age: {viral_post.post_age_hours:.1f} hours

PRE-CALCULATED ALGORITHM FACTORS (validate/refine if needed):
- Engagement Velocity: {velocity_score:.1f}/100
- Save/Share Ratio: {save_share_score:.1f}/100
- Hashtag Performance: {hashtag_score:.1f}/100
- Posting Time: {posting_time_score:.1f}/100

YOUR ANALYSIS TASKS:
1. Why Viral Summary: 2-3 sentences explaining what made this post go viral
2. Validate/refine the 4 pre-calculated scores above (adjust if mathematical calculation missed context)
3. Hook Strength (0-100): Rate the opening (first line of caption for photos, first 3 seconds for videos)
4. Emotional Trigger: Which primary emotion? (joy|awe|anger|surprise|sadness|fear)
5. Audience Retention (0-100): How well does content hold attention throughout?
6. Confidence Score (0-1): How confident are you in this analysis?

Provide structured analysis following the ViralAnalysisResult schema."""

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
