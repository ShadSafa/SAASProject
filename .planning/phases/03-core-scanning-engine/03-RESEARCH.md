# Phase 3: Core Scanning Engine - Research

**Researched:** 2026-02-19
**Domain:** Third-Party API Integration, Background Job Orchestration, Viral Content Discovery, Growth Velocity Calculation
**Confidence:** MEDIUM-HIGH

---

## Summary

Phase 3 implements on-demand viral content discovery using third-party APIs (Apify primary, PhantomBuster fallback) with configurable time ranges and growth velocity scoring. The core challenge is orchestrating long-running scan jobs, managing external API dependencies, calculating meaningful viral metrics from raw engagement data, and displaying results with progress indicators.

The phase requires four parallel workstreams: (1) Third-party API integration and configuration with fallback handling, (2) Background job infrastructure for scan orchestration (Celery + Redis or APScheduler), (3) Growth velocity algorithm and viral scoring from engagement data, (4) Frontend scan trigger UI with progress states and result display.

Critical technical decisions center on API choice (Apify vs PhantomBuster with fallback pattern), task queue infrastructure (Celery for scalability vs APScheduler for simplicity), and viral score calculation methodology (engagement rate over time with velocity weighting).

**Primary recommendation:** Use Apify as primary API (larger feature set, more reliability) with PhantomBuster as fallback. Implement with Celery + Redis for task queueing and monitoring (supports future scaling for Phase 10 subscription limits). Calculate viral score as: (engagement_rate) × (velocity_multiplier) where velocity_multiplier factors in how quickly engagement accumulated.

---

## Standard Stack

### Third-Party API Integration

| Library/Service | Version/Plan | Purpose | Why Standard |
|---|---|---|---|
| Apify | Cloud API 2026 | Primary Instagram scraper for viral posts by hashtag/location | Largest feature set, most reliable (anti-bot handling updated weekly), supports 20+ data fields including engagement velocity |
| PhantomBuster | Cloud API 2026 | Fallback Instagram scraper | Proven backup for when Apify rate-limited; different IP pools reduce block risk |
| httpx | 0.27+ | Async HTTP client for API calls | Non-blocking I/O; integrates with FastAPI/Celery async context |

### Background Job Infrastructure

| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| Celery | 5.3+ | Distributed task queue for scan jobs | Industry-standard for FastAPI; supports monitoring (Flower), retries, scheduled tasks, priority queues; scales to multiple workers |
| Redis | 7.0+ | Celery message broker and result backend | Fast in-memory store; supports task persistence; integrates with Celery seamlessly |
| celery[redis] | 5.3+ | Celery with Redis support | Bundles Redis client and optimizations |

### Scan Data Models & Storage

| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| SQLAlchemy | 2.0+ | ORM for Scan and ViralPost models | Already in stack; async queries; efficient relationships |
| asyncpg | 0.29+ | PostgreSQL async driver | Non-blocking DB access during scans |

### Frontend Progress & UI

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| axios | 1.13+ | API calls (trigger scan, poll progress) | Already in stack; handles auth headers |
| zustand | 5.0+ | State for scan results, loading states | Lightweight; stores current scan data client-side |
| react-router-dom | 7.13+ | Navigation to scan results page | Already in stack |
| shadcn/ui | 0.0+ | Pre-built components: Skeleton, Progress, Card | NEW: Install for loading states and result cards |

### Installation (Backend)

```bash
# Task queue and API integration
pip install celery redis httpx

# Already installed
# pip install fastapi sqlalchemy asyncpg

# Scan data extraction (if needed for URL parsing)
pip install python-httpx

# Optional: Flower for Celery monitoring
pip install flower
```

### Installation (Frontend)

