"""Tests for Analysis model audience demographics fields.

Tests verify that new Phase 05 fields (audience_demographics, engagement_rate,
audience_interests) can be stored and retrieved from the database.
"""
import pytest
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.models.scan import Scan
from app.models.user import User


def test_analysis_model_has_audience_demographics_field(db_session):
    """Verify Analysis model supports audience_demographics JSON field."""
    # Create required parent records
    user = User(email="test@example.com", hashed_password="hashed", email_verified=True)
    db_session.add(user)
    db_session.flush()

    scan = Scan(user_id=user.id, scan_type="trending", time_range="24h", status="completed")
    db_session.add(scan)
    db_session.flush()

    post = ViralPost(
        scan_id=scan.id,
        instagram_post_id="123",
        creator_username="test",
        post_type="Photo"
    )
    db_session.add(post)
    db_session.flush()

    # Create Analysis with audience_demographics
    analysis = Analysis(
        viral_post_id=post.id,
        audience_demographics={
            "age_range": {"18-24": 25, "25-34": 45},
            "gender_distribution": {"male": 40, "female": 60},
            "top_countries": [
                {"code": "US", "percentage": 45},
                {"code": "GB", "percentage": 12}
            ]
        }
    )
    db_session.add(analysis)
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.query(Analysis).first()
    assert retrieved.audience_demographics is not None
    assert "age_range" in retrieved.audience_demographics
    assert "gender_distribution" in retrieved.audience_demographics
    assert "top_countries" in retrieved.audience_demographics
    assert retrieved.audience_demographics["age_range"]["18-24"] == 25
    assert retrieved.audience_demographics["gender_distribution"]["male"] == 40


def test_analysis_model_has_engagement_rate_field(db_session):
    """Verify Analysis model supports engagement_rate Float field."""
    # Create required parent records
    user = User(email="test2@example.com", hashed_password="hashed", email_verified=True)
    db_session.add(user)
    db_session.flush()

    scan = Scan(user_id=user.id, scan_type="trending", time_range="24h", status="completed")
    db_session.add(scan)
    db_session.flush()

    post = ViralPost(
        scan_id=scan.id,
        instagram_post_id="456",
        creator_username="test2",
        post_type="Reel"
    )
    db_session.add(post)
    db_session.flush()

    # Create Analysis with engagement_rate
    analysis = Analysis(
        viral_post_id=post.id,
        engagement_rate=4.5  # 4.5% engagement
    )
    db_session.add(analysis)
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.query(Analysis).first()
    assert retrieved.engagement_rate is not None
    assert retrieved.engagement_rate == 4.5
    assert isinstance(retrieved.engagement_rate, float)


def test_analysis_model_has_audience_interests_field(db_session):
    """Verify Analysis model supports audience_interests JSON field."""
    # Create required parent records
    user = User(email="test3@example.com", hashed_password="hashed", email_verified=True)
    db_session.add(user)
    db_session.flush()

    scan = Scan(user_id=user.id, scan_type="trending", time_range="24h", status="completed")
    db_session.add(scan)
    db_session.flush()

    post = ViralPost(
        scan_id=scan.id,
        instagram_post_id="789",
        creator_username="test3",
        post_type="Video"
    )
    db_session.add(post)
    db_session.flush()

    # Create Analysis with audience_interests
    analysis = Analysis(
        viral_post_id=post.id,
        audience_interests={
            "inferred_topics": ["fitness", "wellness"],
            "content_affinity": ["educational", "inspirational"],
            "hashtag_analysis": ["#fitnessmotivation", "#healthylifestyle"]
        }
    )
    db_session.add(analysis)
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.query(Analysis).first()
    assert retrieved.audience_interests is not None
    assert "inferred_topics" in retrieved.audience_interests
    assert "content_affinity" in retrieved.audience_interests
    assert "hashtag_analysis" in retrieved.audience_interests
    assert "fitness" in retrieved.audience_interests["inferred_topics"]
    assert "educational" in retrieved.audience_interests["content_affinity"]
