"""Test suite for analysis background tasks with mocked dependencies."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime

from app.tasks.analysis_jobs import analyze_posts_batch
from app.services.openai_service import ViralAnalysisResult as OpenAIResult


@pytest.fixture
def mock_viral_posts():
    """Create mock ViralPost objects for testing."""
    posts = []
    for i in range(3):
        post = MagicMock()
        post.id = i + 1
        post.scan_id = 1
        post.instagram_post_id = f"180000000000000{i+1}"
        post.instagram_url = f"https://instagram.com/p/ABC{i+1}/"
        post.post_type = "Reel" if i == 0 else "Photo"
        post.caption = f"Test caption {i+1} #viral #trending"
        post.hashtags = '["viral", "trending"]'
        post.creator_username = f"creator_{i+1}"
        post.creator_follower_count = 100000 * (i + 1)
        post.likes_count = 10000 * (i + 1)
        post.comments_count = 1000 * (i + 1)
        post.saves_count = 5000 * (i + 1)
        post.shares_count = 2000 * (i + 1)
        post.post_age_hours = 12.0 + i
        post.viral_score = 75.0 + i * 5
        post.created_at = datetime.utcnow()
        posts.append(post)
    return posts


@pytest.fixture
def mock_openai_result():
    """Create a mock ViralAnalysisResult from OpenAI service."""
    return OpenAIResult(
        why_viral_summary="This post resonates with audiences through emotional hooks and engagement velocity.",
        posting_time_score=82.0,
        hook_strength=88.0,
        emotional_trigger="joy",
        engagement_velocity_score=85.0,
        save_share_ratio_score=90.0,
        hashtag_performance=78.0,
        audience_retention=86.0,
        confidence_score=0.91
    )


@pytest.fixture
def mock_cache_result():
    """Create a mock cached analysis result (from cache_service.ViralAnalysisResult)."""
    result = MagicMock()
    result.why_viral_summary = "Cached analysis summary"
    result.hook_strength = "85.0"
    result.emotional_trigger = "awe"
    result.posting_time_score = 80.0
    result.engagement_velocity = 82.0
    result.save_share_ratio = 88.0
    result.hashtag_performance = {"score": 75.0}
    result.audience_demographics = {"score": 84.0}
    result.content_category = "travel"
    result.niche = "travel_influencers"
    return result


def test_analyze_posts_batch_registered():
    """Verify task name is registered correctly."""
    assert analyze_posts_batch.name == "analysis.analyze_posts_batch"


def test_analyze_posts_batch_all_cache_hits(mock_cache_result):
    """Test batch where all posts are found in cache."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.get_cached_analysis") as mock_get_cache:
        with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
            # Mock all cache hits
            mock_get_cache.side_effect = [mock_cache_result, mock_cache_result, mock_cache_result]

            # Mock _run_analysis to return expected results
            mock_asyncio.return_value = {"analyzed": 0, "cached": 3, "failed": 0}

            result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

            # Verify result
            assert result["cached"] == 3
            assert result["analyzed"] == 0
            assert result["failed"] == 0


def test_analyze_posts_batch_all_cache_misses(mock_openai_result):
    """Test batch where no posts are cached (all call OpenAI)."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.get_cached_analysis") as mock_get_cache:
        with patch("app.tasks.analysis_jobs.analyze_viral_post") as mock_openai:
            with patch("app.tasks.analysis_jobs.cache_analysis") as mock_cache:
                with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
                    # Mock all cache misses
                    mock_get_cache.return_value = None

                    # Mock OpenAI returns
                    mock_openai.return_value = mock_openai_result

                    # Mock _run_analysis
                    mock_asyncio.return_value = {"analyzed": 3, "cached": 0, "failed": 0}

                    result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

                    # Verify result
                    assert result["analyzed"] == 3
                    assert result["cached"] == 0
                    assert result["failed"] == 0


def test_analyze_posts_batch_mixed_cache_hits_and_misses(mock_openai_result, mock_cache_result):
    """Test batch with mixed cache hits and misses."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.get_cached_analysis") as mock_get_cache:
        with patch("app.tasks.analysis_jobs.analyze_viral_post") as mock_openai:
            with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
                # Mock 2 cache hits, 1 miss
                mock_get_cache.side_effect = [mock_cache_result, mock_cache_result, None]

                # Mock OpenAI result
                mock_openai.return_value = mock_openai_result

                # Mock _run_analysis
                mock_asyncio.return_value = {"analyzed": 1, "cached": 2, "failed": 0}

                result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

                # Verify result
                assert result["analyzed"] == 1
                assert result["cached"] == 2
                assert result["failed"] == 0


def test_analyze_posts_batch_handles_openai_error(mock_cache_result):
    """Test batch gracefully handles OpenAI error for one post."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.get_cached_analysis") as mock_get_cache:
        with patch("app.tasks.analysis_jobs.analyze_viral_post") as mock_openai:
            with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
                # Post 1: cache hit
                # Post 2: OpenAI error
                # Post 3: cache hit
                mock_get_cache.side_effect = [mock_cache_result, None, mock_cache_result]

                # Mock OpenAI error for post 2
                mock_openai.side_effect = Exception("OpenAI API Error")

                # Mock _run_analysis: 1 analyzed, 2 cached, but 1 failed (post 2 error)
                mock_asyncio.return_value = {"analyzed": 0, "cached": 2, "failed": 1}

                result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

                # Verify result - batch completed despite error
                assert result["cached"] == 2
                assert result["failed"] == 1


def test_analyze_posts_batch_empty_list():
    """Test batch with empty list returns zeros."""
    viral_post_ids = []

    with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
        mock_asyncio.return_value = {"analyzed": 0, "cached": 0, "failed": 0}

        result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

        assert result["analyzed"] == 0
        assert result["cached"] == 0
        assert result["failed"] == 0


def test_analyze_posts_batch_task_failure_returns_failed_count():
    """Test task failure is handled gracefully."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
        # Mock _run_analysis to raise exception
        mock_asyncio.side_effect = Exception("Database connection error")

        result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

        # Task returns failed count
        assert result["analyzed"] == 0
        assert result["cached"] == 0
        assert result["failed"] == 3


def test_analyze_posts_batch_result_schema():
    """Verify result dict has required keys."""
    viral_post_ids = [1, 2, 3]

    with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
        mock_asyncio.return_value = {"analyzed": 2, "cached": 1, "failed": 0}

        result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

        # Verify required keys present
        assert "analyzed" in result
        assert "cached" in result
        assert "failed" in result
        assert isinstance(result["analyzed"], int)
        assert isinstance(result["cached"], int)
        assert isinstance(result["failed"], int)


def test_analyze_posts_batch_large_batch():
    """Test batch processing many posts (stress test)."""
    viral_post_ids = list(range(1, 51))  # 50 posts

    with patch("app.tasks.analysis_jobs.asyncio.run") as mock_asyncio:
        mock_asyncio.return_value = {"analyzed": 30, "cached": 20, "failed": 0}

        result = analyze_posts_batch(scan_id=1, viral_post_ids=viral_post_ids)

        assert result["analyzed"] + result["cached"] + result["failed"] == 50
