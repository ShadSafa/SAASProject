---
phase: 03-core-scanning-engine
plan: 03
subsystem: api
tags: [apify, phantombuster, celery, s3, boto3, httpx, instagram, viral-scanning]

# Dependency graph
requires:
  - phase: 03-01
    provides: Celery app, Scan/ViralPost SQLAlchemy models, AsyncSessionLocal
  - phase: 03-02
    provides: calculate_viral_score() algorithm

provides:
  - ApifyClient with scrape_trending_posts() and scrape_single_post() with async polling
  - PhantomBusterClient with scrape_trending_posts() as agent-based fallback
  - cache_thumbnail_to_s3() for persistent S3 thumbnail storage
  - extract_post_id_from_url() for Instagram shortcode parsing
  - get_scan_with_posts() for eager-loading scan results
  - execute_scan Celery task orchestrating full scan lifecycle

affects: [03-04, 03-05, 03-06, 03-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Apify actor polling: POST to start run, GET to poll status until SUCCEEDED/FAILED/ABORTED"
    - "PhantomBuster agent: POST to launch, GET containers/fetch-output to poll"
    - "Fallback pattern: try Apify first, catch exception, try PhantomBuster, raise if both fail"
    - "Celery + asyncio.run(): sync Celery task wrapper calls async _run_scan() via asyncio.run()"
    - "S3 thumbnail caching: graceful no-op if AWS credentials not configured"
    - "Lazy imports inside Celery task body to avoid circular imports at module load time"

key-files:
  created:
    - backend/app/integrations/__init__.py
    - backend/app/integrations/apify.py
    - backend/app/integrations/phantombuster.py
  modified:
    - backend/app/services/scan_service.py
    - backend/app/tasks/scan_jobs.py
    - backend/app/config.py

key-decisions:
  - "asyncio.run() inside Celery task: Celery workers run sync; asyncio.run() creates event loop for each task call"
  - "Lazy imports in _run_scan/_fetch_posts: prevents circular import at module load, imports resolved at task execution"
  - "PHANTOMBUSTER_AGENT_ID added to Settings: agent must be pre-configured in PhantomBuster dashboard before API trigger"
  - "task name='scan.execute_scan': short namespaced name over default module path for cleaner Celery routing"

patterns-established:
  - "Normalized post dict schema: all scrapers return identical dict shape (post_id, url, type, thumbnail, creator_username, creator_followers, likes, comments, saves, shares, engagement_count, age_hours, caption, hashtags)"
  - "Graceful fallback chain: Apify primary -> PhantomBuster secondary -> RuntimeError if both fail"
  - "S3 caching is best-effort: returns None on any failure, caller uses original URL as fallback"

# Metrics
duration: 6min
completed: 2026-02-19
---

# Phase 3 Plan 3: Apify Integration Summary

**Async Apify and PhantomBuster scraper clients with S3 thumbnail caching and Celery execute_scan task orchestrating pending->running->completed/failed lifecycle for viral post discovery**

## Performance

- **Duration:** 6 min
- **Started:** 2026-02-19T15:16:25Z
- **Completed:** 2026-02-19T15:22:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- ApifyClient: async polling actor runs to fetch trending Instagram posts across viral/trending/reels hashtags
- PhantomBusterClient: agent-based fallback with identical normalized post dict output schema
- execute_scan Celery task: full lifecycle — loads scan, marks running, fetches posts with fallback, scores + sorts top 20, caches thumbnails to S3, stores ViralPost records, marks completed or failed
- S3 thumbnail caching: graceful no-op when AWS credentials absent, persistent storage via boto3 put_object

## Task Commits

Each task was committed atomically:

1. **Task 1: Apify and PhantomBuster API integration clients** - `233ab29` (feat)
2. **Task 2: S3 thumbnail service and Celery scan task** - `0c56d19` (feat)

**Plan metadata:** (to be added below)

## Files Created/Modified
- `backend/app/integrations/__init__.py` - Empty package init for integrations module
- `backend/app/integrations/apify.py` - ApifyClient with scrape_trending_posts(), scrape_single_post(), _normalize_post(), _estimate_age_hours(), _extract_hashtags()
- `backend/app/integrations/phantombuster.py` - PhantomBusterClient with scrape_trending_posts() and _normalize_post()
- `backend/app/services/scan_service.py` - Extended with cache_thumbnail_to_s3(), get_scan_with_posts() alongside existing extract_post_id_from_url()
- `backend/app/tasks/scan_jobs.py` - Replaced stub with full execute_scan Celery task, _run_scan(), _fetch_posts(), _mark_scan_failed()
- `backend/app/config.py` - Added PHANTOMBUSTER_AGENT_ID setting

## Decisions Made
- `asyncio.run()` inside Celery task body: Celery workers are sync; wrapping async scan logic with asyncio.run() creates a new event loop per task invocation — correct pattern for Celery + async SQLAlchemy
- Lazy imports inside `_run_scan` and `_fetch_posts`: avoids circular import issues at module load time; all heavy imports deferred until task execution
- Task name `scan.execute_scan` (not auto-generated): shorter namespaced name for cleaner Celery routing and monitoring dashboards
- `PHANTOMBUSTER_AGENT_ID` added to Settings: PhantomBuster requires a pre-configured dashboard agent; the ID cannot be auto-discovered via API

## Deviations from Plan

None - plan executed exactly as written.

Note: `scan_service.py` had a partial stub from a prior plan (03-01). The file was extended in-place, adding `cache_thumbnail_to_s3()` and `get_scan_with_posts()` alongside the existing `extract_post_id_from_url()`. This was expected per the plan's design.

## Issues Encountered
None. All dependencies (httpx, boto3) were pre-installed in requirements.txt from plan 03-01. dotenv parse warnings on lines 20/22 are pre-existing non-blocking environment file issues.

## User Setup Required
**External services require manual configuration.** Before running scans, these environment variables must be set in `backend/.env`:

| Variable | Source |
|---|---|
| `APIFY_API_KEY` | Apify Console -> Settings -> Integrations -> API token |
| `PHANTOMBUSTER_API_KEY` | PhantomBuster Dashboard -> API Keys |
| `PHANTOMBUSTER_AGENT_ID` | PhantomBuster Dashboard -> agent ID after configuring Instagram Hashtag Collector |
| `AWS_ACCESS_KEY_ID` | AWS Console -> IAM -> Users -> Security Credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS Console -> IAM -> Users -> Security Credentials |
| `AWS_S3_BUCKET` | Create S3 bucket (e.g. instagram-analyzer-thumbnails) |
| `AWS_S3_REGION` | Region where bucket was created (e.g. us-east-1) |

All API keys are optional for development — the execute_scan task will fail gracefully with descriptive errors if keys are missing.

## Next Phase Readiness
- execute_scan task is importable and Celery-registered as `scan.execute_scan`
- execute_scan.delay(scan_id) can be called from API routes (Plan 03-04 already wires this)
- ApifyClient and PhantomBusterClient ready for integration testing with real API keys
- S3 caching skips gracefully without AWS config — functional in dev without credentials

---
*Phase: 03-core-scanning-engine*
*Completed: 2026-02-19*

## Self-Check: PASSED

All files confirmed present:
- FOUND: backend/app/integrations/__init__.py
- FOUND: backend/app/integrations/apify.py
- FOUND: backend/app/integrations/phantombuster.py
- FOUND: backend/app/services/scan_service.py
- FOUND: backend/app/tasks/scan_jobs.py

All commits confirmed:
- FOUND: 233ab29 (Task 1 - integration clients)
- FOUND: 0c56d19 (Task 2 - scan service + Celery task)
