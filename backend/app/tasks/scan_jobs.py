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
    7. Dispatch analysis background task

    Args:
        scan_id: Primary key of the Scan record to process.

    Returns:
        dict with scan_id and status.
    """
    try:
        viral_post_ids = asyncio.run(_run_scan(scan_id))

        # Dispatch analysis task AFTER event loop closes (outside async context)
        if viral_post_ids:
            from app.tasks.analysis_jobs import analyze_posts_batch
            analyze_posts_batch.delay(scan_id, viral_post_ids)
            logger.info(f"Scan {scan_id} analysis dispatched for {len(viral_post_ids)} posts")

        return {"scan_id": scan_id, "status": "completed"}
    except Exception as exc:
        logger.error(f"execute_scan failed for scan_id={scan_id}: {exc}", exc_info=True)
        asyncio.run(_mark_scan_failed(scan_id, str(exc)))
        raise self.retry(exc=exc)


async def _run_scan(scan_id: int) -> List[int]:
    """Async implementation of scan logic. Returns list of ViralPost IDs for analysis dispatch."""
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
            viral_posts = []
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
                viral_posts.append(viral_post)

            # Mark completed
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Scan {scan_id} completed with {len(top_posts)} posts")

            # Return ViralPost IDs for analysis dispatch (happens after event loop closes)
            if viral_posts:
                return [post.id for post in viral_posts]
            return []

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
    """Return mock Instagram posts for development/testing - 5 highly viral posts."""
    return [
        {
            "post_id": "17987654321098765",
            "url": "https://instagram.com/p/Cu7J8K9Lm0N/",
            "type": "Reel",
            "caption": "POV: You found the best hack to save 10 hours every week 🤯 This changed everything! #productivity #lifehack #shortcut",
            "hashtags": '["productivity", "lifehack", "shortcut", "timedmanagement", "motivation"]',
            "thumbnail": "https://via.placeholder.com/400?text=Viral+Reel+1",
            "creator_username": "productivity_hacks",
            "creator_followers": 450000,
            "likes": 245000,
            "comments": 18500,
            "saves": 67000,
            "shares": 12500,
            "age_hours": 1.5,
            "engagement_count": 343000,
        },
        {
            "post_id": "17987654321098766",
            "url": "https://instagram.com/p/Cu7J8K9Lm0O/",
            "type": "Reel",
            "caption": "This cooking trick will blow your mind 🔥 Chefs HATE this one simple trick! #cooking #foodhack #recipe #viral",
            "hashtags": '["cooking", "foodhack", "recipe", "viral", "kitchenhacks", "cooking101"]',
            "thumbnail": "https://via.placeholder.com/400?text=Viral+Reel+2",
            "creator_username": "chef_secrets",
            "creator_followers": 650000,
            "likes": 520000,
            "comments": 32000,
            "saves": 145000,
            "shares": 28000,
            "age_hours": 0.8,
            "engagement_count": 725000,
        },
        {
            "post_id": "17987654321098767",
            "url": "https://instagram.com/p/Cu7J8K9Lm0P/",
            "type": "Photo",
            "caption": "Aesthetic sunset from my rooftop garden 🌅✨ Nature's best masterpiece #photography #nature #golden_hour #aesthetic",
            "hashtags": '["photography", "nature", "goldenhour", "aesthetic", "landscapephotography"]',
            "thumbnail": "https://via.placeholder.com/400?text=Viral+Photo+3",
            "creator_username": "aestheticcaptures",
            "creator_followers": 280000,
            "likes": 156000,
            "comments": 9800,
            "saves": 42000,
            "shares": 5200,
            "age_hours": 2.1,
            "engagement_count": 213000,
        },
        {
            "post_id": "17987654321098768",
            "url": "https://instagram.com/p/Cu7J8K9Lm0Q/",
            "type": "Carousel",
            "caption": "Transformation Tuesday! 💪 6 month fitness journey - swipe to see the before and after! What's your next goal? #fitness #transformation #motivation #gym",
            "hashtags": '["fitness", "transformation", "motivation", "gym", "fitnessgains", "beforeandafter"]',
            "thumbnail": "https://via.placeholder.com/400?text=Viral+Carousel+4",
            "creator_username": "fitnessmotivation",
            "creator_followers": 380000,
            "likes": 298000,
            "comments": 15600,
            "saves": 76000,
            "shares": 11200,
            "age_hours": 1.2,
            "engagement_count": 400800,
        },
        {
            "post_id": "17987654321098769",
            "url": "https://instagram.com/p/Cu7J8K9Lm0R/",
            "type": "Reel",
            "caption": "Wait for the ending 😱 You won't believe what happens next! #funny #viral #entertainment #comedy #laughs",
            "hashtags": '["funny", "viral", "entertainment", "comedy", "laughs", "foryou"]',
            "thumbnail": "https://via.placeholder.com/400?text=Viral+Reel+5",
            "creator_username": "comedy_central",
            "creator_followers": 520000,
            "likes": 680000,
            "comments": 45000,
            "saves": 89000,
            "shares": 32000,
            "age_hours": 0.5,
            "engagement_count": 846000,
        },
    ]
