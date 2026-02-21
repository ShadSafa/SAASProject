"""Test suite for niche detection service."""

import pytest
from app.services.niche_detection_service import (
    NicheDetectionResult,
    NICHE_OPTIONS,
    detect_niche,
    _classify_creator_size
)


def test_niche_detection_result_model():
    """Test NicheDetectionResult Pydantic model validates correctly"""
    result = NicheDetectionResult(
        primary_niche="Fitness & Wellness",
        secondary_niche="Health & Wellness",
        confidence=0.85,
        reasoning="Post contains fitness hashtags and workout content",
        keywords=["fitness", "gym", "workout", "health"]
    )
    assert result.primary_niche in NICHE_OPTIONS
    assert result.confidence == 0.85
    assert len(result.keywords) > 0


def test_niche_options_comprehensive():
    """Test that niche options list is comprehensive"""
    # Should have at least 25 niches
    assert len(NICHE_OPTIONS) >= 25

    # Should include major categories
    assert "Fitness & Wellness" in NICHE_OPTIONS
    assert "Fashion & Styling" in NICHE_OPTIONS
    assert "Technology & Gadgets" in NICHE_OPTIONS
    assert "Food & Cooking" in NICHE_OPTIONS
    assert "Business & Entrepreneurship" in NICHE_OPTIONS


def test_niche_detection_result_validation():
    """Test that NicheDetectionResult validates confidence bounds"""
    # Valid confidence
    result = NicheDetectionResult(
        primary_niche="Fitness & Wellness",
        confidence=0.5,
        reasoning="Medium confidence",
        keywords=[]
    )
    assert 0.0 <= result.confidence <= 1.0

    # Invalid confidence should raise validation error
    with pytest.raises(ValueError):
        NicheDetectionResult(
            primary_niche="Fitness & Wellness",
            confidence=1.5,  # Out of bounds
            reasoning="Invalid",
            keywords=[]
        )


@pytest.mark.asyncio
async def test_niche_detection_with_mock_openai(mocker):
    """Test niche detection with mocked OpenAI response"""
    # Mock OpenAI response
    mock_result = NicheDetectionResult(
        primary_niche="Fitness & Wellness",
        secondary_niche=None,
        confidence=0.92,
        reasoning="Post contains fitness hashtags and workout tips",
        keywords=["fitness", "gym", "workout"]
    )

    mock_parse = mocker.patch(
        "app.services.niche_detection_service._get_client",
        return_value=mocker.MagicMock(
            beta=mocker.MagicMock(
                chat=mocker.MagicMock(
                    completions=mocker.MagicMock(
                        parse=mocker.MagicMock(
                            return_value=mocker.MagicMock(
                                choices=[
                                    mocker.MagicMock(
                                        message=mocker.MagicMock(parsed=mock_result)
                                    )
                                ]
                            )
                        )
                    )
                )
            )
        )
    )

    result = await detect_niche(
        caption="Amazing workout routine for beginners",
        hashtags='["fitness", "gym", "workout"]',
        extended_formats=["Tutorial", "Educational"],
        content_type="Reel",
        creator_follower_count=50000
    )

    assert result.primary_niche == "Fitness & Wellness"
    assert result.confidence == 0.92
    mock_parse.assert_called_once()


@pytest.mark.asyncio
async def test_niche_detection_fallback_on_error(mocker):
    """Test niche detection gracefully falls back to 'Other' on API error"""
    # Mock OpenAI to raise error
    mocker.patch(
        "app.services.niche_detection_service._get_client",
        side_effect=Exception("API Error")
    )

    result = await detect_niche(
        caption="Some caption",
        hashtags="",
        extended_formats=None,
        content_type="Post",
        creator_follower_count=1000
    )

    # Should return fallback "Other" niche
    assert result.primary_niche == "Other"
    assert result.confidence < 0.5


def test_creator_size_classification():
    """Test creator size classification for prompt context"""
    assert "Micro-creator" in _classify_creator_size(500)
    assert "Small creator" in _classify_creator_size(5000)
    assert "Medium creator" in _classify_creator_size(50000)
    assert "Macro-creator" in _classify_creator_size(500000)
    assert "Mega-creator" in _classify_creator_size(5000000)
