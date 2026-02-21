"""Tests for analysis enrichment integration."""

import pytest
from app.models.analysis import Analysis
from app.models.viral_post import ViralPost
from app.services.analysis_enrichment_service import (
    enrich_analysis_with_metrics,
    enrich_analysis_with_categorization,
    enrich_analysis_with_niche,
    enrich_analysis_complete,
)


@pytest.fixture
def mock_viral_post():
    """Create a mock viral post for testing."""
    return ViralPost(
        id=1,
        instagram_post_id="test_post_123",
        creator_username="test_creator",
        creator_follower_count=10000,
        likes_count=500,
        comments_count=100,
        saves_count=75,
        shares_count=25,
        post_type="Reel",
        caption="How to make the perfect tutorial",
        hashtags="#tutorial #howto #educational",
    )


@pytest.fixture
def mock_analysis():
    """Create a mock analysis for testing."""
    return Analysis(
        id=1,
        viral_post_id=1,
        why_viral_summary="Test summary",
        posting_time_score=85.0,
        hook_strength_score=90.0,
        engagement_velocity_score=80.0,
        save_share_ratio_score=75.0,
        hashtag_performance_score=70.0,
        audience_retention_score=85.0,
        emotional_trigger="joy",
        confidence_score=0.92,
    )


@pytest.mark.asyncio
async def test_enrich_analysis_with_engagement_rate(mock_viral_post, mock_analysis):
    """Test enrichment adds engagement rate to analysis."""
    mock_viral_post.creator_follower_count = 50000
    mock_viral_post.likes_count = 600
    mock_viral_post.comments_count = 200
    mock_viral_post.saves_count = 150
    mock_viral_post.shares_count = 50

    assert mock_analysis.engagement_rate is None

    await enrich_analysis_with_metrics(mock_analysis, mock_viral_post)

    assert mock_analysis.engagement_rate == 2.0  # (1000 / 50000) * 100


@pytest.mark.asyncio
async def test_enrich_analysis_with_categorization(mock_viral_post, mock_analysis):
    """Test enrichment adds content categorization to analysis."""
    mock_viral_post.post_type = "Reel"
    mock_viral_post.caption = "How to make the perfect tutorial"
    mock_viral_post.hashtags = "#tutorial #howto"

    assert mock_analysis.content_category is None

    await enrich_analysis_with_categorization(mock_analysis, mock_viral_post)

    assert mock_analysis.content_category == "Reel"
    assert "Tutorial" in mock_analysis.audience_interests.get("inferred_formats", [])


@pytest.mark.asyncio
async def test_enrich_analysis_complete_runs_all_steps(mock_viral_post, mock_analysis):
    """Test enrich_analysis_complete runs all enrichment steps."""
    mock_viral_post.creator_follower_count = 10000
    mock_viral_post.likes_count = 100
    mock_viral_post.comments_count = 50
    mock_viral_post.saves_count = 30
    mock_viral_post.shares_count = 20
    mock_viral_post.post_type = "Video"
    mock_viral_post.caption = "Tutorial for beginners"

    await enrich_analysis_complete(mock_analysis, mock_viral_post)

    assert mock_analysis.engagement_rate is not None
    assert mock_analysis.content_category is not None
    assert mock_analysis.audience_interests is not None


@pytest.mark.asyncio
async def test_enrichment_handles_missing_data(mock_viral_post, mock_analysis):
    """Test enrichment handles missing post data gracefully."""
    # Minimal viral post data
    mock_viral_post.creator_follower_count = 0
    mock_viral_post.likes_count = 0
    mock_viral_post.comments_count = 0
    mock_viral_post.saves_count = 0
    mock_viral_post.shares_count = 0
    mock_viral_post.post_type = None
    mock_viral_post.caption = None
    mock_viral_post.hashtags = None

    # Should not raise, should handle gracefully
    await enrich_analysis_complete(mock_analysis, mock_viral_post)

    assert mock_analysis.engagement_rate == 0.0
    assert mock_analysis.content_category == "Post"  # Default


