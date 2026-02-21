"""Tests for engagement rate calculation service."""

import pytest
from app.services.engagement_service import (
    calculate_engagement_rate,
    calculate_engagement_rate_from_values,
    EngagementMetrics,
)


def test_engagement_rate_basic_calculation():
    """Test basic engagement rate calculation: (interactions / followers) * 100"""
    # 1000 interactions / 100000 followers = 1%
    rate = calculate_engagement_rate_from_values(
        likes=600, comments=200, saves=150, shares=50, follower_count=100000
    )
    assert rate == 1.0


def test_engagement_rate_zero_followers():
    """Test edge case: follower_count is 0"""
    rate = calculate_engagement_rate_from_values(
        likes=100, comments=50, saves=30, shares=20, follower_count=0
    )
    assert rate == 0.0  # Should not crash


def test_engagement_rate_small_creator_exceeds_100():
    """Test that small creators with high engagement can exceed 100%"""
    # 250 interactions / 100 followers = 250%
    rate = calculate_engagement_rate_from_values(
        likes=150, comments=60, saves=30, shares=10, follower_count=100
    )
    assert rate == 250.0


def test_engagement_metrics_includes_all_fields():
    """Test EngagementMetrics model has all required fields"""
    metrics = EngagementMetrics(
        engagement_rate=5.5,
        total_interactions=1100,
        follower_count=20000,
        interaction_per_follower=0.055,
    )
    assert metrics.engagement_rate == 5.5
    assert metrics.total_interactions == 1100
    assert metrics.follower_count == 20000
    assert metrics.interaction_per_follower == 0.055


@pytest.fixture
def mock_viral_post():
    """Mock ViralPost object for testing."""

    class MockViralPost:
        def __init__(self):
            self.creator_follower_count = 0
            self.likes_count = 0
            self.comments_count = 0
            self.saves_count = 0
            self.shares_count = 0

    return MockViralPost()


def test_calculate_engagement_rate_from_viral_post(mock_viral_post):
    """Test calculate_engagement_rate with ViralPost ORM object"""
    # Mock viral post with 50000 followers, 1000 interactions
    mock_viral_post.creator_follower_count = 50000
    mock_viral_post.likes_count = 600
    mock_viral_post.comments_count = 200
    mock_viral_post.saves_count = 150
    mock_viral_post.shares_count = 50

    metrics = calculate_engagement_rate(mock_viral_post)
    assert metrics.engagement_rate == 2.0  # 1000 / 50000 * 100
    assert metrics.total_interactions == 1000
    assert metrics.follower_count == 50000
    assert metrics.interaction_per_follower == 0.02


def test_engagement_rate_precision():
    """Test engagement rate calculation precision"""
    # 1 interaction / 3 followers = 33.333...%
    rate = calculate_engagement_rate_from_values(
        likes=1, comments=0, saves=0, shares=0, follower_count=3
    )
    assert abs(rate - 33.33333333333333) < 0.0001