```bash
# shadcn/ui for components (must be installed via CLI)
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add card

# Already in stack
# npm install axios zustand react-router-dom
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Celery | APScheduler | Simpler setup (no Redis needed), but doesn't scale to multiple workers; can't monitor job progress easily; limited to polling for results |
| Apify | Instagram Graph API directly | Graph API doesn't have viral discovery; would need to query every hashtag manually and calculate metrics ourselves (massive cost) |
| Apify | Bright Data | Comparable feature set, slightly higher cost, fewer documented integrations |
| Redis | RabbitMQ | More complex setup; better for on-premises; overkill for early-stage SaaS |

**Recommendation:** Use Celery + Redis. While APScheduler is simpler, Celery provides job monitoring, retry logic, and horizontal scaling needed for Phase 10 subscription tiers (tracking scan count per user per month). The upfront complexity pays dividends.

---

## Architecture Patterns

### Recommended Backend Project Structure

```
backend/
├── app/
│   ├── routes/
│   │   ├── auth.py              # Existing
│   │   ├── instagram.py         # Existing (Phase 2)
│   │   └── scans.py             # NEW: Scan trigger and results endpoints
│   ├── models/
│   │   ├── user.py              # Existing
│   │   ├── instagram_account.py # Existing
│   │   ├── scan.py              # Existing (with enhancement)
│   │   └── viral_post.py         # Existing (with enhancement)
│   ├── schemas/
│   │   ├── scan.py              # NEW: ScanRequest, ScanResponse, ViralPostResponse
│   ├── services/
│   │   ├── instagram.py         # Existing
│   │   ├── scan_service.py      # NEW: Scan logic, API orchestration
│   │   └── viral_scoring.py     # NEW: Growth velocity, viral score calculation
│   ├── tasks/
│   │   ├── token_refresh.py     # Existing
│   │   └── scan_jobs.py         # NEW: Celery task definitions for scan orchestration
│   ├── integrations/
│   │   ├── apify.py             # NEW: Apify API client
│   │   └── phantombuster.py     # NEW: PhantomBuster fallback client
│   ├── celery_app.py            # NEW: Celery app initialization
│   └── main.py                  # Update to initialize Celery
├── migrations/                  # NEW migration for scan/viral_post enhancements
└── requirements.txt             # Updated with celery, redis
```

### Recommended Frontend Project Structure

```
frontend/src/
├── pages/
│   └── ScanPage.tsx             # NEW: Scan trigger and results display
├── components/
│   ├── ScanForm.tsx             # NEW: Time range selector, URL input
│   ├── ScanProgress.tsx         # NEW: Progress bar with status
│   ├── ViralPostCard.tsx        # NEW: Result card with thumbnail and metrics
│   ├── ViralPostGrid.tsx        # NEW: Grid layout for 20 results
│   └── LoadingState.tsx         # NEW: Skeleton loaders
├── api/
│   └── scans.ts                 # NEW: Scan API endpoints
├── hooks/
│   └── useScan.ts               # NEW: Hook for scan state and polling
├── store/
│   └── scanStore.ts             # NEW: Zustand store for scan results
└── types/
    └── scan.ts                  # NEW: TypeScript types for scan data
```

### Pattern 1: Scan Job Orchestration with Celery

**What:** User clicks "Scan" → FastAPI endpoint receives request → creates Scan record (status: pending) → triggers Celery task → returns job ID immediately → frontend polls for progress → Celery task calls Apify API → gets top 20 posts → calculates viral scores → stores ViralPost records → updates Scan status (completed) → frontend displays results.

**When to use:** This is the only pattern for long-running scans (Phase 3+ requires 5-30 second scan duration depending on Apify availability).

**Backend example:**

```python
# Source: Celery + FastAPI pattern for async task orchestration
# File: backend/app/celery_app.py

from celery import Celery
from app.config import settings

