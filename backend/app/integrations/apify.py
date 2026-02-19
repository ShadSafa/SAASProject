import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Apify Instagram Scraper actor ID (verified 2026-02)
APIFY_ACTOR_ID = "apify~instagram-scraper"


class ApifyClient:
    """Primary Instagram data source for viral post discovery."""

    BASE_URL = "https://api.apify.com/v2"
    POLL_INTERVAL_SECONDS = 4
    MAX_POLL_ATTEMPTS = 45  # 45 * 4s = 3 min max wait

    def __init__(self):
        self.api_key = settings.APIFY_API_KEY

    async def scrape_trending_posts(
        self,
        time_range: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Fetch top trending Instagram posts for a given time range.
        time_range: "12h", "24h", "48h", "7d"
        Returns list of normalized post dicts.
        Raises exception on failure (caller should fallback to PhantomBuster).
        """
        if not self.api_key:
            raise ValueError("APIFY_API_KEY not configured")

        # Map time range to recent post search parameters
        recent_days_map = {"12h": 1, "24h": 1, "48h": 2, "7d": 7}
        recent_days = recent_days_map.get(time_range, 1)

        # Use Apify Instagram Scraper actor input
        # Actor: apify/instagram-scraper - scrapes hashtags and profiles
        actor_input = {
            "directUrls": [
                "https://www.instagram.com/explore/tags/viral/",
                "https://www.instagram.com/explore/tags/trending/",
                "https://www.instagram.com/explore/tags/reels/",
            ],
            "resultsType": "posts",
            "resultsLimit": limit * 2,  # Fetch extra, filter to top limit by score
            "addParentData": True,
            "scrapeComments": False,
            "maxRequestRetries": 3,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            # Start actor run
            start_resp = await client.post(
                f"{self.BASE_URL}/acts/{APIFY_ACTOR_ID}/runs",
                params={"token": self.api_key},
                json=actor_input,
            )
            start_resp.raise_for_status()
            run_id = start_resp.json()["data"]["id"]
            logger.info(f"Apify run started: {run_id}")

            # Poll for completion
            for attempt in range(self.MAX_POLL_ATTEMPTS):
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                status_resp = await client.get(
                    f"{self.BASE_URL}/acts/{APIFY_ACTOR_ID}/runs/{run_id}",
                    params={"token": self.api_key},
                )
                status_resp.raise_for_status()
                run_data = status_resp.json()["data"]
                run_status = run_data["status"]

                if run_status == "SUCCEEDED":
                    dataset_id = run_data["defaultDatasetId"]
                    results_resp = await client.get(
                        f"{self.BASE_URL}/datasets/{dataset_id}/items",
                        params={"token": self.api_key, "limit": limit * 2},
                    )
                    results_resp.raise_for_status()
                    raw_items = results_resp.json()
                    return [self._normalize_post(item) for item in raw_items[:limit * 2]]

                elif run_status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    raise RuntimeError(f"Apify run {run_id} ended with status: {run_status}")

                logger.debug(f"Apify run {run_id} still {run_status} (attempt {attempt + 1})")

            raise TimeoutError(f"Apify run {run_id} did not complete within timeout")

    async def scrape_single_post(self, instagram_url: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific Instagram post by URL."""
        if not self.api_key:
            raise ValueError("APIFY_API_KEY not configured")

        actor_input = {
            "directUrls": [instagram_url],
            "resultsType": "posts",
            "resultsLimit": 1,
            "addParentData": True,
            "scrapeComments": False,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            start_resp = await client.post(
                f"{self.BASE_URL}/acts/{APIFY_ACTOR_ID}/runs",
                params={"token": self.api_key},
                json=actor_input,
            )
            start_resp.raise_for_status()
            run_id = start_resp.json()["data"]["id"]

            for _ in range(self.MAX_POLL_ATTEMPTS):
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                status_resp = await client.get(
                    f"{self.BASE_URL}/acts/{APIFY_ACTOR_ID}/runs/{run_id}",
                    params={"token": self.api_key},
                )
                run_data = status_resp.json()["data"]
                if run_data["status"] == "SUCCEEDED":
                    dataset_id = run_data["defaultDatasetId"]
                    results_resp = await client.get(
                        f"{self.BASE_URL}/datasets/{dataset_id}/items",
                        params={"token": self.api_key, "limit": 1},
                    )
                    items = results_resp.json()
                    if items:
                        return self._normalize_post(items[0])
                    return None
                elif run_data["status"] in ("FAILED", "ABORTED", "TIMED-OUT"):
                    raise RuntimeError(f"Apify run failed: {run_data['status']}")

        return None

    def _normalize_post(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Apify output to internal post dict format."""
        likes = item.get("likesCount", 0) or 0
        comments = item.get("commentsCount", 0) or 0
        # Apify doesn't always provide saves/shares — default to 0
        saves = item.get("savesCount", 0) or 0
        shares = item.get("sharesCount", 0) or 0

        # Estimate post age
        age_hours = self._estimate_age_hours(item.get("timestamp") or item.get("postedAtFormatted"))

        # Determine post type
        post_type = "Photo"
        product_type = item.get("productType", "")
        if product_type == "clips":
            post_type = "Reel"
        elif product_type == "carousel_container":
            post_type = "Carousel"
        elif "video" in str(item.get("type", "")).lower():
            post_type = "Video"

        return {
            "post_id": item.get("id") or item.get("shortCode"),
            "url": item.get("url") or f"https://www.instagram.com/p/{item.get('shortCode')}/",
            "type": post_type,
            "thumbnail": item.get("displayUrl") or item.get("thumbnailUrl"),
            "creator_username": item.get("ownerUsername") or item.get("username"),
            "creator_followers": item.get("ownerFollowersCount") or item.get("followersCount") or 0,
            "likes": likes,
            "comments": comments,
            "saves": saves,
            "shares": shares,
            "engagement_count": likes + comments + saves,
            "age_hours": age_hours,
            "caption": item.get("caption") or item.get("text") or "",
            "hashtags": self._extract_hashtags(item.get("caption") or item.get("text") or ""),
        }

    def _estimate_age_hours(self, timestamp_str: Optional[str]) -> float:
        """Parse ISO timestamp and return age in hours. Returns 12.0 if unparseable."""
        if not timestamp_str:
            return 12.0
        try:
            # Handle both naive and aware datetimes
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
            return max(age, 0.1)
        except Exception:
            return 12.0

    def _extract_hashtags(self, caption: str) -> str:
        """Extract hashtags from caption text. Returns JSON array string."""
        import re, json
        tags = re.findall(r"#(\w+)", caption)
        return json.dumps(tags[:30])  # Limit to 30 hashtags
