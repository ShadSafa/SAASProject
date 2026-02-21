"""Engagement rate calculation service for viral posts."""

from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.models.viral_post import ViralPost


class EngagementMetrics(BaseModel):
    """Engagement metrics for a viral post."""

    engagement_rate: float = Field(
        ..., ge=0.0, description="Engagement rate as percentage (0-100+)"
    )
    total_interactions: int = Field(
        ..., ge=0, description="Sum of likes + comments + saves + shares"
    )
    follower_count: int = Field(..., ge=0, description="Creator's follower count")
    interaction_per_follower: float = Field(
        ..., ge=0.0, description="Decimal form of engagement rate"
    )


def calculate_engagement_rate(viral_post: "ViralPost") -> EngagementMetrics:
    """
    Calculate engagement rate relative to follower count.

    Formula: (likes + comments + saves + shares) / follower_count * 100

    Args:
        viral_post: ViralPost ORM object with engagement metrics and follower_count

    Returns:
        EngagementMetrics with engagement_rate percentage

    Handles edge cases:
    - If follower_count is 0, return 0.0 engagement rate (don't crash)
    - Small creators with high engagement can have rates > 100%
    """
    total_interactions = (
        viral_post.likes_count
        + viral_post.comments_count
        + viral_post.saves_count
        + viral_post.shares_count
    )

    if viral_post.creator_follower_count == 0:
        engagement_rate = 0.0
        interaction_per_follower = 0.0
    else:
        engagement_rate = (
            total_interactions / viral_post.creator_follower_count
        ) * 100
        interaction_per_follower = (
            total_interactions / viral_post.creator_follower_count
        )

    return EngagementMetrics(
        engagement_rate=engagement_rate,
        total_interactions=total_interactions,
        follower_count=viral_post.creator_follower_count,
        interaction_per_follower=interaction_per_follower,
    )


def calculate_engagement_rate_from_values(
    likes: int, comments: int, saves: int, shares: int, follower_count: int
) -> float:
    """
    Calculate engagement rate from raw values (for batch processing).

    Args:
        likes: Number of likes
        comments: Number of comments
        saves: Number of saves
        shares: Number of shares
        follower_count: Creator's follower count

    Returns:
        Engagement rate as percentage (can exceed 100 for small creators)
    """
    if follower_count == 0:
        return 0.0

    total_interactions = likes + comments + saves + shares
    return (total_interactions / follower_count) * 100


def should_calculate_engagement_rate_for_post(viral_post: "ViralPost") -> bool:
    """
    Check if we should calculate engagement rate for this post.

    Returns True if all required metrics exist:
    - creator_follower_count > 0 or = 0 (always calculate)
    - At least one engagement metric (likes, comments, saves, or shares)
    """
    has_engagement = (
        viral_post.likes_count > 0
        or viral_post.comments_count > 0
        or viral_post.saves_count > 0
        or viral_post.shares_count > 0
    )
    return has_engagement or viral_post.creator_follower_count > 0