@pytest.mark.asyncio
async def test_enrichment_preserves_openai_fields(mock_viral_post, mock_analysis):
    """Test enrichment doesn't overwrite existing OpenAI fields."""
    # Pre-populate OpenAI fields
    mock_analysis.why_viral_summary = "Original summary"
    mock_analysis.posting_time_score = 85.0
    mock_analysis.confidence_score = 0.92

    await enrich_analysis_complete(mock_analysis, mock_viral_post)

    # OpenAI fields should be unchanged
    assert mock_analysis.why_viral_summary == "Original summary"
    assert mock_analysis.posting_time_score == 85.0
    assert mock_analysis.confidence_score == 0.92

    # Enrichment fields should be populated
    assert mock_analysis.engagement_rate is not None
    assert mock_analysis.content_category is not None


@pytest.mark.asyncio
async def test_enrich_analysis_with_niche(mock_viral_post, mock_analysis, mocker):
    """Test enrichment adds AI-detected niche to analysis"""
    from app.services.niche_detection_service import NicheDetectionResult

    mock_viral_post.caption = "Amazing fitness workout routine"
    mock_viral_post.hashtags = '["fitness", "gym", "workout"]'
    mock_viral_post.post_type = "Reel"

    # Mock niche detection
    mock_niche = NicheDetectionResult(
        primary_niche="Fitness & Wellness",
        secondary_niche=None,
        confidence=0.92,
        reasoning="Post contains fitness hashtags and workout content",
        keywords=["fitness", "gym", "workout"]
    )

    mocker.patch(
        "app.services.niche_detection_service.detect_niche",
        return_value=mock_niche
    )

    assert mock_analysis.niche is None

    await enrich_analysis_with_niche(mock_analysis, mock_viral_post)

    assert mock_analysis.niche == "Fitness & Wellness"
    assert mock_analysis.audience_interests["niche"] == "Fitness & Wellness"
    assert mock_analysis.audience_interests["niche_confidence"] == 0.92


@pytest.mark.asyncio
async def test_enrich_analysis_complete_with_niche(mock_viral_post, mock_analysis, mocker):
    """Test full enrichment includes niche detection as final step"""
    from app.services.niche_detection_service import NicheDetectionResult

    mock_viral_post.creator_follower_count = 100000
    mock_viral_post.likes_count = 500
    mock_viral_post.comments_count = 200
    mock_viral_post.saves_count = 100
    mock_viral_post.shares_count = 50
    mock_viral_post.post_type = "Reel"
    mock_viral_post.caption = "Fashion styling tips"
    mock_viral_post.hashtags = '["fashion", "style"]'

    mock_niche = NicheDetectionResult(
        primary_niche="Fashion & Styling",
        secondary_niche=None,
        confidence=0.88,
        reasoning="Fashion-related hashtags and styling content",
        keywords=["fashion", "style"]
    )

    mocker.patch(
        "app.services.niche_detection_service.detect_niche",
        return_value=mock_niche
    )

    await enrich_analysis_complete(mock_analysis, mock_viral_post)

    # All enrichment steps should be completed
    assert abs(mock_analysis.engagement_rate - 0.85) < 0.01  # 850/100000 * 100
    assert mock_analysis.content_category == "Reel"
    assert mock_analysis.niche == "Fashion & Styling"
    assert "inferred_formats" in mock_analysis.audience_interests


@pytest.mark.asyncio
async def test_niche_enrichment_handles_api_failure(mock_viral_post, mock_analysis, mocker):
    """Test niche enrichment falls back gracefully if API fails"""

    # Mock niche detection to fail (returns fallback)
    mocker.patch(
        "app.services.niche_detection_service.detect_niche",
        side_effect=Exception("API Error")
    )

    await enrich_analysis_with_niche(mock_analysis, mock_viral_post)

    # Should not crash, should set niche to fallback
    assert mock_analysis.niche == "Other"
    # Analysis should still be usable
    assert mock_analysis.viral_post_id is not None
