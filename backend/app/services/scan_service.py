"""
Scan service utilities.

Note: Full scan orchestration logic lives in app/tasks/scan_jobs.py (Celery tasks).
This module provides helper functions shared across routes and tasks.
"""
import re
import logging
import uuid
from typing import Optional

import httpx
import boto3
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.scan import Scan

logger = logging.getLogger(__name__)


# Patterns for Instagram post/reel URLs
_INSTAGRAM_POST_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?",
    re.IGNORECASE,
)


def extract_post_id_from_url(url: str) -> Optional[str]:
    """
    Extract the Instagram shortcode from a post, reel, or IGTV URL.

    Returns the shortcode string if matched, or None if the URL is not a
    recognised Instagram post URL.

    Examples:
        https://www.instagram.com/p/ABC123/       -> "ABC123"
        https://www.instagram.com/reel/XYZ789/   -> "XYZ789"
        https://www.instagram.com/tv/DEF456/      -> "DEF456"
        https://www.instagram.com/username/       -> None
    """
    if not url:
        return None
    match = _INSTAGRAM_POST_RE.search(url)
    return match.group(1) if match else None


async def cache_thumbnail_to_s3(instagram_url: str) -> Optional[str]:
    """
    Download thumbnail from Instagram URL and upload to S3.
    Returns S3 URL (https://bucket.s3.region.amazonaws.com/key) or None if caching fails.
    Falls back gracefully — caller should use original URL if this returns None.
    """
    if not settings.AWS_S3_BUCKET or not settings.AWS_ACCESS_KEY_ID:
        logger.warning("S3 not configured — skipping thumbnail cache")
        return None

    if not instagram_url:
        return None

    try:
        # Download image
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(instagram_url, follow_redirects=True)
            resp.raise_for_status()
            image_data = resp.content
            content_type = resp.headers.get("content-type", "image/jpeg")

        # Determine file extension
        ext = "jpg"
        if "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"

        # Upload to S3
        s3_key = f"thumbnails/{uuid.uuid4()}.{ext}"
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
            Body=image_data,
            ContentType=content_type,
            CacheControl="max-age=2592000",  # 30 days
        )

        region = settings.AWS_S3_REGION
        bucket = settings.AWS_S3_BUCKET
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

    except Exception as e:
        logger.warning(f"Failed to cache thumbnail to S3: {e}")
        return None


async def get_scan_with_posts(scan_id: int, db: AsyncSession) -> Optional[Scan]:
    """Fetch scan with all related viral_posts eagerly loaded."""
    result = await db.execute(
        select(Scan)
        .where(Scan.id == scan_id)
        .options(selectinload(Scan.viral_posts))
    )
    return result.scalar_one_or_none()
