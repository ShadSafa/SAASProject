"""Test suite for OpenAI service with mocked API responses."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.services.openai_service import analyze_viral_post, ViralAnalysisResult
from app.models.viral_post import ViralPost


@pytest.fixture
def mock_viral_post():
    """Create a mock ViralPost with realistic data."""
    return ViralPost(
        id=1,
        scan_id=1,
        instagram_post_id="12345678901234567",
        instagram_url="https://instagram.com/p/ABC123/",
        post_type="Reel",
        caption="Check out this amazing travel hack! #travel #tips #viral",
        hashtags="travel,tips,viral,hacks,wanderlust",
        thumbnail_url="https://instagram.com/thumbnail.jpg",
        thumbnail_s3_url="https://s3.amazonaws.com/bucket/thumbnail.jpg",
        creator_username="travel_influencer",
        creator_follower_count=500000,
        likes_count=125000,
        comments_count=5200,
        saves_count=45000,
        shares_count=8900,
        post_age_hours=12.5,
        viral_score=87.5,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def mock_analysis_response():
    """Create a mock ViralAnalysisResult."""
    return ViralAnalysisResult(
        why_viral_summary="This travel hack resonates with wanderlust audiences and provides immediate value. The hook captures attention in the first 3 seconds, and the emotional trigger (awe) combined with practical utility drives high engagement.",
        posting_time_score=85.0,
        hook_strength=92.0,
        emotional_trigger="awe",
        engagement_velocity_score=88.0,
        save_share_ratio_score=91.0,
        hashtag_performance=78.0,
        audience_retention=84.0,
        confidence_score=0.92
    )


def test_analyze_viral_post_success(mock_viral_post, mock_analysis_response):
    """Test successful OpenAI API call returns ViralAnalysisResult."""
    with patch("app.services.openai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        with patch("app.services.openai_service.OpenAI") as mock_openai:
            # Setup mock OpenAI response
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_message = MagicMock()
            mock_message.parsed = mock_analysis_response
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_client.beta.chat.completions.parse.return_value = mock_response

            # Call the function
            result = analyze_viral_post(mock_viral_post)

            # Verify result
            assert isinstance(result, ViralAnalysisResult)
            assert result.why_viral_summary == mock_analysis_response.why_viral_summary
            assert result.posting_time_score == 85.0
            assert result.hook_strength == 92.0
            assert result.emotional_trigger == "awe"

            # Verify API was called with correct model
            mock_client.beta.chat.completions.parse.assert_called_once()
            call_args = mock_client.beta.chat.completions.parse.call_args
            assert call_args.kwargs["model"] == "gpt-4o"
            assert call_args.kwargs["response_format"] == ViralAnalysisResult


def test_analyze_viral_post_validates_schema(mock_viral_post, mock_analysis_response):
    """Verify all required fields present in ViralAnalysisResult."""
    with patch("app.services.openai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        with patch("app.services.openai_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_message = MagicMock()
            mock_message.parsed = mock_analysis_response
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_client.beta.chat.completions.parse.return_value = mock_response

            result = analyze_viral_post(mock_viral_post)

            # Verify all required fields are present
            required_fields = [
                "why_viral_summary",
                "posting_time_score",
                "hook_strength",
                "emotional_trigger",
                "engagement_velocity_score",
                "save_share_ratio_score",
                "hashtag_performance",
                "audience_retention",
                "confidence_score"
            ]

            for field in required_fields:
                assert hasattr(result, field), f"Missing field: {field}"
                assert getattr(result, field) is not None, f"Field {field} is None"


def test_analyze_viral_post_handles_api_error(mock_viral_post):
    """Verify HTTPException raised on OpenAI API error."""
    with patch("app.services.openai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        with patch("app.services.openai_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            # Mock a generic exception to test error handling path
            mock_client.beta.chat.completions.parse.side_effect = Exception("API Error")

            with pytest.raises(HTTPException) as exc_info:
                analyze_viral_post(mock_viral_post)

            assert exc_info.value.status_code == 500
            assert "error" in exc_info.value.detail.lower()


def test_scores_within_bounds(mock_viral_post, mock_analysis_response):
    """Verify all factor scores are 0.0 <= score <= 100.0."""
    with patch("app.services.openai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        with patch("app.services.openai_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_message = MagicMock()
            mock_message.parsed = mock_analysis_response
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_client.beta.chat.completions.parse.return_value = mock_response

            result = analyze_viral_post(mock_viral_post)

            # Check score bounds for all 7 algorithm factors
            score_fields = [
                "posting_time_score",
                "hook_strength",
                "engagement_velocity_score",
                "save_share_ratio_score",
                "hashtag_performance",
                "audience_retention"
            ]

            for field in score_fields:
                score = getattr(result, field)
                assert 0.0 <= score <= 100.0, f"{field} out of bounds: {score}"


def test_confidence_within_bounds(mock_viral_post, mock_analysis_response):
    """Verify confidence_score is 0.0 <= score <= 1.0."""
    with patch("app.services.openai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        with patch("app.services.openai_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_message = MagicMock()
            mock_message.parsed = mock_analysis_response
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_client.beta.chat.completions.parse.return_value = mock_response

            result = analyze_viral_post(mock_viral_post)

            # Check confidence bounds
            assert 0.0 <= result.confidence_score <= 1.0, f"confidence_score out of bounds: {result.confidence_score}"