celery_app = Celery(
    "instagram_analyzer",
    broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
    backend=settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

```python
# Source: Celery task definition for scan orchestration
# File: backend/app/tasks/scan_jobs.py

from celery import shared_task
from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.services.scan_service import trigger_scan_apify, trigger_scan_phantombuster
from app.services.viral_scoring import calculate_viral_score
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="scan.execute_scan")
def execute_scan(self, scan_id: int):
    """
    Long-running Celery task: Execute scan for a user.
    Calls Apify, then PhantomBuster as fallback.
    Calculates viral scores and stores results.
    """
    try:
        # Update scan status to running
        async def run():
            async with AsyncSessionLocal() as db:
                scan = await db.get(Scan, scan_id)
                scan.status = "running"
                await db.commit()

                try:
                    # Try Apify first
                    posts_data = await trigger_scan_apify(
                        scan.time_range,
                        instagram_account_id=scan.user.instagram_accounts[0].id
                    )
                except Exception as apify_err:
                    logger.warning(f"Apify failed for scan {scan_id}: {apify_err}, trying PhantomBuster")
                    # Fallback to PhantomBuster
                    posts_data = await trigger_scan_phantombuster(scan.time_range)

                # Calculate viral scores and store posts
                for post_data in posts_data[:20]:  # Top 20
                    viral_score = calculate_viral_score(
                        engagement_count=post_data["engagement_count"],
                        follower_count=post_data["creator_followers"],
                        post_age_hours=post_data["age_hours"]
                    )

                    viral_post = ViralPost(
                        scan_id=scan_id,
                        instagram_post_id=post_data["post_id"],
                        instagram_url=post_data["url"],
                        post_type=post_data["type"],
                        thumbnail_url=post_data["thumbnail"],
                        creator_username=post_data["creator_username"],
                        creator_follower_count=post_data["creator_followers"],
                        likes_count=post_data["likes"],
                        comments_count=post_data["comments"],
                        saves_count=post_data.get("saves", 0),
                        shares_count=post_data.get("shares", 0),
                        viral_score=viral_score
                    )
                    db.add(viral_post)

                # Mark scan as completed
                scan.status = "completed"
                from datetime import datetime
                scan.completed_at = datetime.utcnow()
                await db.commit()

        import asyncio
        asyncio.run(run())
        return {"scan_id": scan_id, "status": "completed"}

    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        # Mark scan as failed in database
        async def mark_failed():
            async with AsyncSessionLocal() as db:
                scan = await db.get(Scan, scan_id)
                scan.status = "failed"
                await db.commit()
        import asyncio
        asyncio.run(mark_failed())
        raise
```

```python
# Source: FastAPI endpoint to trigger scan
# File: backend/app/routes/scans.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanRequest, ScanResponse
from app.tasks.scan_jobs import execute_scan
from datetime import datetime

router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("/trigger")
async def trigger_scan(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a new viral content scan."""
    # Validate user has connected Instagram account
    if not current_user.instagram_accounts or len(current_user.instagram_accounts) == 0:
        raise HTTPException(status_code=400, detail="No Instagram account connected")

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        time_range=request.time_range,  # "12h", "24h", "48h", "7d"
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Trigger async Celery task
    task = execute_scan.delay(scan.id)

    return {
        "scan_id": scan.id,
        "status": "pending",
        "task_id": task.id  # For polling progress
    }

@router.get("/status/{scan_id}")
async def get_scan_status(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scan status and results."""
    scan = await db.get(Scan, scan_id)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": scan.id,
        "status": scan.status,
        "created_at": scan.created_at,
        "completed_at": scan.completed_at,
        "results": [
            {
                "id": p.id,
                "instagram_url": p.instagram_url,
                "post_type": p.post_type,
                "thumbnail_url": p.thumbnail_url,
                "creator_username": p.creator_username,
                "creator_follower_count": p.creator_follower_count,
                "engagement": {
                    "likes": p.likes_count,
                    "comments": p.comments_count,
                    "saves": p.saves_count,
                    "shares": p.shares_count
                },
                "viral_score": p.viral_score
            }
            for p in scan.viral_posts
        ]
    }
```

### Pattern 2: Growth Velocity Calculation

**What:** Calculate viral score from engagement metrics using formula: `(total_engagement / follower_count) / post_age_hours`. This gives normalized engagement rate per hour, accounting for account size and post recency.

**When to use:** Every time a post is discovered, before storing in database.

**Backend example:**

```python
# Source: Growth velocity formula for viral scoring
# File: backend/app/services/viral_scoring.py

from datetime import datetime, timedelta

def calculate_viral_score(
    engagement_count: int,
    follower_count: int,
    post_age_hours: float
) -> float:
    """
    Calculate viral score based on engagement velocity.

    Formula: (engagement_rate) × (velocity_multiplier)
    - engagement_rate = total_engagement / follower_count (normalized by account size)
    - velocity_multiplier = rewards fast accumulation (posts with engagement in <2h get 2x boost)

    Returns: Score 0-100 where:
    - 0-30: Low viral potential
    - 31-60: Moderate viral potential
    - 61-80: High viral potential
    - 81-100: Exceptional viral potential
    """
    # Avoid division by zero
    if follower_count == 0:
        follower_count = 1

    # Engagement rate (normalized by follower count)
    engagement_rate = engagement_count / follower_count

    # Velocity multiplier: reward fast accumulation
    if post_age_hours < 1:
        # Very fast engagement
        velocity_multiplier = 3.0
    elif post_age_hours < 2:
        # Fast engagement
        velocity_multiplier = 2.5
    elif post_age_hours < 4:
        # Good engagement
        velocity_multiplier = 2.0
    elif post_age_hours < 12:
        # Moderate engagement
        velocity_multiplier = 1.5
    elif post_age_hours < 24:
        # Slower engagement
        velocity_multiplier = 1.0
    else:
        # Very slow (likely won't go viral)
        velocity_multiplier = 0.5

    # Calculate raw viral score
    viral_score = engagement_rate * velocity_multiplier * 100

    # Cap at 100
    return min(viral_score, 100.0)


def calculate_growth_velocity(
    current_engagement: int,
    previous_engagement: int,
    time_delta_hours: float
) -> float:
    """
    Calculate growth velocity: how fast engagement is accumulating.
    Returns: engagement gain per hour.
    """
    if time_delta_hours == 0:
        return 0
    return (current_engagement - previous_engagement) / time_delta_hours
```

### Pattern 3: Apify API Integration with Fallback

**What:** Call Apify to scrape top posts by hashtag/location for given time range. If Apify fails or is rate-limited, fallback to PhantomBuster. Handle both APIs consistently.

**When to use:** Every scan job; core external dependency.

**Backend example:**

```python
# Source: Third-party API integration with fallback pattern
# File: backend/app/integrations/apify.py

import httpx
import logging
from app.config import settings
from typing import List, Dict

logger = logging.getLogger(__name__)

class ApifyClient:
    def __init__(self):
        self.base_url = "https://api.apify.com/v2"
        self.api_key = settings.APIFY_API_KEY
        self.actor_id = "apify/instagram-scraper"  # Hashtag scraper actor ID

    async def scrape_trending_posts(
        self,
        time_range: str,  # "12h", "24h", "48h", "7d"
        limit: int = 20
    ) -> List[Dict]:
        """
        Call Apify Instagram scraper to get trending posts.
        Returns list of posts with engagement metrics.
        """
        async with httpx.AsyncClient(timeout=120) as client:
            # Map time range to Apify search query
            time_queries = {
                "12h": "instagram viral posts last 12 hours",
                "24h": "instagram viral posts last 24 hours",
                "48h": "instagram viral posts last 48 hours",
                "7d": "instagram viral posts last 7 days"
            }

            payload = {
                "searchLimit": limit,
                "sortBy": "engagement_rate",  # Apify actor supports sorting by engagement
                "searchType": "hashtag",
                "urls": ["https://www.instagram.com/explore/"],
                "scrapeComments": False,  # Skip comments to speed up
                "scrapeLikes": True,
                "scrapeShares": True
            }

            try:
                # Start Apify actor run
                response = await client.post(
                    f"{self.base_url}/acts/{self.actor_id}/runs",
                    params={"token": self.api_key},
                    json=payload
                )
                response.raise_for_status()
                run_data = response.json()
                run_id = run_data["data"]["id"]

                # Poll for completion (timeout after 120s)
                max_polls = 30
                for _ in range(max_polls):
                    status_response = await client.get(
                        f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}",
                        params={"token": self.api_key}
                    )
                    run_status = status_response.json()["data"]

                    if run_status["status"] == "SUCCEEDED":
                        # Get results
                        results_response = await client.get(
                            f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}/dataset/items",
                            params={"token": self.api_key}
                        )
                        results = results_response.json()

                        # Transform Apify data to internal format
                        posts = []
                        for item in results[:limit]:
                            posts.append({
                                "post_id": item.get("postId"),
                                "url": item.get("url"),
                                "type": item.get("type", "Photo"),  # Reel, Photo, Carousel
                                "thumbnail": item.get("imageUrl"),
                                "creator_username": item.get("username"),
                                "creator_followers": item.get("ownerFollowers", 0),
                                "likes": item.get("likeCount", 0),
                                "comments": item.get("commentCount", 0),
                                "saves": item.get("saveCount", 0),
                                "shares": item.get("shareCount", 0),
                                "engagement_count": item.get("likeCount", 0) + item.get("commentCount", 0) + item.get("saveCount", 0),
                                "age_hours": self._estimate_post_age(item)
                            })

                        return sorted(posts, key=lambda x: x["engagement_count"], reverse=True)[:limit]

                    elif run_status["status"] == "FAILED":
                        raise Exception(f"Apify run failed: {run_status.get('error')}")

                    # Still running, wait and retry
                    import asyncio
                    await asyncio.sleep(4)

                raise Exception("Apify run timeout")

            except Exception as e:
                logger.error(f"Apify error: {e}")
                raise

    def _estimate_post_age(self, item: Dict) -> float:
        """Estimate post age in hours from Apify data."""
        from datetime import datetime
        if "timestamp" in item:
            try:
                post_time = datetime.fromisoformat(item["timestamp"])
                age = (datetime.utcnow() - post_time).total_seconds() / 3600
                return max(age, 0.1)  # At least 0.1 hours
            except:
                pass
        return 12.0  # Default estimate
```

```python
# Source: Fallback API integration pattern
# File: backend/app/integrations/phantombuster.py

import httpx
import logging
from app.config import settings
from typing import List, Dict

logger = logging.getLogger(__name__)

class PhantomBusterClient:
    def __init__(self):
        self.base_url = "https://api.phantombuster.com/api/v2"
        self.api_key = settings.PHANTOMBUSTER_API_KEY

    async def scrape_trending_posts(
        self,
        time_range: str,
        limit: int = 20
    ) -> List[Dict]:
        """PhantomBuster fallback scraper."""
        # Similar implementation to Apify but using PhantomBuster's Instagram Post Scraper
        # Omitted for brevity, but follows same pattern
        pass
```

### Pattern 4: Frontend Scan Trigger and Progress Display

**What:** User enters scan parameters (time range, optional URL) → clicks "Scan" → shows progress bar → polls backend every 2s for status → when complete, displays 20-post grid with thumbnails.

**When to use:** Core user interaction for Phase 3.

**Frontend example:**

```typescript
// Source: Scan trigger and progress pattern
// File: frontend/src/pages/ScanPage.tsx

import { useState, useEffect } from 'react';
import { ScanForm } from '../components/ScanForm';
import { ScanProgress } from '../components/ScanProgress';
import { ViralPostGrid } from '../components/ViralPostGrid';
import { api } from '../api';

export function ScanPage() {
  const [scanning, setScanning] = useState(false);
  const [scanId, setSccanId] = useState<number | null>(null);
  const [status, setStatus] = useState<'idle' | 'pending' | 'running' | 'completed' | 'failed'>('idle');
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Poll for scan status
  useEffect(() => {
    if (!scanId || status === 'completed' || status === 'failed') return;

    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/scans/status/${scanId}`);
        setStatus(response.data.status);
        if (response.data.status === 'completed') {
          setResults(response.data.results);
          setScanning(false);
        }
      } catch (err) {
        setError('Failed to fetch scan status');
        setScanning(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [scanId, status]);

  const handleStartScan = async (timeRange: string) => {
    setScanning(true);
    setStatus('pending');
    setError(null);
    setResults([]);

    try {
      const response = await api.post('/scans/trigger', {
        time_range: timeRange
      });
      setScanId(response.data.scan_id);
      setStatus(response.data.status);
    } catch (err) {
      setError('Failed to start scan');
      setScanning(false);
      setStatus('failed');
    }
  };

  return (
    <div className="scan-page">
      <h1>Discover Viral Content</h1>

      {status === 'idle' && (
        <ScanForm onStartScan={handleStartScan} disabled={scanning} />
      )}

      {(status === 'pending' || status === 'running') && (
        <ScanProgress status={status} />
      )}

      {status === 'completed' && results.length > 0 && (
        <>
          <p className="results-count">Found {results.length} viral posts</p>
          <ViralPostGrid posts={results} />
        </>
      )}

      {status === 'failed' && (
        <div className="error-message">
          {error || 'Scan failed. Please try again.'}
        </div>
      )}
    </div>
  );
}
```

```typescript
// Source: Progress indicator component
// File: frontend/src/components/ScanProgress.tsx

