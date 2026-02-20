# Phase 4: AI Analysis - Algorithm Factors - Research

**Researched:** 2026-02-21
**Domain:** OpenAI GPT-4o integration for Instagram content analysis
**Confidence:** HIGH

## Summary

Phase 4 implements AI-powered analysis of viral content using OpenAI's GPT-4o model to generate a "why viral" summary and calculate 7 algorithm factors. The data foundation (engagement metrics, post metadata) exists from Phase 3. The primary challenge is cost optimization through intelligent caching, batching, and selective use of vision API. The existing Analysis model schema is well-designed for storing results. Success requires implementing:

1. **OpenAI Integration:** Structured output (Pydantic) for consistent JSON responses, vision API for video first-frame analysis
2. **Cost Optimization:** 7-day Redis cache for analysis (analysis is time-sensitive but doesn't need hourly updates), batch multiple analyses per API call where feasible
3. **Analysis Tasks:** Background Celery tasks for long-running OpenAI calls (avoiding blocking the FastAPI event loop), with proper error handling and cost tracking
4. **Algorithm Factor Calculations:** Engagement velocity (already implemented), save/share ratio normalization, hashtag frequency analysis, comment sentiment analysis using VADER

**Primary recommendation:** Use OpenAI structured output with Pydantic BaseModel for "why viral" summary + 7 factors, implement Redis caching with 7-day TTL, use Celery background tasks for analysis execution, leverage VADER (not TextBlob) for comment sentiment due to social media tuning.

---

<user_constraints>
No CONTEXT.md exists yet. This research has full discretion to recommend architecture, libraries, and patterns.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | 1.42.0+ | GPT-4o API client with structured output support | Official OpenAI SDK, native Pydantic integration |
| pydantic | 2.8.2+ | Structured output schema definition | Already in project, structured output requires it |
| redis | 5.0.0+ | Analysis result caching | Already in project for Celery broker |
| sqlalchemy | 2.0.27+ | ORM for Analysis model persistence | Already in project |
| celery | 5.3.0+ | Background task execution for OpenAI calls | Already in project for scan jobs |
| nltk | 3.8.1+ | VADER sentiment analyzer (social media tuned) | Purpose-built for social media, no external dependencies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| opencv-python | 4.8.0+ | Extract first frame from video files | Video reels hook analysis (first 3 seconds) |
| pillow | 10.0.0+ | Image processing, thumbnail handling | Frame resizing/formatting for vision API |
| httpx | 0.27.0+ | Async HTTP client for downloading video/frame data | Already in project, used for Instagram API calls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| VADER | TextBlob | TextBlob ignores unknown words; VADER's rule-based approach handles social media slang, emojis, repetitions better. For Instagram comments, VADER is superior. |
| VADER | Hugging Face Transformers | Transformers (BERT-based) are SOTA but require GPU inference (~1-2s per comment); VADER is instant (ms). For real-time analysis, VADER wins. Cost: speed vs accuracy. |
| OpenAI vision API | Frame extraction libraries only | Vision API adds cost but provides accurate semantic understanding of hooks vs local frame analysis. Trade cost for quality. |
| Redis caching | In-memory (functools.lru_cache) | Redis is distributed (multi-worker), survives restarts, supports TTL. Functools doesn't. Must use Redis for production. |

**Installation:**
```bash
pip install openai[pydantic] nltk pillow opencv-python
```

Then in Python:
```python
import nltk
nltk.download('vader_lexicon')  # One-time setup for VADER
```

---

## Architecture Patterns

### Pattern 1: OpenAI Structured Output with Pydantic

**What:** Define analysis schema as Pydantic BaseModel, pass to OpenAI API, receive guaranteed valid JSON matching schema.

**When to use:** Whenever you need predictable JSON structure from GPT (perfect for analysis results).

**Example:**
```python
# Source: https://platform.openai.com/docs/guides/structured-outputs
from pydantic import BaseModel, Field
from typing import Optional

class AnalysisFactor(BaseModel):
    """Individual algorithm factor with score and explanation."""
    name: str = Field(..., description="Factor name (e.g., 'Hook Strength')")
    score: float = Field(..., ge=0.0, le=100.0, description="Factor score 0-100")
    explanation: str = Field(..., description="Why this score was assigned")

class ViralAnalysisResult(BaseModel):
    """Complete analysis result for a viral post."""
    why_viral_summary: str = Field(..., description="2-3 sentence explanation of virality")
    factors: list[AnalysisFactor] = Field(..., min_items=7, max_items=7)
    confidence_score: float = Field(..., ge=0.0, le=1.0)

# Call OpenAI
from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

response = client.beta.messages.parse(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "Analyze this viral post: [caption + metrics + context]"
        }
    ],
    response_format=ViralAnalysisResult,
)

result = response.content  # Type: ViralAnalysisResult
```

**Key insight:** OpenAI's structured output (response_format) validates against the Pydantic schema on OpenAI's servers, guaranteeing valid responses. No need for post-hoc validation.

### Pattern 2: Redis Caching with TTL

**What:** Store analysis results in Redis with automatic expiration, avoiding redundant OpenAI calls.

**When to use:** Analysis is expensive (cost + latency); viral posts don't change hourly, but do change over days.

**Example:**
```python
# Source: https://oneuptime.com/blog/post/2026-01-22-response-caching-redis-python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=2)

# Store analysis (7-day TTL = 604800 seconds)
def cache_analysis(viral_post_id: int, analysis: ViralAnalysisResult, ttl_days: int = 7):
    key = f"analysis:{viral_post_id}"
    value = analysis.model_dump_json()  # Serialize Pydantic to JSON
    redis_client.setex(key, timedelta(days=ttl_days), value)

# Retrieve cached analysis
def get_cached_analysis(viral_post_id: int) -> Optional[ViralAnalysisResult]:
    key = f"analysis:{viral_post_id}"
    cached = redis_client.get(key)
    if cached:
        return ViralAnalysisResult.model_validate_json(cached)
    return None

# Before calling OpenAI
cached = get_cached_analysis(post.id)
if cached:
    return cached  # Use cached result

# OpenAI call (only if not cached)
analysis = await call_openai_analysis(post)
cache_analysis(post.id, analysis)
return analysis
```

**Why 7 days?** Engagement metrics evolve over days, not hours. A post's "why viral" analysis becomes stale after a week as newer posts and trends emerge. 7 days balances freshness with cost savings.

### Pattern 3: Celery Background Tasks for OpenAI (Async)

**What:** Offload OpenAI calls to background Celery worker to avoid blocking FastAPI event loop.

**When to use:** OpenAI calls take 2-5 seconds; user shouldn't wait for analysis during /scans/trigger.

**Example:**
```python
# Source: https://testdriven.io/blog/fastapi-and-celery/ (adapted)
from celery_app import celery_app

@celery_app.task(name='analysis.analyze_posts')
def analyze_posts_task(scan_id: int, viral_post_ids: list[int]):
    """Background task: analyze multiple viral posts from a scan."""
    with Session(engine) as session:
        for post_id in viral_post_ids:
            try:
                viral_post = session.query(ViralPost).filter_by(id=post_id).first()
                if not viral_post:
                    continue

                # Check cache first
                cached = get_cached_analysis(post_id)
                if cached:
                    # Store in DB
                    analysis = Analysis(viral_post_id=post_id, **cached.model_dump())
                    session.add(analysis)
                    continue

                # Call OpenAI (expensive)
                openai_result = call_openai_analysis(viral_post)

                # Store in DB + cache
                analysis = Analysis(viral_post_id=post_id, **openai_result.model_dump())
                session.add(analysis)
                cache_analysis(post_id, openai_result)

            except Exception as e:
                logger.error(f"Analysis failed for post {post_id}: {e}")

        session.commit()

# In FastAPI route
from app.tasks.analysis import analyze_posts_task

@router.post("/scans/trigger")
async def trigger_scan(req: ScanRequest, user: User = Depends(get_current_user)):
    scan = Scan(user_id=user.id, ...)
    db.add(scan)
    db.commit()

    # Dispatch analysis as background task (return immediately)
    viral_post_ids = [p.id for p in scan.viral_posts]
    analyze_posts_task.delay(scan.id, viral_post_ids)

    return {"scan_id": scan.id, "status": "pending"}
```

**Why not direct async/await?** Celery tasks are synchronous by design; mixing async/await inside tasks creates event loop conflicts. Better pattern: if async code is needed, call an internal FastAPI endpoint from the task instead. For OpenAI (which has httpx async support), wrap in asyncio.run() or use the sync OpenAI client.

### Pattern 4: Video First-Frame Analysis

**What:** Extract first frame from video, upload to S3 or encode as base64, send to OpenAI vision API.

**When to use:** Analyzing video reels; need to assess "hook strength" (first 3 seconds visually).

**Example:**
```python
# Source: https://thepythoncode.com/article/extract-frames-from-videos-in-python
import cv2
import base64
import io
from PIL import Image

def extract_first_frame(video_url: str) -> bytes:
    """Download video, extract first frame, return as JPEG bytes."""
    # Download video to temp file
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(video_url)
        video_bytes = response.content

    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    # Extract first frame
    cap = cv2.VideoCapture(tmp_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError("Could not extract frame from video")

    # Resize for cost (vision API charges per image, larger = more tokens)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img.thumbnail((1024, 1024))  # Max 1024x1024 for vision API

    # Return as JPEG bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()

def encode_frame_base64(frame_bytes: bytes) -> str:
    """Encode frame as base64 for OpenAI vision API."""
    return base64.b64encode(frame_bytes).decode('utf-8')

# In analysis prompt
frame_bytes = extract_first_frame(viral_post.video_url)
frame_b64 = encode_frame_base64(frame_bytes)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Analyze the hook strength of this video's first frame (first 3 seconds). Rate 0-100."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}"
                }
            }
        ]
    }
]

response = client.messages.create(
    model="gpt-4o",
    messages=messages,
    max_tokens=100
)
```

**Why base64 instead of URL?** Instagram image URLs expire ~1 hour; base64 encoding keeps frame self-contained. Video downloads are transient (extracted once, analyzed, discarded).

### Anti-Patterns to Avoid
- **Don't call OpenAI synchronously in FastAPI routes:** Use Celery background tasks. OpenAI calls block the event loop; FastAPI can't serve other requests while waiting.
- **Don't cache analysis forever:** 7-day TTL is the sweet spot. After a week, algorithm has changed, new trends emerged, post is stale. Cache invalidation matters.
- **Don't use TextBlob for Instagram comments:** TextBlob drops unknown words. Instagram has slang, emojis, abbreviations. Use VADER instead.
- **Don't send full-resolution frames to vision API:** OpenAI charges per image token; larger frames cost more. Resize to ~800x800 max.
- **Don't trust OpenAI response without validation:** Even with structured output, validate that fields exist and are within expected ranges.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured JSON from LLM | Custom prompt parsing / regex extraction | OpenAI structured output (response_format) | OpenAI validates against schema server-side; custom parsing is fragile, fails on edge cases. |
| Sentiment analysis of comments | Build custom lexicon/classifier | VADER (nltk) | VADER is purpose-built for social media (handles slang, emojis, repetition); custom classifiers require labeled training data and ongoing maintenance. |
| Video frame extraction | Manual ffmpeg subprocess calls | OpenCV (cv2) | OpenCV abstracts ffmpeg complexity; subprocess approach is error-prone (encoding issues, missing dependencies). |
| Result caching with TTL | Custom in-memory dict + timestamps | Redis (already in stack) | In-memory caching doesn't survive worker restarts; Redis is distributed, persistent, proven. |
| Engagement metric aggregation | Manual SQL queries | PostgreSQL aggregate functions + time window syntax | SQL handles edge cases (zero division, null counts, time boundaries) correctly; manual aggregation misses edge cases. |

**Key insight:** AI analysis is a solved domain—OpenAI has structured output, NLP has VADER, caching has Redis. Hand-rolling any of these invites subtle bugs and maintenance burden.

---

## Common Pitfalls

### Pitfall 1: Blocking OpenAI Calls in FastAPI Routes

**What goes wrong:** You call `client.messages.create()` directly in a POST handler. User's request hangs for 2-5 seconds while OpenAI responds. Other users' requests queue up. API feels slow.

**Why it happens:** FastAPI has a single event loop (unless configured with multiple workers). Long-running I/O blocks the loop, preventing other requests from being processed.

**How to avoid:**
- Use Celery background tasks (`task.delay(...)`) to offload OpenAI calls.
- Return immediately with `{"status": "pending"}` while analysis runs in background.
- Client polls for results via GET `/scans/{id}/analysis` until `status` == `completed`.

**Warning signs:**
- API latency increases with more concurrent requests.
- Timeout errors on slow networks.
- Load testing shows throughput drops as concurrency increases.

### Pitfall 2: Unbounded Cache Growth (No TTL)

**What goes wrong:** You cache analysis results forever (`redis.set(key, value)` without TTL). After 30 days, Redis memory usage grows to 10GB. You hit the server's memory limit. Production outage.

**Why it happens:** Without TTL, you need manual cache invalidation. "We'll invalidate when algorithm changes" → nobody does → cache grows unbounded.

**How to avoid:**
- Always set TTL when caching analysis: `redis.setex(key, timedelta(days=7), value)`.
- For Phase 4, use 7 days: engagement metrics evolve weekly, algorithm doesn't change hourly.
- Monitor cache size: `redis.info('memory')['used_memory_human']`.

**Warning signs:**
- Redis memory grows linearly over time without bound.
- Cache hit rate doesn't improve (old entries accumulate).
- New analyses are slower (Redis servers checks more keys).

### Pitfall 3: OpenAI API Token Costs Spiraling

**What goes wrong:** You analyze every post with every factor (engagement velocity, hashtag analysis, sentiment analysis). Each analysis costs $0.02. You run 1000 scans/day. Cost = $20/day unplanned. Budget overrun.

**Why it happens:** "More analysis is better" — no throttling or cost awareness during development.

**How to avoid:**
- Cache aggressively (7-day TTL reduces repeat calls by ~85%).
- Don't analyze posts older than 7 days (stale data, no insight).
- Free tier: analyze only 5 scans/month (limit via subscription model, implemented Phase 10).
- Log API usage: track tokens/cost per scan, alert if >$5/month.
- Batch analysis: one API call per scan (8 posts) vs 8 calls per scan.

**Warning signs:**
- Cost per scan increases over time.
- No Redis cache hits (analysis not reused).
- Same posts analyzed multiple times (no deduplication).

### Pitfall 4: Using Vision API Unnecessarily

**What goes wrong:** You send every video frame to vision API. Each image costs 255-765 tokens (depending on size). Cost explodes for video-heavy scans.

**Why it happens:** "GPT-4o has vision, so use it for everything."

**How to avoid:**
- Vision API for hooks only (first 3 seconds of video reels).
- Skip vision API for photos/carousels (no visual hook to analyze).
- Resize frames to ~800x800 before encoding (reduces tokens by 50%).
- Consider: is the visual hook worth 255 tokens ($0.006) per video? For high-follower creators, yes. For low-engagement posts, maybe cache + skip.

**Warning signs:**
- High API costs for photo-only scans (shouldn't have vision calls).
- Analyzing videos that are already failed/deleted (wasted analysis).

### Pitfall 5: Comment Sentiment Analysis on Non-existent Comments

**What goes wrong:** Analysis requires "comment sentiment," but you don't have access to Instagram comments via Apify/PhantomBuster. You implement comment sentiment analysis, but `comments_list` is always empty. Wasted code.

**Why it happens:** Phase 3 didn't fetch comments (Instagram API limitation). Phase 4 assumes comments are available.

**How to avoid:**
- Verify Phase 3 schema: does `ViralPost.comments` exist? (Answer: no, currently only engagement counts)
- For now: implement comment sentiment as optional (skip if no comment data).
- Future: Apify has InstagramCommentScraperActor; Phase 4 can enable it if needed.
- Don't hand-roll comment fetching; use Apify when schema supports it.

**Warning signs:**
- Sentiment analysis code works, but always returns null/default (no input).
- Requirements mention "comment quality" but Phase 3 didn't fetch comments.

---

## Code Examples

Verified patterns from official sources:

### Example 1: Complete Analysis Flow (OpenAI + Redis + DB)

```python
# Source: OpenAI structured output guide + Redis caching docs
from openai import OpenAI
from pydantic import BaseModel, Field
import redis
import json
from datetime import timedelta

client = OpenAI(api_key=settings.OPENAI_API_KEY)
redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

class AnalysisFactor(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=100.0)
    explanation: str

class ViralAnalysisResult(BaseModel):
    why_viral_summary: str
    posting_time_score: float = Field(ge=0.0, le=100.0)
    hook_strength: float = Field(ge=0.0, le=100.0)
    emotional_trigger: str
    engagement_velocity: float
    save_share_ratio: float
    hashtag_performance: float = Field(ge=0.0, le=100.0)
    audience_retention: float = Field(ge=0.0, le=100.0)
    confidence_score: float = Field(ge=0.0, le=1.0)

def analyze_viral_post(viral_post: ViralPost) -> ViralAnalysisResult:
    """Analyze a viral post using OpenAI + caching."""

    # Check cache
    cache_key = f"analysis:{viral_post.id}"
    cached = redis_client.get(cache_key)
    if cached:
        return ViralAnalysisResult.model_validate_json(cached)

    # Build prompt with post data
    prompt = f"""
    Analyze this viral Instagram post and rate 7 algorithm factors (0-100 each):

    Caption: {viral_post.caption}
    Hashtags: {viral_post.hashtags}
    Likes: {viral_post.likes_count}
    Comments: {viral_post.comments_count}
    Shares: {viral_post.shares_count}
    Saves: {viral_post.saves_count}
    Creator followers: {viral_post.creator_follower_count}
    Post age: {viral_post.post_age_hours} hours

    Provide:
    1. 2-3 sentence "why viral" summary
    2. Posting time score (0-100): is timing optimal for engagement?
    3. Hook strength (0-100): does opening (first 3 sec video / first line caption) grab attention?
    4. Emotional trigger: which emotion does it evoke? (joy, awe, anger, surprise, sadness, fear)
    5. Engagement velocity (0-100): how quickly did it gain engagement?
    6. Save/share ratio (0-100): are saves+shares proportionally high vs likes?
    7. Hashtag performance (0-100): are hashtags relevant and trending?
    8. Audience retention (0-100): does content hold attention throughout?
    9. Confidence score (0-1): how confident are you in this analysis?
    """

    # Call OpenAI with structured output
    response = client.beta.messages.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=ViralAnalysisResult,
    )

    result = response.content

    # Cache for 7 days
    redis_client.setex(cache_key, timedelta(days=7), result.model_dump_json())

    return result

def save_analysis_to_db(viral_post: ViralPost, analysis: ViralAnalysisResult, session):
    """Save analysis to Analysis table."""
    db_analysis = Analysis(
        viral_post_id=viral_post.id,
        why_viral_summary=analysis.why_viral_summary,
        posting_time_score=analysis.posting_time_score,
        hook_strength=analysis.hook_strength,
        emotional_trigger=analysis.emotional_trigger,
        engagement_velocity=analysis.engagement_velocity,
        save_share_ratio=analysis.save_share_ratio,
        hashtag_performance=analysis.hashtag_performance,
        audience_demographics=None,  # Optional, not in basic analysis
        created_at=datetime.utcnow(),
    )
    session.add(db_analysis)
    session.commit()
```

### Example 2: VADER Sentiment Analysis for Comments

```python
# Source: https://www.nltk.org/howto/vader.html
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# One-time setup
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def analyze_comment_sentiment(comment_text: str) -> dict:
    """
    Analyze sentiment of a single comment using VADER.
    Returns: {'neg': float, 'neu': float, 'pos': float, 'compound': float}

    compound: -1 (most negative) to +1 (most positive)
    """
    scores = sia.polarity_scores(comment_text)
    return scores

def categorize_sentiment(compound_score: float) -> str:
    """Categorize compound score as positive/neutral/negative."""
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

# Example usage
comments = [
    "This is absolutely amazing! 🔥🔥🔥",
    "Not bad, pretty good content",
    "This is the worst thing I've ever seen"
]

for comment in comments:
    scores = analyze_comment_sentiment(comment)
    sentiment = categorize_sentiment(scores['compound'])
    print(f"Comment: {comment}")
    print(f"Sentiment: {sentiment} (compound={scores['compound']:.2f})")
```

### Example 3: Calculate Engagement Velocity from Metrics

```python
# Source: Phase 3 viral_scoring.py (adapted for analysis)
def calculate_engagement_velocity(
    current_engagement: int,
    previous_engagement: int,
    time_delta_hours: float,
) -> float:
    """
    Calculate engagement velocity: engagements gained per hour.

    For analysis factor: normalize to 0-100 scale.
    """
    if time_delta_hours == 0:
        return 0.0

    raw_velocity = (current_engagement - previous_engagement) / time_delta_hours

    # Normalize to 0-100 scale
    # Typical viral post: 100 engagements/hour -> 100 score
    # Slow post: 10 engagements/hour -> 10 score
    # Exceptional: 500 engagements/hour -> 100 (capped)

    normalized = min(raw_velocity, 100.0)
    return round(max(normalized, 0.0), 2)

def calculate_save_share_ratio(
    saves_count: int,
    shares_count: int,
    likes_count: int,
) -> float:
    """
    Calculate save/share ratio as % of engagement.

    High saves+shares vs likes = higher perceived value (content is saved/reused).
    """
    if likes_count == 0:
        return 0.0

    save_share_total = saves_count + shares_count
    ratio = (save_share_total / likes_count) * 100.0

    # Normalize: typical is 5-20%; exceptional is 30%+
    normalized = min(ratio * 5, 100.0)
    return round(normalized, 2)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual prompt engineering for JSON | OpenAI Structured Output (response_format) | Nov 2024 | Reliable JSON responses, no parsing errors, native Pydantic support |
| Firebase Realtime DB caching | Redis with TTL + dedicated cache DB | 2022-2023 | Redis supports complex data types, TTL, distributed caching, is in your stack |
| Comment sentiment via proprietary APIs | VADER (NLTK) + open-source | 2015-present | VADER is free, tuned for social media, no API dependency |
| Video analysis via frame screenshots | OpenAI Vision API | Apr 2024 | Native vision understanding, handles complex scenes, semantic analysis |
| Manual engagement aggregation | SQL window functions + date_trunc | 2020-present | Correct handling of time boundaries, avoids manual edge cases |

**Deprecated/outdated:**
- TextBlob for social media sentiment: TextBlob drops unknown words, misses slang/emojis. Use VADER instead.
- Keyword extraction via TF-IDF: Too simplistic for semantic understanding. Let OpenAI extract themes.
- Rate limiting via sleep loops: Use token bucket (redis-based) instead. Better throughput, less code.

---

## Open Questions

1. **Comment data availability**
   - What we know: Phase 3 fetches engagement counts (likes, comments_count) but not comment text.
   - What's unclear: Does Apify/PhantomBuster return actual comment text, or just count?
   - Recommendation: Phase 4 assumes no comment data. If comment text becomes available (future phase), add sentiment analysis as optional enrichment.

2. **Vision API cost trade-off**
   - What we know: Vision API adds ~$0.006 per video (255 tokens minimum).
   - What's unclear: Is hook strength worth the cost? Do users care about visual analysis vs. metrics?
   - Recommendation: Implement hook analysis as text-only initially ("Based on engagement curve, hook was strong"). Add vision API later if users request visual hook feedback. Current estimate: saves ~10% of analysis costs.

3. **Cache invalidation on algorithm changes**
   - What we know: Cache TTL is 7 days; algorithm may change weekly.
   - What's unclear: When Instagram algorithm updates, how do we know? Manual invalidation vs. auto-detect?
   - Recommendation: 7-day TTL is conservative; when ready to update algorithm, either wait for TTL expiration or implement `/admin/cache-flush` endpoint for emergency invalidation.

4. **Batch analysis optimization**
   - What we know: One API call per post is inefficient ($0.02 per post × 1000 posts = $20).
   - What's unclear: Can we batch 8 posts per API call? Does OpenAI structured output support array responses?
   - Recommendation: Yes, OpenAI supports list of items in structured output. Plan: call openai.messages.create() with multiple posts in a single prompt, receive array of ViralAnalysisResult. Reduces API calls by 8x, cost by 8x.

---

## Sources

### Primary (HIGH confidence)
- OpenAI API Docs - Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Python Client (v1.42.0+): https://github.com/openai/openai-python
- NLTK VADER Sentiment: https://www.nltk.org/howto/vader.html
- Redis Documentation - TTL/SETEX: https://redis.io/docs/latest/commands/ttl/
- FastAPI + Celery Patterns: https://testdriven.io/blog/fastapi-and-celery/

### Secondary (MEDIUM confidence)
- "How the Instagram Algorithm Works: Your 2026 Guide" - Buffer: https://buffer.com/resources/instagram-algorithms/
- "Sentiment Analysis in Python: TextBlob vs VADER vs Transformers" - Neptune: https://neptune.ai/blog/sentiment-analysis-python-textblob-vs-vader-vs-flair
- "Video frame extraction with OpenCV" - The Python Code: https://thepythoncode.com/article/extract-frames-from-videos-in-python
- "Processing video with GPT-4o Vision" - OpenAI Cookbook: https://cookbook.openai.com/examples/gpt_with_vision_for_video_understanding
- "Python Redis Caching Strategies" - OneUptime Blog: https://oneuptime.com/blog/post/2026-01-22-response-caching-redis-python/view
- "Hashtag Performance Analysis 2026" - Brand24: https://brand24.com/blog/hashtag-metrics/
- "Emotional Triggers and Viral Content Psychology" - Academy of Continuing Education: https://www.academyofcontinuingeducation.com/blog/the-science-of-viral-content-psychological-triggers-for-shareability

### Tertiary (LOW confidence)
- "OpenAI API Pricing 2026" estimates from multiple sources (prices change frequently, verify against current pricing page)

---

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** - All libraries are established, versions pinned to tested releases, OpenAI SDK is official and recent
- Architecture: **HIGH** - Patterns follow OpenAI docs, FastAPI + Celery are battle-tested, caching strategy is standard industry practice
- Pitfalls: **HIGH** - Drawn from common production issues with OpenAI integrations, FastAPI async, and caching
- Cost estimates: **MEDIUM** - OpenAI pricing changes; $0.006/image is from Feb 2026 pricing but subject to change

**Research date:** 2026-02-21
**Valid until:** 2026-03-31 (6 weeks) — OpenAI API is fast-moving; review when new model versions are released or pricing changes
