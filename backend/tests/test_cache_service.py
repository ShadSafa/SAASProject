"""Test suite for Redis cache service."""

import json
from datetime import timedelta
from unittest.mock import patch, MagicMock

import fakeredis
import pytest
import redis

from app.services.cache_service import (
    ViralAnalysisResult,
    cache_analysis,
    get_cached_analysis,
    clear_analysis_cache,
)


@pytest.fixture
def mock_redis():
    """Provide in-memory fake Redis client for testing."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def sample_analysis():
    """Sample ViralAnalysisResult for testing."""
    return ViralAnalysisResult(
        viral_post_id=123,
        why_viral_summary="Strong emotional hook combined with trending audio",
        hook_strength="Very High",
        emotional_trigger="Inspiration",
        posting_time_score=8.5,
        engagement_velocity=1.2,
        save_share_ratio=0.75,
        hashtag_performance={"trending": ["reels", "viral", "motivation"]},
        audience_demographics={"age_range": "18-35", "gender": "mixed"},
        content_category="Motivational",
        niche="Personal Development",
    )


def test_cache_analysis_stores_with_ttl(mock_redis, sample_analysis):
    """Verify cache_analysis stores result with 7-day TTL."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        cache_analysis(sample_analysis.viral_post_id, sample_analysis)

        # Verify key exists
        cache_key = f"analysis:{sample_analysis.viral_post_id}"
        assert mock_redis.exists(cache_key)

        # Verify stored data is correct
        cached_json = mock_redis.get(cache_key)
        cached_data = json.loads(cached_json)
        assert cached_data["viral_post_id"] == 123
        assert cached_data["why_viral_summary"] == "Strong emotional hook combined with trending audio"

        # Verify TTL is approximately 7 days (604800 seconds)
        ttl = mock_redis.ttl(cache_key)
        # Allow some tolerance (ttl should be <= 7 days and > 6.99 days in seconds)
        assert 600000 < ttl <= 604800  # Between 6.94-7 days


def test_get_cached_analysis_hit(mock_redis, sample_analysis):
    """Verify cache hit returns ViralAnalysisResult correctly."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        # Pre-populate cache
        cache_analysis(sample_analysis.viral_post_id, sample_analysis)

        # Retrieve from cache
        result = get_cached_analysis(sample_analysis.viral_post_id)

        # Verify correct result returned
        assert result is not None
        assert result.viral_post_id == 123
        assert result.why_viral_summary == "Strong emotional hook combined with trending audio"
        assert result.hook_strength == "Very High"
        assert result.emotional_trigger == "Inspiration"
        assert result.posting_time_score == 8.5
        assert result.engagement_velocity == 1.2
        assert result.save_share_ratio == 0.75
        assert result.content_category == "Motivational"
        assert result.niche == "Personal Development"


def test_get_cached_analysis_miss(mock_redis):
    """Verify cache miss returns None."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        result = get_cached_analysis(999)  # Non-existent post ID
        assert result is None


def test_cache_key_format(mock_redis, sample_analysis):
    """Verify cache key format is 'analysis:{viral_post_id}'."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        cache_analysis(sample_analysis.viral_post_id, sample_analysis)

        # Check exact key exists
        expected_key = f"analysis:{sample_analysis.viral_post_id}"
        assert mock_redis.exists(expected_key)

        # Verify key is in the expected format
        keys = mock_redis.keys("analysis:*")
        assert expected_key in keys


def test_cache_handles_redis_error_on_set(sample_analysis):
    """Verify graceful handling of Redis errors when caching."""
    mock_redis = MagicMock()
    mock_redis.setex.side_effect = redis.RedisError("Connection failed")

    with patch("app.services.cache_service.redis_client", mock_redis):
        # Should not raise exception
        cache_analysis(sample_analysis.viral_post_id, sample_analysis)
        # Verify setex was attempted
        assert mock_redis.setex.called


def test_cache_handles_redis_error_on_get(mock_redis):
    """Verify graceful handling of Redis errors when retrieving."""
    mock_redis_with_error = MagicMock()
    mock_redis_with_error.get.side_effect = redis.RedisError("Connection failed")

    with patch("app.services.cache_service.redis_client", mock_redis_with_error):
        result = get_cached_analysis(123)
        # Should return None on error, not raise
        assert result is None


def test_cache_handles_invalid_json(mock_redis):
    """Verify graceful handling of corrupted cache data."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        # Store invalid JSON
        cache_key = "analysis:123"
        mock_redis.set(cache_key, "{invalid json")

        # Retrieving should return None, not raise
        result = get_cached_analysis(123)
        assert result is None


