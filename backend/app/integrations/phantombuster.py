import asyncio
import logging
from typing import List, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PhantomBusterClient:
    """
    Fallback Instagram scraper when Apify is unavailable.
    Uses PhantomBuster Instagram Hashtag Collector agent.
    """

    BASE_URL = "https://api.phantombuster.com/api/v2"
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 36  # 36 * 5s = 3 min max wait

    def __init__(self):
        self.api_key = settings.PHANTOMBUSTER_API_KEY

    async def scrape_trending_posts(
        self,
        time_range: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending posts using PhantomBuster Instagram Hashtag Collector.
        Returns normalized post dicts in same format as ApifyClient.
        Raises exception on failure.
        """
        if not self.api_key:
            raise ValueError("PHANTOMBUSTER_API_KEY not configured")

        # PhantomBuster uses agent-based approach; agent must be pre-configured in dashboard
        # We trigger the agent via API and poll for result
        # Find your agent ID in PhantomBuster dashboard after setting up Instagram Hashtag Collector
        agent_id = settings.PHANTOMBUSTER_AGENT_ID if hasattr(settings, "PHANTOMBUSTER_AGENT_ID") else ""
        if not agent_id:
            raise ValueError("PHANTOMBUSTER_AGENT_ID not configured")

        headers = {"X-Phantombuster-Key": self.api_key, "Content-Type": "application/json"}
        hashtags = ["viral", "trending", "reels", "viralreels"]

        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            # Launch agent
            launch_resp = await client.post(
                f"{self.BASE_URL}/agents/launch",
                json={
                    "id": agent_id,
                    "argument": {
                        "hashtags": hashtags,
                        "numberOfPostsPerHashtag": limit // len(hashtags) + 1,
                        "recentOrPopular": "recent",
                    },
                },
            )
            launch_resp.raise_for_status()
            container_id = launch_resp.json().get("data", {}).get("containerId")

            for _ in range(self.MAX_POLL_ATTEMPTS):
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                status_resp = await client.get(
                    f"{self.BASE_URL}/containers/fetch-output",
                    params={"id": container_id},
                )
                container_data = status_resp.json().get("data", {})
                state = container_data.get("status")

                if state == "finished":
                    output = container_data.get("output", "[]")
                    import json
                    raw_items = json.loads(output) if isinstance(output, str) else output
                    return [self._normalize_post(item) for item in raw_items[:limit]]
                elif state in ("error", "stopped"):
                    raise RuntimeError(f"PhantomBuster container {container_id} ended: {state}")

            raise TimeoutError("PhantomBuster agent did not complete within timeout")

    def _normalize_post(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize PhantomBuster output to internal format (same as ApifyClient)."""
        likes = item.get("likesCount", 0) or 0
        comments = item.get("commentsCount", 0) or 0
        saves = item.get("savesCount", 0) or 0
        shares = 0  # PhantomBuster doesn't provide shares

        return {
            "post_id": item.get("postId") or item.get("shortCode"),
            "url": item.get("postUrl") or item.get("url"),
            "type": item.get("postType", "Photo"),
            "thumbnail": item.get("imageUrl") or item.get("displayUrl"),
            "creator_username": item.get("profileHandle") or item.get("username"),
            "creator_followers": item.get("followersCount", 0) or 0,
            "likes": likes,
            "comments": comments,
            "saves": saves,
            "shares": shares,
            "engagement_count": likes + comments + saves,
            "age_hours": 12.0,  # PhantomBuster doesn't reliably provide post timestamps
            "caption": item.get("postCaption") or item.get("caption") or "",
            "hashtags": "[]",
        }