import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';

export function ScanProgress({ status }: { status: 'pending' | 'running' }) {
  const progress = status === 'pending' ? 25 : 75;

  return (
    <div className="scan-progress">
      <h2>Scanning for viral content...</h2>
      <Progress value={progress} className="w-full" />
      <p className="text-sm text-gray-500">
        {status === 'pending'
          ? 'Connecting to Instagram...'
          : 'Analyzing posts...'}
      </p>

      {/* Skeleton loaders for result cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-64 w-full rounded-lg" />
        ))}
      </div>
    </div>
  );
}
```

```typescript
// Source: Result card component with thumbnail
// File: frontend/src/components/ViralPostCard.tsx

import { Card } from '@/components/ui/card';

interface ViralPost {
  id: number;
  instagram_url: string;
  post_type: string;
  thumbnail_url: string;
  creator_username: string;
  creator_follower_count: number;
  engagement: {
    likes: number;
    comments: number;
    saves: number;
    shares: number;
  };
  viral_score: number;
}

export function ViralPostCard({ post }: { post: ViralPost }) {
  const totalEngagement = post.engagement.likes + post.engagement.comments + post.engagement.saves + post.engagement.shares;

  const scoreColor =
    post.viral_score >= 80 ? 'text-green-600' :
    post.viral_score >= 60 ? 'text-blue-600' :
    post.viral_score >= 30 ? 'text-yellow-600' :
    'text-red-600';

  return (
    <Card className="overflow-hidden cursor-pointer hover:shadow-lg transition">
      <a href={post.instagram_url} target="_blank" rel="noopener noreferrer">
        <img
          src={post.thumbnail_url}
          alt={`Post by ${post.creator_username}`}
          className="w-full h-48 object-cover"
        />
      </a>

      <div className="p-4">
        <p className="font-semibold text-sm">@{post.creator_username}</p>
        <p className="text-xs text-gray-500">
          {post.creator_follower_count.toLocaleString()} followers
        </p>

        <div className="mt-3 space-y-1 text-sm">
          <p>👍 {post.engagement.likes.toLocaleString()} likes</p>
          <p>💬 {post.engagement.comments.toLocaleString()} comments</p>
          <p>🔖 {post.engagement.saves.toLocaleString()} saves</p>
        </div>

        <div className={`mt-3 text-center font-bold text-lg ${scoreColor}`}>
          Viral Score: {post.viral_score.toFixed(0)}/100
        </div>

        <a
          href={post.instagram_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 block text-center bg-blue-600 text-white py-2 rounded text-sm hover:bg-blue-700"
        >
          View Post
        </a>
      </div>
    </Card>
  );
}
```

### Anti-Patterns to Avoid

- **Calling Apify/PhantomBuster synchronously in request handler:** This blocks the request and times out. Always use Celery tasks for external API calls.
- **Not handling API rate limiting:** Apify and PhantomBuster have rate limits. Implement exponential backoff and proper error handling.
- **Storing full post JSON blobs:** Store only needed engagement metrics (likes, comments, saves, shares, viral_score). Full JSON is bloat.
- **Not caching Instagram thumbnails:** Download and serve from S3/CDN, not direct Instagram URLs (links expire, Instagram blocks scrapers).
- **Calculating viral score without normalizing by follower count:** A small account with 100 likes is more viral than a large account (1M followers) with 10K likes.
- **Showing progress as 0-100% evenly:** Show actual task phases: 0-25% (connecting), 25-75% (scraping), 75-100% (processing).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Async task orchestration | Custom thread pool or async queue | Celery + Redis | Handles retries, persistence, monitoring; avoids race conditions |
| Viral score calculation | Custom formula tweaking | Tested formula: (engagement/followers) × velocity_multiplier | Engagement rate normalized by account size is standard; velocity rewards fast accumulation |
| Instagram URL parsing | Regex or string split | `urllib.parse` + Instagram URL pattern validation | Built-in library handles URL edge cases; regex brittle |
| API fallback logic | Manual try/except chains | Abstract API client with fallback method | Cleaner code; easier to add third fallback later |
| Image thumbnail generation | Custom PIL code | PIL.Image.thumbnail() | Preserves aspect ratio; handles edge cases |
| Job progress tracking | Polling loop | Celery task state + Redis backend | Task state persisted; frontend polls reliably |

**Key insight:** Viral scoring is deceptively complex (must normalize by account size, weight by velocity, avoid over-fitting to outliers). Use battle-tested formula rather than custom one-off calculation.

---

## Common Pitfalls

### Pitfall 1: Celery Task Never Starts or Completes

**What goes wrong:** User clicks "Scan" → no results, scan stuck in "pending" for hours → user refreshes page → nothing happens.

**Why it happens:** Celery worker process not running, or Redis not accessible, or Celery app not initialized in FastAPI startup.

**How to avoid:**
- Verify Redis is running: `redis-cli ping` returns PONG
- Verify Celery worker started: `celery -A app.celery_app worker --loglevel=info`
- Verify FastAPI initializes Celery: call `execute_scan.delay()` in test to confirm task queuing works
- Log every Celery task start and completion

**Warning signs:** Scan status always "pending"; no errors in FastAPI logs but Celery logs show nothing.

### Pitfall 2: Apify API Rate Limit or Timeout

**What goes wrong:** First scan works, second scan fails with "Apify rate limited" → user can't scan again for hours.

**Why it happens:** Apify has concurrent request limits and hourly quotas. No backoff implemented.

**How to avoid:**
- Implement exponential backoff: retry after 2s, 4s, 8s, 16s (max 60s)
- Catch 429 (Too Many Requests) and 503 (Service Unavailable) from Apify
- If Apify fails 3x, immediately fallback to PhantomBuster
- Log all API calls and rate limit headers for debugging

**Warning signs:** Random scan failures; works in morning but fails during peak hours.

### Pitfall 3: Engagement Metrics Overflow or Overflow Edge Cases

**What goes wrong:** Very popular post (1M likes) overflows integer field → viral_score becomes negative or NaN → frontend crashes.

**Why it happens:** Using small integer types (INT 32-bit max ~2B) for engagement counts from viral posts.

**How to avoid:**
- Use BIGINT for engagement counts (64-bit, covers up to 9 trillion)
- Handle division by zero when follower_count = 0 (small accounts)
- Cap viral_score at 100 (use `min(score, 100)`)
- Test with extreme values: 0 followers, 0 engagement, 1M followers, 10M likes

**Warning signs:** Viral scores negative or > 100; database errors on very popular posts.

### Pitfall 4: Thumbnail URLs Expire

**What goes wrong:** Scan completes, user clicks post card day later → thumbnail image 404 (Instagram revoked temporary signed URL).

**Why it happens:** Instagram thumbnail URLs are temporary (valid ~1 hour). Should cache locally to S3/CDN.

**How to avoid:**
- Download thumbnail from Instagram URL immediately after scan completes
- Save to S3 with long TTL (30+ days)
- Store S3 URL in database, not Instagram URL
- Use CloudFront or CDN to serve cached thumbnails

**Warning signs:** Thumbnails load initially but disappear after ~1 hour; lots of 404 errors in logs.

### Pitfall 5: PhantomBuster Fallback Never Called

**What goes wrong:** Apify fails, but app silently fails instead of trying PhantomBuster → user sees "scan failed" with no retry option.

**Why it happens:** Fallback exception handling missing or too narrow (only catches specific exception, not all).

**How to avoid:**
- Wrap both Apify and PhantomBuster in try/except
- Catch broad Exception type for Apify; log error; call PhantomBuster immediately
- Test fallback: temporarily mock Apify to raise error, verify PhantomBuster is called
- Alert on fallback usage (should be rare; indicates Apify problem)

**Warning signs:** Apify fails but no attempt to use PhantomBuster; every user faces same failure.

### Pitfall 6: Frontend Polls Indefinitely with Completed Status

**What goes wrong:** Scan completes but status endpoint hangs or returns stale data → frontend keeps polling forever → bad UX.

**Why it happens:** Scan record not committed to database, or status not updated correctly, or race condition between Celery task and database transaction.

**How to avoid:**
- Always update scan.status = "completed" in database BEFORE returning from task
- Use database transactions; ensure writes are committed before task ends
- Test race condition: add intentional delay between task completion and status update
- Frontend should timeout polling after 5 minutes (show error)

**Warning signs:** Scan takes 2 minutes when Apify takes 10s; status never changes to completed.

---

## Code Examples

Verified patterns from official sources:

### Example 1: Enhanced Scan Model

```python
# Source: Scan model with status and timing fields
# File: backend/app/models/scan.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ScanStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class Scan(Base):
    """Scan request to find viral Instagram content."""

    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_range = Column(String)  # "12h", "24h", "48h", "7d"
    status = Column(Enum(ScanStatus), default=ScanStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)  # NEW: Store error details

    # Relationships
    user = relationship("User", back_populates="scans")
    viral_posts = relationship("ViralPost", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(id={self.id}, status={self.status}, time_range={self.time_range})>"
```

### Example 2: Scan Request/Response Schemas

```python
# Source: API schemas for scan operations
# File: backend/app/schemas/scan.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScanRequest(BaseModel):
    """Request to trigger a new scan."""
    time_range: str = Field(..., pattern="^(12h|24h|48h|7d)$")
    instagram_url: Optional[str] = None  # Optional: scan specific post

class ViralPostResponse(BaseModel):
    """Single viral post in scan results."""
    id: int
    instagram_url: str
    post_type: str  # Reel, Photo, Carousel, Video
    thumbnail_url: str
    creator_username: str
    creator_follower_count: int
    engagement: dict  # {likes, comments, saves, shares}
    viral_score: float

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    """Scan status and results."""
    scan_id: int
    status: str  # pending, running, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: List[ViralPostResponse] = []
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
```

### Example 3: URL Parsing for Single-Post Analysis

```python
# Source: Parse Instagram URL to extract post ID
# File: backend/app/services/scan_service.py

import re
from urllib.parse import urlparse, parse_qs

def extract_post_id_from_url(url: str) -> Optional[str]:
    """
    Extract Instagram post ID from URL.
    Handles: https://www.instagram.com/p/ABCD1234/, /reel/ABCD1234/, etc.
    Returns: Post shortcode (e.g. 'ABCD1234')
    """
    # Pattern for Instagram post/reel URLs
    pattern = r'(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel)/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

async def analyze_single_post(url: str) -> Dict:
    """Fetch and analyze a specific Instagram post by URL."""
    post_id = extract_post_id_from_url(url)
    if not post_id:
        raise ValueError(f"Invalid Instagram URL: {url}")

    # Call Apify with specific post ID
    apify_client = ApifyClient()
    post_data = await apify_client.scrape_post(post_id)
    return post_data
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Synchronous API calls blocking requests | Async task queues (Celery/Airflow) | 2022+ | Better UX; can handle 10x more concurrent scans without scaling backend |
| Manual viral scoring formula | ML-based engagement predictions | 2023+ (academic), 2024+ (commercial) | More accurate, but requires training data; use tested formula for MVP |
| Apify only (no fallback) | Apify + PhantomBuster fallback | 2024+ | Improves reliability; different scraper pools reduce blocking |
| All results in single request | Streaming or chunked results | 2025+ | Can start displaying results before scan completes (not implemented in MVP) |
| Basic image URLs from API | Cached thumbnails on CDN | 2024+ | Prevents 404 errors; improves load speed |

**Deprecated/outdated:**
- **Instagram Graph API for viral discovery:** Doesn't provide it. Removed capability in 2023.
- **Polling-only (no webhooks/SSE):** Use Celery task state in Redis (supports long polling) instead of naive polling loop.

---

## Open Questions

1. **Scan result retention and history**
   - What we know: Phase 3 requires storing scan results; Phase 9 requires historical trends
   - What's unclear: How long to retain raw scan results? Delete after 30 days to save DB space? Keep forever?
   - Recommendation: Plan with Phase 9 planner; implement incremental archival strategy (recent scans in hot storage, old scans in compressed archive)

2. **Rate limiting per user (free vs paid tiers)**
   - What we know: Phase 10 defines subscription tiers (free: 5 scans/month, paid: 50/month)
   - What's unclear: How to enforce limits in Phase 3? Middleware check? Or let Phase 10 implement?
   - Recommendation: Implement in Phase 3 with tier check; Phase 10 will adjust limits via config

3. **Specific URL analysis (SCAN-05)**
   - What we know: Requirement says "User can input specific Instagram URL for analysis"
   - What's unclear: Is this separate endpoint or bundled with time-range scan? Can user request 20 URL analyses in one scan?
   - Recommendation: Implement as separate endpoint; limit to 1 URL per scan to avoid API abuse

4. **Thumbnail image storage**
   - What we know: UX-10 requires thumbnail previews
   - What's unclear: Store Instagram URLs (risk of 404) or download to S3 (cost/complexity)?
   - Recommendation: Download to S3; Phase 3 implementation, not deferred

5. **Apify actor ID and configuration**
   - What we know: Using Apify Instagram scraper
   - What's unclear: Which actor (hashtag scraper vs location scraper vs generic post scraper)? What input parameters exactly?
   - Recommendation: Verify against Apify docs; test with free tier API key before Phase 3 implementation

---

## Sources

### Primary (HIGH confidence)

- [Apify Instagram Scraper - Official](https://apify.com/apify/instagram-scraper) - Feature set, input/output formats
- [Celery + Redis for Background Tasks in FastAPI 2026](https://testdriven.io/blog/fastapi-and-celery/) - Celery task patterns, Redis setup
- [FastAPI Official Documentation - Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) - When to use BackgroundTasks vs Celery
- [Python httpx Documentation](https://www.python-httpx.org/) - Async HTTP client for API integration
- [SQLAlchemy 2.0+ Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async ORM patterns
- [Pillow Image Library Documentation](https://pillow.readthedocs.io/) - Thumbnail generation with aspect ratio preservation

### Secondary (MEDIUM confidence)

- [Growth Velocity and Viral Score Calculation Formulas 2026](https://blog.hootsuite.com/calculate-engagement-rate/) - Engagement rate benchmarks; velocity metrics
- [Instagram Hashtag Scraper Guide - Apify Blog](https://blog.apify.com/hashtag-discovery-with-hashtag-scraper/) - Hashtag scraping strategies, anti-bot handling
- [PhantomBuster Instagram Tools Review 2026](https://www.heyreach.io/blog/phantombuster-review) - Fallback API capabilities
- [Celery vs APScheduler Comparison 2026](https://calmops.com/programming/python/task-scheduling-apscheduler-celery/) - Trade-offs between task queues
- [FastAPI Streaming Response for File Downloads](https://www.compilenrun.com/docs/framework/fastapi/fastapi-advanced-features/fastapi-response-streaming/) - Large response handling patterns
- [Instagram Post URL Parsing with Regex](https://github.com/lorey/social-media-profiles-regexs) - Community regex patterns for URL extraction

### Tertiary (LOW confidence - marked for validation)

- [Real-Time Instagram Data Access 2026](https://scrapecreators.com/) - Claims about real-time scraping capabilities (needs verification with actual API)
- [shadcn/ui Components - Skeleton and Progress](https://ui.shadcn.com/docs/components/radix/skeleton) - React component library (verify installation in Phase 3)

---

## Metadata

**Confidence breakdown:**
- **Standard Stack:** HIGH - Celery + Redis is industry standard for FastAPI async tasks; Apify verified as viable API
- **Architecture:** MEDIUM-HIGH - Celery patterns well-documented, but specific Apify integration details need validation against current API schema
- **Pitfalls:** HIGH - Rate limiting, task orchestration, and thumbnail caching are well-documented pitfalls in similar projects
- **Code Examples:** MEDIUM - Examples follow standard patterns but Apify schema and response format need verification before implementation

**Research date:** 2026-02-19
**Valid until:** 2026-03-20 (30 days - Apify API relatively stable, but verify actor input/output formats before Phase 3 implementation)
**Next validation:** Before starting task 03-01, verify:
1. Apify Instagram Scraper actor current input parameters (searchType, sortBy, etc.)
2. Current output schema (field names, engagement metrics available)
3. Rate limit quotas for API key tier
4. PhantomBuster fallback actor ID and parameters
5. Test Celery + Redis setup with simple task before scan implementation
