"""
Celery scan job tasks.

Full scan orchestration: Apify (primary) -> PhantomBuster (fallback),
viral scoring, S3 thumbnail caching, ViralPost record storage.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="scan.execute_scan", max_retries=2, default_retry_delay=30)
def execute_scan(self, scan_id: int) -> Dict[str, Any]:
    """
    Celery task: Full scan lifecycle.
    1. Mark scan as running
    2. Call Apify (primary) -> PhantomBuster (fallback) for posts
    3. Calculate viral scores
    4. Cache thumbnails to S3
    5. Store ViralPost records
    6. Mark scan as completed (or failed on error)

    Args:
        scan_id: Primary key of the Scan record to process.

    Returns:
        dict with scan_id and status.
    """
    try:
        asyncio.run(_run_scan(scan_id))
        return {"scan_id": scan_id, "status": "completed"}
    except Exception as exc:
        logger.error(f"execute_scan failed for scan_id={scan_id}: {exc}", exc_info=True)
        asyncio.run(_mark_scan_failed(scan_id, str(exc)))
        raise self.retry(exc=exc)


async def _run_scan(scan_id: int) -> None:
    """Async implementation of scan logic."""
    from app.database import AsyncSessionLocal
    from app.models.scan import Scan
    from app.models.viral_post import ViralPost
    from app.services.viral_scoring import calculate_viral_score
    from app.services.scan_service import cache_thumbnail_to_s3, extract_post_id_from_url
    from app.integrations.apify import ApifyClient
    from app.integrations.phantombuster import PhantomBusterClient

    async with AsyncSessionLocal() as db:
        # Load scan
        scan = await db.get(Scan, scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        # Mark as running
        scan.status = "running"
        await db.commit()
        logger.info(f"Scan {scan_id} running (type={scan.scan_type}, time_range={scan.time_range})")

        try:
            # Fetch posts from API
            posts_data = await _fetch_posts(scan)

            if not posts_data:
                raise RuntimeError("No posts returned from any API source")

            # Calculate viral scores and sort
            for post in posts_data:
                post["viral_score"] = calculate_viral_score(
                    engagement_count=post["engagement_count"],
                    follower_count=post["creator_followers"],
                    post_age_hours=post["age_hours"],
                )

            # Sort by viral_score descending, take top 20
            posts_data.sort(key=lambda p: p["viral_score"], reverse=True)
            top_posts = posts_data[:20]

            # Store ViralPost records
            for post in top_posts:
                # Cache thumbnail to S3
                s3_url = await cache_thumbnail_to_s3(post.get("thumbnail"))

                viral_post = ViralPost(
                    scan_id=scan_id,
                    instagram_post_id=post.get("post_id") or "unknown",
                    instagram_url=post.get("url"),
                    post_type=post.get("type", "Photo"),
                    caption=post.get("caption", "")[:2000],  # Truncate to 2000 chars
                    hashtags=post.get("hashtags", "[]"),
                    thumbnail_url=post.get("thumbnail"),
                    thumbnail_s3_url=s3_url,
                    creator_username=post.get("creator_username"),
                    creator_follower_count=int(post.get("creator_followers", 0)),
                    likes_count=int(post.get("likes", 0)),
                    comments_count=int(post.get("comments", 0)),
                    saves_count=int(post.get("saves", 0)),
                    shares_count=int(post.get("shares", 0)),
                    post_age_hours=post.get("age_hours", 12.0),
                    viral_score=post["viral_score"],
                )
                db.add(viral_post)

            # Mark completed
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Scan {scan_id} completed with {len(top_posts)} posts")

        except Exception as exc:
            scan.status = "failed"
            scan.error_message = str(exc)[:500]
            await db.commit()
            raise


async def _fetch_posts(scan) -> List[Dict[str, Any]]:
    """Try Apify first, fallback to PhantomBuster."""
    from app.integrations.apify import ApifyClient
    from app.integrations.phantombuster import PhantomBusterClient

    # Development mode: return mock data for instant testing
    if settings.ENVIRONMENT == "development":
        logger.info(f"Development mode: returning mock data for scan {scan.id}")
        return _get_mock_posts()

    if scan.scan_type == "url":
        # Single URL analysis
        apify = ApifyClient()
        try:
            post = await apify.scrape_single_post(scan.target_url)
            return [post] if post else []
        except Exception as e:
            logger.warning(f"Apify single post failed: {e}")
            return []

    # Hashtag/trending scan
    apify = ApifyClient()
    apify_err = None
    try:
        posts = await apify.scrape_trending_posts(scan.time_range or "24h", limit=40)
        logger.info(f"Apify returned {len(posts)} posts for scan {scan.id}")
        return posts
    except Exception as exc:
        apify_err = exc
        logger.warning(f"Apify failed for scan {scan.id}: {exc} — trying PhantomBuster")

    try:
        pb = PhantomBusterClient()
        posts = await pb.scrape_trending_posts(scan.time_range or "24h", limit=40)
        logger.info(f"PhantomBuster returned {len(posts)} posts for scan {scan.id}")
        return posts
    except Exception as pb_err:
        raise RuntimeError(f"Both APIs failed. Apify: {apify_err}. PhantomBuster: {pb_err}")


async def _mark_scan_failed(scan_id: int, error: str) -> None:
    """Mark scan as failed in DB (called when task fails after all retries)."""
    from app.database import AsyncSessionLocal
    from app.models.scan import Scan
    async with AsyncSessionLocal() as db:
        scan = await db.get(Scan, scan_id)
        if scan:
            scan.status = "failed"
            scan.error_message = error[:500]
            await db.commit()


def _get_mock_posts() -> List[Dict[str, Any]]:
    """Return mock Instagram posts for development/testing."""
    return [
        {
            "post_id": "18456789012345678",
            "url": "https://instagram.com/p/ABC123/",
            "type": "Photo",
            "caption": "Beautiful sunset at the beach 🌅 #travel #sunset #nature",
            "hashtags": '["travel", "sunset", "nature", "beautiful"]',
            "thumbnail": "https://via.placeholder.com/400?text=Mock+Post+1",
            "creator_username": "travel_blogger",
            "creator_followers": 125000,
            "likes": 8500,
            "comments": 450,
            "saves": 1200,
            "shares": 320,
            "age_hours": 2.5,
            "engagement_count": 10470,
        },
        {
            "post_id": "18456789012345679",
            "url": "https://instagram.com/p/ABC124/",
            "type": "Carousel",
            "caption": "My morning routine 🌍 #lifestyle #wellness #morningroutine",
            "hashtags": '["lifestyle", "wellness", "morningroutine"]',
            "thumbnail": "https://via.placeholder.com/400?text=Mock+Post+2",
            "creator_username": "wellness_coach",
            "creator_followers": 98000,
            "likes": 6200,
            "comments": 380,
            "saves": 950,
            "shares": 250,
            "age_hours": 3.0,
            "engagement_count": 7782,
        },
    ]
