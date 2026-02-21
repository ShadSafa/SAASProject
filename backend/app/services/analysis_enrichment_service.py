"""
Service for enriching Analysis records with engagement metrics and content categorization.

Integrates engagement_service and content_categorization_service into analysis workflow.
Called after OpenAI analysis to populate optional/computed fields.
"""

import logging
from app.models import Analysis, ViralPost
from app.services.engagement_service import calculate_engagement_rate
from app.services.content_categorization_service import categorize_content

logger = logging.getLogger(__name__)


async def enrich_analysis_with_metrics(
    analysis: Analysis,
    viral_post: ViralPost
) -> None:
    """
    Enrich analysis record with engagement metrics.

    Updates analysis.engagement_rate with calculated engagement metric.

    Args:
        analysis: Analysis ORM object to update
        viral_post: Related ViralPost ORM object with engagement data
    """
    try:
        metrics = calculate_engagement_rate(viral_post)
        analysis.engagement_rate = metrics.engagement_rate
        logger.info(
            f"Enriched analysis {analysis.id} with engagement rate {metrics.engagement_rate:.2f}%"
        )
    except Exception as e:
        logger.error(f"Failed to calculate engagement rate for post {viral_post.id}: {str(e)}")
        # Don't raise — optional enrichment failure shouldn't fail entire analysis
        analysis.engagement_rate = None


async def enrich_analysis_with_categorization(
    analysis: Analysis,
    viral_post: ViralPost
) -> None:
    """
    Enrich analysis record with content categorization.

    Updates analysis fields:
    - content_category: Instagram native type (Reel, Post, Story, etc.)
    - audience_interests: Extended formats as inferred topics

    Args:
        analysis: Analysis ORM object to update
        viral_post: Related ViralPost ORM object with content metadata
    """
    try:
        categorization = categorize_content(
            post_type=viral_post.post_type or "Post",
            caption=viral_post.caption,
            hashtags=viral_post.hashtags,
            creator_follower_count=viral_post.creator_follower_count
        )

        # Store native type
        analysis.content_category = categorization.instagram_native_type

        # Store extended formats as inferred topics in audience_interests
        if not analysis.audience_interests:
            analysis.audience_interests = {}

        analysis.audience_interests["inferred_formats"] = categorization.extended_formats
        analysis.audience_interests["categorization_confidence"] = categorization.confidence
        analysis.audience_interests["categorization_reason"] = categorization.reason

        logger.info(
            f"Enriched analysis {analysis.id} with categorization: "
            f"{categorization.instagram_native_type}, formats: {categorization.extended_formats}"
        )
    except Exception as e:
        logger.error(f"Failed to categorize post {viral_post.id}: {str(e)}")
        # Don't raise — optional enrichment failure shouldn't fail entire analysis
        analysis.content_category = viral_post.post_type or "Post"


async def enrich_analysis_with_niche(
    analysis: Analysis,
    viral_post: ViralPost
) -> None:
    """
    Enrich analysis record with AI-detected niche.

    Updates analysis.niche with detected primary niche.

    Args:
        analysis: Analysis ORM object to update
        viral_post: Related ViralPost ORM object
    """
    try:
        from app.services.niche_detection_service import detect_niche

        # Get extended formats from audience_interests if available
        extended_formats = None
        if analysis.audience_interests and "inferred_formats" in analysis.audience_interests:
            extended_formats = analysis.audience_interests["inferred_formats"]

        niche_result = await detect_niche(
            caption=viral_post.caption,
            hashtags=viral_post.hashtags,
            extended_formats=extended_formats,
            content_type=viral_post.post_type,
            creator_follower_count=viral_post.creator_follower_count
        )

        analysis.niche = niche_result.primary_niche

        # Store niche confidence and reasoning in audience_interests
        if not analysis.audience_interests:
            analysis.audience_interests = {}

        analysis.audience_interests["niche"] = niche_result.primary_niche
        analysis.audience_interests["niche_secondary"] = niche_result.secondary_niche
        analysis.audience_interests["niche_confidence"] = niche_result.confidence
        analysis.audience_interests["niche_reasoning"] = niche_result.reasoning
        analysis.audience_interests["niche_keywords"] = niche_result.keywords

        logger.info(
            f"Enriched analysis {analysis.id} with niche: {niche_result.primary_niche} "
            f"(confidence: {niche_result.confidence:.2f})"
        )
    except Exception as e:
        logger.error(f"Failed to detect niche for post {viral_post.id}: {str(e)}")
        # Don't raise — optional enrichment failure shouldn't fail entire analysis
        analysis.niche = "Other"


async def enrich_analysis_complete(
    analysis: Analysis,
    viral_post: ViralPost
) -> None:
    """
    Run all enrichment steps on analysis record.

    Called after OpenAI analysis to populate optional/computed fields:
    1. Engagement metrics
    2. Content categorization
    3. Niche detection

    Args:
        analysis: Analysis ORM object to enrich
        viral_post: Related ViralPost ORM object
    """
    await enrich_analysis_with_metrics(analysis, viral_post)
    await enrich_analysis_with_categorization(analysis, viral_post)
    await enrich_analysis_with_niche(analysis, viral_post)