def test_clear_analysis_cache(mock_redis, sample_analysis):
    """Verify clear_analysis_cache removes cached entry."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        # Cache the analysis
        cache_analysis(sample_analysis.viral_post_id, sample_analysis)
        cache_key = f"analysis:{sample_analysis.viral_post_id}"
        assert mock_redis.exists(cache_key)

        # Clear it
        clear_analysis_cache(sample_analysis.viral_post_id)

        # Verify it's gone
        assert not mock_redis.exists(cache_key)


def test_clear_analysis_cache_nonexistent(mock_redis):
    """Verify clearing non-existent cache key doesn't raise error."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        # Should not raise exception
        clear_analysis_cache(999)


def test_viral_analysis_result_serialization(sample_analysis):
    """Verify ViralAnalysisResult can be serialized and deserialized."""
    # Serialize to dict
    data = sample_analysis.to_dict()
    assert isinstance(data, dict)
    assert data["viral_post_id"] == 123
    assert data["why_viral_summary"] == "Strong emotional hook combined with trending audio"

    # Deserialize from dict
    restored = ViralAnalysisResult.from_dict(data)
    assert restored.viral_post_id == sample_analysis.viral_post_id
    assert restored.why_viral_summary == sample_analysis.why_viral_summary
    assert restored.hook_strength == sample_analysis.hook_strength
    assert restored.emotional_trigger == sample_analysis.emotional_trigger
    assert restored.posting_time_score == sample_analysis.posting_time_score
    assert restored.engagement_velocity == sample_analysis.engagement_velocity
    assert restored.save_share_ratio == sample_analysis.save_share_ratio
    assert restored.hashtag_performance == sample_analysis.hashtag_performance
    assert restored.audience_demographics == sample_analysis.audience_demographics
    assert restored.content_category == sample_analysis.content_category
    assert restored.niche == sample_analysis.niche


def test_viral_analysis_result_json_round_trip(sample_analysis):
    """Verify JSON serialization round-trip maintains data integrity."""
    # Serialize to JSON
    json_str = json.dumps(sample_analysis.to_dict())

    # Deserialize from JSON
    data = json.loads(json_str)
    restored = ViralAnalysisResult.from_dict(data)

    # Verify all fields match
    assert restored.viral_post_id == sample_analysis.viral_post_id
    assert restored.why_viral_summary == sample_analysis.why_viral_summary
    assert restored.posting_time_score == sample_analysis.posting_time_score
    assert restored.save_share_ratio == sample_analysis.save_share_ratio
    assert restored.hashtag_performance == sample_analysis.hashtag_performance


def test_multiple_analyses_in_cache(mock_redis):
    """Verify multiple analyses can be cached independently."""
    with patch("app.services.cache_service.redis_client", mock_redis):
        # Create and cache multiple analyses
        analyses = [
            ViralAnalysisResult(
                viral_post_id=1,
                why_viral_summary="First",
                hook_strength="High",
                emotional_trigger="Joy",
                posting_time_score=7.0,
                engagement_velocity=1.0,
                save_share_ratio=0.5,
                hashtag_performance={},
                audience_demographics={},
                content_category="Category1",
                niche="Niche1",
            ),
            ViralAnalysisResult(
                viral_post_id=2,
                why_viral_summary="Second",
                hook_strength="Very High",
                emotional_trigger="Surprise",
                posting_time_score=9.0,
                engagement_velocity=1.5,
                save_share_ratio=0.8,
                hashtag_performance={},
                audience_demographics={},
                content_category="Category2",
                niche="Niche2",
            ),
        ]

        for analysis in analyses:
            cache_analysis(analysis.viral_post_id, analysis)

        # Verify both are retrievable independently
        result1 = get_cached_analysis(1)
        result2 = get_cached_analysis(2)

        assert result1.why_viral_summary == "First"
        assert result2.why_viral_summary == "Second"
        assert result1.viral_post_id == 1
        assert result2.viral_post_id == 2
