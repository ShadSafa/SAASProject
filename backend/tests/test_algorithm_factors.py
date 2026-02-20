"""Tests for algorithm factor calculations.

Tests verify that all 4 algorithm factor functions return deterministic
scores in the 0.0-100.0 range and handle edge cases gracefully.
"""

import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from app.services.algorithm_factors import (
    calculate_engagement_velocity_score,
    calculate_save_share_ratio_score,
    calculate_hashtag_performance_score,
    calculate_posting_time_score,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def viral_post_high_velocity():
    """ViralPost with high engagement velocity: 10k engagements in 1 hour."""
    post = Mock()
    post.likes_count = 7000
    post.comments_count = 2000
    post.saves_count = 800
    post.shares_count = 200
    post.post_age_hours = 1.0
    return post


@pytest.fixture
def viral_post_low_velocity():
    """ViralPost with low engagement velocity: 100 engagements in 10 hours."""
    post = Mock()
    post.likes_count = 70
    post.comments_count = 20
    post.saves_count = 5
    post.shares_count = 5
    post.post_age_hours = 10.0
    return post


@pytest.fixture
def viral_post_high_save_ratio():
    """ViralPost with 30% save+share ratio."""
    post = Mock()
    post.likes_count = 5000
    post.comments_count = 1000
    post.saves_count = 1500  # 30% of 5k
    post.shares_count = 1500  # 30% of 5k (total: 60% of (5k+1k))
    post.post_age_hours = 2.0
    return post


@pytest.fixture
def viral_post_low_save_ratio():
    """ViralPost with 5% save+share ratio."""
    post = Mock()
    post.likes_count = 8000
    post.comments_count = 1000
    post.saves_count = 350  # ~5% of 9k
    post.shares_count = 150  # ~5% of 9k
    post.post_age_hours = 1.5
    return post


@pytest.fixture
def viral_post_zero_engagement():
    """ViralPost with no engagement at all."""
    post = Mock()
    post.likes_count = 0
    post.comments_count = 0
    post.saves_count = 0
    post.shares_count = 0
    post.post_age_hours = 5.0
    return post


@pytest.fixture
def viral_post_zero_age():
    """ViralPost with zero age (avoid division by zero)."""
    post = Mock()
    post.likes_count = 1000
    post.comments_count = 200
    post.saves_count = 100
    post.shares_count = 50
    post.post_age_hours = 0
    return post


# ============================================================================
# ENGAGEMENT VELOCITY SCORE TESTS
# ============================================================================


class TestEngagementVelocityScore:
    """Tests for calculate_engagement_velocity_score."""

    def test_high_velocity(self, viral_post_high_velocity):
        """10k engagements / 1 hour -> score ~100."""
        score = calculate_engagement_velocity_score(viral_post_high_velocity)
        assert 95.0 <= score <= 100.0
        assert isinstance(score, float)

    def test_low_velocity(self, viral_post_low_velocity):
        """100 engagements / 10 hours -> score ~10."""
        score = calculate_engagement_velocity_score(viral_post_low_velocity)
        assert 8.0 <= score <= 12.0
        assert isinstance(score, float)

    def test_zero_age(self, viral_post_zero_age):
        """post_age_hours = 0 -> score 0 (no division error)."""
        score = calculate_engagement_velocity_score(viral_post_zero_age)
        assert score == 0.0

    def test_none_age(self):
        """post_age_hours = None -> score 0 (no error)."""
        post = Mock()
        post.likes_count = 100
        post.comments_count = 20
        post.saves_count = 10
        post.shares_count = 5
        post.post_age_hours = None
        score = calculate_engagement_velocity_score(post)
        assert score == 0.0

    def test_medium_velocity(self):
        """500 engagements / 5 hours -> score ~100 (capped)."""
        post = Mock()
        post.likes_count = 400
        post.comments_count = 80
        post.saves_count = 15
        post.shares_count = 5
        post.post_age_hours = 5.0
        score = calculate_engagement_velocity_score(post)
        assert 95.0 <= score <= 100.0

    def test_score_within_bounds(self, viral_post_high_velocity):
        """Score always between 0.0 and 100.0."""
        score = calculate_engagement_velocity_score(viral_post_high_velocity)
        assert 0.0 <= score <= 100.0


# ============================================================================
# SAVE/SHARE RATIO SCORE TESTS
# ============================================================================


class TestSaveShareRatioScore:
    """Tests for calculate_save_share_ratio_score."""

    def test_high_ratio(self, viral_post_high_save_ratio):
        """30% saves+shares -> score should be high (~100+)."""
        score = calculate_save_share_ratio_score(viral_post_high_save_ratio)
        assert 90.0 <= score <= 100.0
        assert isinstance(score, float)

    def test_low_ratio(self, viral_post_low_save_ratio):
        """5% saves+shares -> score should be low (~25)."""
        score = calculate_save_share_ratio_score(viral_post_low_save_ratio)
        assert 20.0 <= score <= 30.0
        assert isinstance(score, float)

    def test_zero_engagement(self, viral_post_zero_engagement):
        """total_engagement = 0 -> score 0 (no division error)."""
        score = calculate_save_share_ratio_score(viral_post_zero_engagement)
        assert score == 0.0

    def test_no_saves_shares(self):
        """saves_count = 0, shares_count = 0 -> score 0."""
        post = Mock()
        post.likes_count = 1000
        post.comments_count = 100
        post.saves_count = 0
        post.shares_count = 0
        post.post_age_hours = 1.0
        score = calculate_save_share_ratio_score(post)
        assert score == 0.0

    def test_20_percent_ratio(self):
        """20% saves+shares of total engagement -> score ~100."""
        post = Mock()
        post.likes_count = 6000
        post.comments_count = 1000
        post.saves_count = 1500  # 20% of 7500
        post.shares_count = 1500  # 20% of 7500
        post.post_age_hours = 1.0
        score = calculate_save_share_ratio_score(post)
        # 3000 / 10000 * 500 = 150, capped at 100
        assert 98.0 <= score <= 100.0

    def test_score_within_bounds(self, viral_post_high_save_ratio):
        """Score always between 0.0 and 100.0."""
        score = calculate_save_share_ratio_score(viral_post_high_save_ratio)
        assert 0.0 <= score <= 100.0


# ============================================================================
# HASHTAG PERFORMANCE SCORE TESTS
# ============================================================================


class TestHashtagPerformanceScore:
    """Tests for calculate_hashtag_performance_score."""

    def test_no_hashtags(self):
        """None hashtags -> score 0."""
        score = calculate_hashtag_performance_score(None)
        assert score == 0.0

    def test_empty_string(self):
        """Empty string hashtags -> score 0."""
        score = calculate_hashtag_performance_score("")
        assert score == 0.0

    def test_empty_json_array(self):
        """Empty JSON array -> score 0."""
        score = calculate_hashtag_performance_score("[]")
        assert score == 0.0

    def test_one_hashtag(self):
        """1 hashtag -> score ~20."""
        hashtags = json.dumps(["#viral"])
        score = calculate_hashtag_performance_score(hashtags)
        assert 18.0 <= score <= 22.0

    def test_optimal_hashtags(self):
        """8 hashtags -> score ~60-70 (middle of 6-15 range)."""
        hashtags = json.dumps([
            "#viral", "#trending", "#fyp", "#reels",
            "#instagram", "#content", "#growth", "#engagement"
        ])
        score = calculate_hashtag_performance_score(hashtags)
        assert 65.0 <= score <= 75.0

    def test_too_many_hashtags(self):
        """20 hashtags -> score ~95+."""
        hashtags = json.dumps([f"#tag{i}" for i in range(20)])
        score = calculate_hashtag_performance_score(hashtags)
        assert 92.0 <= score <= 100.0

    def test_invalid_json(self):
        """Invalid JSON -> score 0."""
        score = calculate_hashtag_performance_score("not valid json")
        assert score == 0.0

    def test_non_array_json(self):
        """Valid JSON but not array -> score 0."""
        score = calculate_hashtag_performance_score('{"tags": ["a", "b"]}')
        assert score == 0.0

    def test_15_hashtags_boundary(self):
        """15 hashtags -> score ~90."""
        hashtags = json.dumps([f"#tag{i}" for i in range(15)])
        score = calculate_hashtag_performance_score(hashtags)
        assert 88.0 <= score <= 92.0

    def test_score_within_bounds(self):
        """Score always between 0.0 and 100.0."""
        hashtags = json.dumps([f"#tag{i}" for i in range(30)])
        score = calculate_hashtag_performance_score(hashtags)
        assert 0.0 <= score <= 100.0


# ============================================================================
# POSTING TIME SCORE TESTS
# ============================================================================


class TestPostingTimeScore:
    """Tests for calculate_posting_time_score."""

    def test_prime_time_7pm(self):
        """Hour = 19 (7pm) -> score 90-100 (prime time)."""
        created_at = datetime(2026, 2, 21, 19, 30, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 85.0 <= score <= 100.0

    def test_morning_9am(self):
        """Hour = 9 (9am) -> score 30-50 (morning)."""
        created_at = datetime(2026, 2, 21, 9, 0, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 30.0 <= score <= 50.0

    def test_late_night_2am(self):
        """Hour = 2 (2am) -> score 10-30 (late night)."""
        created_at = datetime(2026, 2, 21, 2, 0, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 10.0 <= score <= 30.0

    def test_large_account_bonus(self):
        """Large account (500k followers) gets +10 bonus."""
        created_at = datetime(2026, 2, 21, 9, 0, 0)
        score_small = calculate_posting_time_score(created_at, 50000)
        score_large = calculate_posting_time_score(created_at, 500000)
        # Large account should be ~10 points higher
        assert (score_large - score_small) >= 8.0

    def test_afternoon_2pm(self):
        """Hour = 14 (2pm) -> score 50-80 (good time)."""
        created_at = datetime(2026, 2, 21, 14, 0, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 50.0 <= score <= 80.0

    def test_evening_11pm(self):
        """Hour = 23 (11pm) -> score 50-80 (good time)."""
        created_at = datetime(2026, 2, 21, 23, 0, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 50.0 <= score <= 80.0

    def test_midnight_0am(self):
        """Hour = 0 (midnight) -> score 10-30 (late night)."""
        created_at = datetime(2026, 2, 21, 0, 0, 0)
        score = calculate_posting_time_score(created_at, 10000)
        assert 10.0 <= score <= 30.0

    def test_small_account_no_bonus(self):
        """Small account (<100k followers) gets no bonus."""
        created_at = datetime(2026, 2, 21, 20, 0, 0)
        score = calculate_posting_time_score(created_at, 50000)
        # Should be in prime time range
        assert 80.0 <= score <= 100.0

    def test_score_within_bounds(self):
        """Score always between 0.0 and 100.0."""
        created_at = datetime(2026, 2, 21, 18, 0, 0)
        score = calculate_posting_time_score(created_at, 1000000)
        assert 0.0 <= score <= 100.0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestAlgorithmFactorsIntegration:
    """Integration tests with realistic data."""

    def test_all_functions_callable_with_real_data(self):
        """All functions should work with realistic ViralPost data."""
        post = Mock()
        post.likes_count = 5000
        post.comments_count = 1000
        post.saves_count = 500
        post.shares_count = 200
        post.post_age_hours = 2.5
        post.creator_follower_count = 250000

        hashtags = json.dumps(["#viral", "#trending", "#reels"])

        velocity = calculate_engagement_velocity_score(post)
        ratio = calculate_save_share_ratio_score(post)
        hashtag = calculate_hashtag_performance_score(hashtags)
        time_score = calculate_posting_time_score(
            datetime(2026, 2, 21, 19, 30, 0),
            post.creator_follower_count
        )

        assert all(isinstance(s, float) for s in [velocity, ratio, hashtag, time_score])
        assert all(0.0 <= s <= 100.0 for s in [velocity, ratio, hashtag, time_score])

    def test_viral_post_with_all_zeros(self):
        """Even all-zero posts should return valid scores."""
        post = Mock()
        post.likes_count = 0
        post.comments_count = 0
        post.saves_count = 0
        post.shares_count = 0
        post.post_age_hours = 0

        velocity = calculate_engagement_velocity_score(post)
        ratio = calculate_save_share_ratio_score(post)

        assert velocity == 0.0
        assert ratio == 0.0

    def test_viral_post_extreme_values(self):
        """Scores cap at 100 for extreme engagement."""
        post = Mock()
        post.likes_count = 1000000
        post.comments_count = 500000
        post.saves_count = 250000
        post.shares_count = 100000
        post.post_age_hours = 1.0

        velocity = calculate_engagement_velocity_score(post)
        ratio = calculate_save_share_ratio_score(post)

        # Both should be capped at 100
        assert velocity == 100.0
        # ratio = 350000 / 1850000 * 500 = 94.59
        assert ratio >= 90.0
