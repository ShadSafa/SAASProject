"""Tests for viral scoring algorithm.

TDD RED phase: All tests written before implementation.
"""
import pytest
from app.services.viral_scoring import calculate_viral_score, calculate_growth_velocity


class TestCalculateViralScore:
    """Tests for calculate_viral_score(engagement_count, follower_count, post_age_hours) -> float."""

    # --- Velocity multiplier boundary tests ---

    def test_score_age_under_1_hour_multiplier_3(self):
        """Posts < 1 hour old use 3.0 velocity multiplier."""
        # (1000 / 10000) * 3.0 * 100 = 30.0
        result = calculate_viral_score(1000, 10000, 0.5)
        assert result == 30.0

    def test_score_age_1_to_2_hours_multiplier_2_5(self):
        """Posts 1 to < 2 hours old use 2.5 velocity multiplier."""
        # (1000 / 10000) * 2.5 * 100 = 25.0
        result = calculate_viral_score(1000, 10000, 1.0)
        assert result == 25.0

    def test_score_age_2_to_4_hours_multiplier_2(self):
        """Posts 2 to < 4 hours old use 2.0 velocity multiplier."""
        # (100 / 1000) * 2.0 * 100 = 20.0
        result = calculate_viral_score(100, 1000, 3.0)
        assert result == 20.0

    def test_score_age_4_to_12_hours_multiplier_1_5(self):
        """Posts 4 to < 12 hours old use 1.5 velocity multiplier."""
        # (100 / 1000) * 1.5 * 100 = 15.0
        result = calculate_viral_score(100, 1000, 8.0)
        assert result == 15.0

    def test_score_age_12_to_24_hours_multiplier_1(self):
        """Posts 12 to < 24 hours old use 1.0 velocity multiplier."""
        # (100 / 1000) * 1.0 * 100 = 10.0
        result = calculate_viral_score(100, 1000, 24.0)
        assert result == 10.0

    def test_score_age_24_hours_or_more_multiplier_0_5(self):
        """Posts >= 24 hours old use 0.5 velocity multiplier."""
        # (100 / 1000) * 0.5 * 100 = 5.0
        result = calculate_viral_score(100, 1000, 48.0)
        assert result == 5.0

    # --- Boundary conditions at exact thresholds ---

    def test_score_age_exactly_1_hour_uses_2_5_multiplier(self):
        """Age == 1.0 should use 2.5 multiplier (1 to < 2 range)."""
        result = calculate_viral_score(1000, 10000, 1.0)
        assert result == 25.0

    def test_score_age_exactly_2_hours_uses_2_0_multiplier(self):
        """Age == 2.0 should use 2.0 multiplier (2 to < 4 range)."""
        # (1000 / 10000) * 2.0 * 100 = 20.0
        result = calculate_viral_score(1000, 10000, 2.0)
        assert result == 20.0

    def test_score_age_exactly_4_hours_uses_1_5_multiplier(self):
        """Age == 4.0 should use 1.5 multiplier (4 to < 12 range)."""
        # (1000 / 10000) * 1.5 * 100 = 15.0
        result = calculate_viral_score(1000, 10000, 4.0)
        assert result == 15.0

    def test_score_age_exactly_12_hours_uses_1_0_multiplier(self):
        """Age == 12.0 should use 1.0 multiplier (12 to < 24 range)."""
        # (1000 / 10000) * 1.0 * 100 = 10.0
        result = calculate_viral_score(1000, 10000, 12.0)
        assert result == 10.0

    def test_score_age_exactly_24_hours_uses_0_5_multiplier(self):
        """Age == 24.0 should use 0.5 multiplier (>= 24 range)."""
        # (1000 / 10000) * 0.5 * 100 = 5.0
        result = calculate_viral_score(1000, 10000, 24.0)
        assert result == 5.0

    # --- Plan-specified edge cases ---

    def test_zero_engagement_returns_zero(self):
        """engagement=0, followers=10000, age=1.0 -> 0.0"""
        result = calculate_viral_score(0, 10000, 1.0)
        assert result == 0.0

    def test_zero_followers_returns_zero_not_division_error(self):
        """engagement=100, followers=0, age=5.0 -> 0.0 (not ZeroDivisionError)"""
        result = calculate_viral_score(100, 0, 5.0)
        assert result == 0.0

    def test_very_high_engagement_capped_at_100(self):
        """engagement=1000000, followers=1000, age=0.5 -> capped at 100.0"""
        result = calculate_viral_score(1000000, 1000, 0.5)
        assert result == 100.0

    # --- Return type ---

    def test_returns_float_not_none(self):
        """calculate_viral_score must always return a float, never None."""
        result = calculate_viral_score(500, 5000, 3.0)
        assert result is not None
        assert isinstance(result, float)

    def test_returns_float_for_zero_inputs(self):
        """Even with all zeros, return must be a float."""
        result = calculate_viral_score(0, 0, 0.0)
        assert isinstance(result, float)

    # --- Score always in range [0.0, 100.0] ---

    def test_score_minimum_is_zero(self):
        """Score is never negative."""
        result = calculate_viral_score(0, 10000, 100.0)
        assert result >= 0.0

    def test_score_maximum_is_100(self):
        """Score is never above 100."""
        result = calculate_viral_score(999999999, 1, 0.1)
        assert result <= 100.0

    # --- Viral score comparison: fast engagement > slow for same raw numbers ---

    def test_fast_engagement_higher_score_than_slow(self):
        """Fast post (< 2 hrs) scores higher than old post with identical engagement."""
        fast_score = calculate_viral_score(1000, 10000, 1.0)   # age=1h, multiplier=2.5
        slow_score = calculate_viral_score(1000, 10000, 48.0)  # age=48h, multiplier=0.5
        assert fast_score > slow_score


class TestCalculateGrowthVelocity:
    """Tests for calculate_growth_velocity(current, previous, time_delta_hours) -> float."""

    def test_basic_velocity_calculation(self):
        """(200 - 100) / 2.0 = 50.0 engagements per hour."""
        result = calculate_growth_velocity(200, 100, 2.0)
        assert result == 50.0

    def test_zero_time_delta_returns_zero(self):
        """time_delta_hours == 0 returns 0.0, not ZeroDivisionError."""
        result = calculate_growth_velocity(500, 100, 0.0)
        assert result == 0.0

    def test_no_growth_returns_zero(self):
        """Same engagement before and after returns 0.0."""
        result = calculate_growth_velocity(100, 100, 5.0)
        assert result == 0.0

    def test_decline_returns_negative(self):
        """Engagement drop returns negative velocity."""
        result = calculate_growth_velocity(50, 100, 2.0)
        assert result == -25.0

    def test_returns_float(self):
        """Return type is always float."""
        result = calculate_growth_velocity(300, 200, 4.0)
        assert isinstance(result, float)

    def test_fractional_time_delta(self):
        """Works with fractional hours."""
        # (100 - 0) / 0.5 = 200.0
        result = calculate_growth_velocity(100, 0, 0.5)
        assert result == 200.0
