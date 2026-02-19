"""
Scan service utilities.

Note: Full scan orchestration logic lives in app/tasks/scan_jobs.py (Celery tasks).
This module provides helper functions shared across routes and tasks.
"""
import re
from typing import Optional


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
