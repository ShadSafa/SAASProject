"""Test suite for content categorization service."""

import pytest
from app.services.content_categorization_service import (
    categorize_content,
    ContentCategory,
    INSTAGRAM_NATIVE_TYPES,
    EXTENDED_FORMATS,
)


def test_native_type_normalization():
    """Test normalization of post types to Instagram native types"""
    result = categorize_content("Reel", "", "", 1000)
    assert result.instagram_native_type == "Reel"

    result = categorize_content("Photo", "", "", 1000)
    assert result.instagram_native_type == "Post"

    result = categorize_content("Video", "", "", 1000)
    assert result.instagram_native_type == "Video"

    result = categorize_content("Unknown", "", "", 1000)
    assert result.instagram_native_type == "Post"  # Default


def test_tutorial_format_detection():
    """Test detection of Tutorial extended format"""
    result = categorize_content(
        "Reel",
        "How to make the perfect coffee - step by step tutorial!",
        "#howto #tutorial",
        10000
    )
    assert "Tutorial" in result.extended_formats
    assert result.confidence >= 0.7


def test_comedy_format_detection():
    """Test detection of Comedy extended format"""
    result = categorize_content(
        "Reel",
        "This is so funny lol 😂",
        "#comedy #funny #humor",
        50000
    )
    assert "Comedy" in result.extended_formats


def test_multiple_formats_detected():
    """Test that multiple extended formats can be detected"""
    result = categorize_content(
        "Reel",
        "Educational fitness tutorial: learn how to do 10 pushups",
        "#fitness #tutorial #education #workout",
        20000
    )
    assert len(result.extended_formats) >= 2
    assert "Tutorial" in result.extended_formats or "Educational" in result.extended_formats
    assert "Fitness" in result.extended_formats


def test_no_keywords_low_confidence():
    """Test generic post with no format keywords has lower confidence"""
    result = categorize_content("Post", "Check this out", "", 1000)
    assert result.extended_formats == []
    assert result.confidence < 0.5


def test_rich_caption_high_confidence():
    """Test rich description with keywords has higher confidence"""
    long_caption = (
        "This comprehensive tutorial shows you step by step how to create the perfect "
        "Instagram reels for your audience. We'll walk through the entire filming process, "
        "including lighting setup, camera angles, and editing techniques that professionals use."
    )
    result = categorize_content(
        "Video",
        long_caption,
        "#tutorial #howto",
        100000
    )
    assert result.confidence > 0.75


def test_content_category_model_validation():
    """Test ContentCategory Pydantic model validates correctly"""
    category = ContentCategory(
        instagram_native_type="Reel",
        extended_formats=["Tutorial", "Educational"],
        confidence=0.85,
        reason="Post is Reel with Tutorial and Educational formats"
    )
    assert category.instagram_native_type == "Reel"
    assert len(category.extended_formats) == 2
    assert 0.0 <= category.confidence <= 1.0
