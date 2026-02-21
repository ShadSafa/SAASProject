"""
Celery background tasks for AI-powered viral post analysis.

Analysis tasks run in background worker, checking cache first before
calling OpenAI API. Results stored in both PostgreSQL and Redis cache.
"""
import asyncio
import logging
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.services.openai_service import analyze_viral_post, ViralAnalysisResult
from app.services.cache_service import get_cached_analysis, cache_analysis

logger = logging.getLogger(__name__)


@celery_app.task(name="analysis.analyze_posts_batch")
def analyze_posts_batch(scan_id: int, viral_post_ids: List[int]) -> Dict[str, int]:
    """
    Celery task: Analyze batch of viral posts with cache-first strategy.

    For each viral post:
    1. Check Redis cache first
    2. If cached: create Analysis record from cache, skip OpenAI call
    3. If not cached: fetch from DB, call OpenAI, store result in DB and cache
    4. Per-post error handling prevents batch failure from single post error

    Args:
        scan_id: ID of the Scan record containing these posts
        viral_post_ids: List of ViralPost IDs to analyze

    Returns:
        dict with counts: {"analyzed": int, "cached": int, "failed": int}
    """
    try:
        # Handle event loop properly for Celery workers
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_run_analysis(scan_id, viral_post_ids))
        return result
    except Exception as exc:
        logger.error(f"analyze_posts_batch failed for scan_id={scan_id}: {exc}", exc_info=True)
        # Task completes successfully even on error; errors are logged
        return {"analyzed": 0, "cached": 0, "failed": len(viral_post_ids)}


async def _run_analysis(scan_id: int, viral_post_ids: List[int]) -> Dict[str, int]:
    """Async implementation of analysis logic using SQLAlchemy async session."""
    from app.database import AsyncSessionLocal
    from app.models.viral_post import ViralPost
    from app.models.analysis import Analysis

    analyzed_count = 0
    cached_count = 0
    failed_count = 0

    async with AsyncSessionLocal() as db:
        for post_id in viral_post_ids:
            try:
                # Check cache first (avoids expensive OpenAI call)
                cached_result = get_cached_analysis(post_id)

                if cached_result:
                    # Cache hit: create Analysis record from cached data
                    logger.info(f"Cache hit for viral_post_id={post_id}")
                    # Extract scalar value from JSON demographic object for audience_retention_score
                    audience_score = cached_result.audience_demographics.get("score") if isinstance(cached_result.audience_demographics, dict) else cached_result.audience_demographics
                    analysis = Analysis(
                        viral_post_id=post_id,
                        why_viral_summary=cached_result.why_viral_summary,
                        hook_strength_score=float(cached_result.hook_strength),
                        emotional_trigger=cached_result.emotional_trigger,
                        posting_time_score=cached_result.posting_time_score,
                        engagement_velocity_score=cached_result.engagement_velocity,
                        save_share_ratio_score=cached_result.save_share_ratio,
                        hashtag_performance_score=cached_result.hashtag_performance,
                        audience_retention_score=float(audience_score) if audience_score else None,
                        content_category=cached_result.content_category,
                        niche=cached_result.niche,
                    )
                    db.add(analysis)
                    cached_count += 1
                    continue

                # Cache miss: fetch viral_post from DB
                viral_post = await db.get(ViralPost, post_id)
                if not viral_post:
                    logger.warning(f"ViralPost {post_id} not found in DB")
                    failed_count += 1
                    continue

                # Call OpenAI (expensive 2-5s API call)
                logger.info(f"Calling OpenAI for viral_post_id={post_id}")
                openai_result = analyze_viral_post(viral_post)

                # Store in DB
                analysis = Analysis(
                    viral_post_id=post_id,
                    why_viral_summary=openai_result.why_viral_summary,
                    hook_strength_score=openai_result.hook_strength,
                    emotional_trigger=openai_result.emotional_trigger,
                    posting_time_score=openai_result.posting_time_score,
                    engagement_velocity_score=openai_result.engagement_velocity_score,
                    save_share_ratio_score=openai_result.save_share_ratio_score,
                    hashtag_performance_score=openai_result.hashtag_performance,
                    audience_retention_score=openai_result.audience_retention,
                    content_category=None,  # Not provided by analysis result
                    niche=None,  # Not provided by analysis result
                )
                db.add(analysis)

                # Store in cache (7-day TTL)
                # Convert ViralAnalysisResult to cache-compatible format
                from app.services.cache_service import ViralAnalysisResult as CacheResult
                cache_obj = CacheResult(
                    viral_post_id=post_id,
                    why_viral_summary=openai_result.why_viral_summary,
                    hook_strength=str(openai_result.hook_strength),
                    emotional_trigger=openai_result.emotional_trigger,
                    posting_time_score=openai_result.posting_time_score,
                    engagement_velocity=openai_result.engagement_velocity_score,
                    save_share_ratio=openai_result.save_share_ratio_score,
                    hashtag_performance={"score": openai_result.hashtag_performance},
                    audience_demographics={"score": openai_result.audience_retention},
                    content_category=None,
                    niche=None,
                )
                cache_analysis(post_id, cache_obj)
                analyzed_count += 1

            except Exception as exc:
                # Per-post error handling: log and continue to next post
                logger.error(f"Analysis failed for viral_post_id={post_id}: {exc}", exc_info=True)
                failed_count += 1

        # Commit all Analysis records at end
        await db.commit()
        logger.info(
            f"Analysis batch complete for scan_id={scan_id}: "
            f"analyzed={analyzed_count}, cached={cached_count}, failed={failed_count}"
        )

    return {"analyzed": analyzed_count, "cached": cached_count, "failed": failed_count}
