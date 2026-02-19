"""Viral scoring algorithm for Instagram content analysis.

This module provides core scoring functions used by the scanning engine
to rank posts by viral potential based on engagement rate and posting velocity.
"""


def _get_velocity_multiplier(post_age_hours: float) -> float:
    """Return the velocity multiplier for the given post age.

    Args:
        post_age_hours: Age of the post in hours.

    Returns:
        Velocity multiplier based on post age:
        - < 1 hour:      3.0 (exceptional speed)
        - 1 to < 2 hrs:  2.5 (very fast)
        - 2 to < 4 hrs:  2.0 (fast)
        - 4 to < 12 hrs: 1.5 (moderate)
        - 12 to < 24 hrs: 1.0 (normal)
        - >= 24 hrs:     0.5 (slow)
    """
    if post_age_hours < 1.0:
        return 3.0
    elif post_age_hours < 2.0:
        return 2.5
    elif post_age_hours < 4.0:
        return 2.0
    elif post_age_hours < 12.0:
        return 1.5
    elif post_age_hours <= 24.0:
        return 1.0
    else:
        return 0.5


def calculate_viral_score(
    engagement_count: int,
    follower_count: int,
    post_age_hours: float,
) -> float:
    """Calculate the viral score for a post.

    Formula: (engagement_count / follower_count) * velocity_multiplier * 100,
    capped at 100.0.

    Args:
        engagement_count: Total number of engagements (likes + comments + shares).
        follower_count: Number of followers the account has at time of measurement.
        post_age_hours: How old the post is in hours at time of measurement.

    Returns:
        Viral score as a float in the range [0.0, 100.0].
        Returns 0.0 when follower_count is 0 (avoids ZeroDivisionError).
        Returns 0.0 when engagement_count is 0.
    """
    if follower_count == 0:
        return 0.0

    engagement_rate = engagement_count / follower_count
    velocity_multiplier = _get_velocity_multiplier(post_age_hours)
    raw_score = engagement_rate * velocity_multiplier * 100.0

    return round(min(raw_score, 100.0), 10)


def calculate_growth_velocity(
    current_engagement: int,
    previous_engagement: int,
    time_delta_hours: float,
) -> float:
    """Calculate the rate of engagement growth per hour.

    Args:
        current_engagement: Engagement count at the current measurement.
        previous_engagement: Engagement count at the previous measurement.
        time_delta_hours: Time elapsed between measurements in hours.

    Returns:
        Engagements gained per hour as a float.
        Returns 0.0 if time_delta_hours is 0 (avoids ZeroDivisionError).
    """
    if time_delta_hours == 0:
        return 0.0

    return (current_engagement - previous_engagement) / time_delta_hours
