"""Redis caching layer for analysis results with 7-day TTL."""

import json
import logging
from datetime import timedelta
from typing import Optional

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client from Celery broker URL
# decode_responses=True returns strings instead of bytes for convenience
redis_client = redis.Redis.from_url(
    settings.CELERY_BROKER_URL,
    decode_responses=True
)


class ViralAnalysisResult:
    """Serializable analysis result structure."""

    def __init__(
        self,
        viral_post_id: int,
        why_viral_summary: str,
        hook_strength: str,
        emotional_trigger: str,
        posting_time_score: float,
        engagement_velocity: float,
        save_share_ratio: float,
        hashtag_performance: dict,
        audience_demographics: dict,
        content_category: str,
        niche: str,
    ):
        self.viral_post_id = viral_post_id
        self.why_viral_summary = why_viral_summary
        self.hook_strength = hook_strength
        self.emotional_trigger = emotional_trigger
        self.posting_time_score = posting_time_score
        self.engagement_velocity = engagement_velocity
        self.save_share_ratio = save_share_ratio
        self.hashtag_performance = hashtag_performance
        self.audience_demographics = audience_demographics
        self.content_category = content_category
        self.niche = niche

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "viral_post_id": self.viral_post_id,
            "why_viral_summary": self.why_viral_summary,
            "hook_strength": self.hook_strength,
            "emotional_trigger": self.emotional_trigger,
            "posting_time_score": self.posting_time_score,
            "engagement_velocity": self.engagement_velocity,
            "save_share_ratio": self.save_share_ratio,
            "hashtag_performance": self.hashtag_performance,
            "audience_demographics": self.audience_demographics,
            "content_category": self.content_category,
            "niche": self.niche,
        }

    @staticmethod
    def from_dict(data: dict) -> "ViralAnalysisResult":
        """Create from dictionary (deserialization)."""
        return ViralAnalysisResult(
            viral_post_id=data["viral_post_id"],
            why_viral_summary=data["why_viral_summary"],
            hook_strength=data["hook_strength"],
            emotional_trigger=data["emotional_trigger"],
            posting_time_score=data["posting_time_score"],
            engagement_velocity=data["engagement_velocity"],
            save_share_ratio=data["save_share_ratio"],
            hashtag_performance=data["hashtag_performance"],
            audience_demographics=data["audience_demographics"],
            content_category=data["content_category"],
            niche=data["niche"],
        )


def cache_analysis(viral_post_id: int, analysis: ViralAnalysisResult) -> None:
    """
    Store analysis result in Redis with 7-day TTL.

    Args:
        viral_post_id: ID of the viral post
        analysis: ViralAnalysisResult instance to cache

    Returns:
        None (fire-and-forget caching)
    """
    try:
        cache_key = f"analysis:{viral_post_id}"
        analysis_json = json.dumps(analysis.to_dict())
        # setex: SET with EXpiration in seconds
        # TTL: 7 days = 604800 seconds
        redis_client.setex(cache_key, timedelta(days=7), analysis_json)
        logger.debug(f"Cached analysis for viral_post_id={viral_post_id}")
    except redis.RedisError as e:
        # Log error but don't crash; caching is optimization, not critical path
        logger.warning(f"Failed to cache analysis for viral_post_id={viral_post_id}: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error caching analysis: {e}")


def get_cached_analysis(viral_post_id: int) -> Optional[ViralAnalysisResult]:
    """
    Retrieve analysis result from cache.

    Args:
        viral_post_id: ID of the viral post

    Returns:
        ViralAnalysisResult if cached, None if not found or error
    """
    try:
        cache_key = f"analysis:{viral_post_id}"
        cached_json = redis_client.get(cache_key)

        if cached_json is None:
            logger.debug(f"Cache miss for viral_post_id={viral_post_id}")
            return None

        # Deserialize JSON to dict, then construct ViralAnalysisResult
        analysis_data = json.loads(cached_json)
        analysis = ViralAnalysisResult.from_dict(analysis_data)
        logger.debug(f"Cache hit for viral_post_id={viral_post_id}")
        return analysis
    except redis.RedisError as e:
        logger.warning(f"Redis error retrieving cache for viral_post_id={viral_post_id}: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Invalid cached data for viral_post_id={viral_post_id}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error retrieving cache: {e}")
        return None


def clear_analysis_cache(viral_post_id: int) -> None:
    """
    Clear analysis cache for a specific viral post.

    Useful for admin operations, testing, or cache invalidation.

    Args:
        viral_post_id: ID of the viral post

    Returns:
        None
    """
    try:
        cache_key = f"analysis:{viral_post_id}"
        redis_client.delete(cache_key)
        logger.debug(f"Cleared analysis cache for viral_post_id={viral_post_id}")
    except redis.RedisError as e:
        logger.warning(f"Failed to clear cache for viral_post_id={viral_post_id}: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error clearing cache: {e}")
