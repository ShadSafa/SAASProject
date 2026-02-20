"""Algorithm factor calculations for viral content analysis.

This module provides pure Python functions to calculate quantifiable algorithm
factors that don't require OpenAI. These factors are used as inputs to the
AI analysis pipeline, reducing token usage and providing instant scores.
"""

import json
from datetime import datetime
from app.models.viral_post import ViralPost


def calculate_engagement_velocity_score(viral_post: ViralPost) -> float:
    """Calculate engagement velocity score from ViralPost data.

    Engagement velocity = total engagement per hour, normalized to 0-100 scale.
    Typical viral: 100 engagements/hour = score 100.

    Args:
        viral_post: ViralPost instance with engagement counts and post_age_hours.

    Returns:
        Float score 0.0-100.0. Returns 0.0 if post_age_hours is 0 (avoid division).
    """
    if viral_post.post_age_hours is None or viral_post.post_age_hours == 0:
        return 0.0

    total_engagement = (
        viral_post.likes_count
        + viral_post.comments_count
        + viral_post.saves_count
        + viral_post.shares_count
    )

    # Velocity: engagements per hour
    velocity = total_engagement / viral_post.post_age_hours

    # Normalize: min((velocity / 100), 1.0) * 100
    # This means 100 engagements/hour -> 100 score, 50 engagements/hour -> 50 score
    normalized = min(velocity / 100.0, 1.0) * 100.0

    return round(normalized, 2)


def calculate_save_share_ratio_score(viral_post: ViralPost) -> float:
    """Calculate save/share ratio score from ViralPost data.

    High save/share ratio (>20%) indicates high perceived value.
    Score = min((save_share_count / total_engagement) * 500, 100.0)

    Args:
        viral_post: ViralPost instance with engagement counts.

    Returns:
        Float score 0.0-100.0. Returns 0.0 if total_engagement is 0.
    """
    total_engagement = (
        viral_post.likes_count
        + viral_post.comments_count
        + viral_post.saves_count
        + viral_post.shares_count
    )

    if total_engagement == 0:
        return 0.0

    save_share_count = viral_post.saves_count + viral_post.shares_count

    # Ratio: (saves + shares) / total_engagement
    # Score = min((ratio) * 500, 100.0)
    # This means:
    #   5% ratio (typical) -> score 25
    #   20% ratio (high) -> score 100
    ratio = (save_share_count / total_engagement) * 500.0
    normalized = min(ratio, 100.0)

    return round(normalized, 2)


def calculate_hashtag_performance_score(hashtags: str | None) -> float:
    """Calculate hashtag performance score from hashtag count.

    Simple heuristic: 0 hashtags = 0, 1-5 = linear 20-60, 6-15 = 60-90, 15+ = 90-100.
    AI analysis will refine trending/relevance in Phase 4 later analysis.

    Args:
        hashtags: JSON array string like '["#viral", "#trending"]' or None.

    Returns:
        Float score 0.0-100.0.
    """
    if hashtags is None or hashtags == "":
        return 0.0

    try:
        hashtag_list = json.loads(hashtags)
        # Ensure it's a list/array, not a dict or other type
        if not isinstance(hashtag_list, list):
            return 0.0
        hashtag_count = len(hashtag_list)
    except (json.JSONDecodeError, TypeError):
        # Invalid JSON or non-string, treat as no hashtags
        return 0.0

    if hashtag_count == 0:
        return 0.0
    elif hashtag_count <= 5:
        # Linear scale: 1 hashtag = 20, 5 hashtags = 60
        score = 20.0 + (hashtag_count - 1) * 10.0
        return round(min(score, 60.0), 2)
    elif hashtag_count <= 15:
        # Linear scale: 6 hashtags = 60, 15 hashtags = 90
        score = 60.0 + (hashtag_count - 6) * (30.0 / 9.0)
        return round(min(score, 90.0), 2)
    else:
        # 15+ hashtags = 90-100, cap at 100
        score = 90.0 + min((hashtag_count - 15) * 1.0, 10.0)
        return round(min(score, 100.0), 2)


def calculate_posting_time_score(
    created_at: datetime,
    creator_follower_count: int,
) -> float:
    """Calculate posting time score based on hour and account size.

    Prime time (6pm-10pm) scores higher. Large accounts (>100k followers)
    get a +10 bonus since they have global audiences.

    Args:
        created_at: Post creation datetime (UTC assumed).
        creator_follower_count: Number of followers the creator has.

    Returns:
        Float score 0.0-100.0.
    """
    hour = created_at.hour

    # Base score by hour
    if 18 <= hour <= 22:
        # Prime time (6pm-10pm): linear scale 80-100
        base_score = 80.0 + (hour - 18) * 5.0
    elif 12 <= hour < 18 or 22 < hour <= 24:
        # Good time (afternoon after 12pm, or late evening 10pm-midnight)
        if hour < 18:
            base_score = 50.0 + (hour - 12) * (30.0 / 6.0)  # 12-6pm: 50-80
        else:
            base_score = 50.0 + (24 - hour) * (30.0 / 2.0)  # 10pm-12am: 50-80
    elif 6 <= hour < 12:
        # Morning (6am-12pm): linear scale 30-50
        base_score = 30.0 + (hour - 6) * (20.0 / 6.0)
    else:
        # Late night (0-6am): linear scale 10-30
        base_score = 10.0 + hour * (20.0 / 6.0)

    # Bonus for large accounts (>100k followers)
    if creator_follower_count > 100000:
        base_score += 10.0

    return round(min(base_score, 100.0), 2)
