---
phase: 03-core-scanning-engine
plan: 01
subsystem: infra
tags: [celery, redis, boto3, alembic, postgresql, sqlalchemy]

# Dependency graph
requires:
  - phase: 02-instagram-integration
    provides: InstagramAccount model + OAuth tokens used by scan engine
  - phase: 01-foundation
    provides: Base SQLAlchemy models, Alembic migration chain (df1349f0b6a4)
provides:
  - Celery application instance (celery_app) for scan job orchestration
  - Scan model with scan_type, target_url, error_message fields
  - ViralPost model with BigInteger engagement counts, thumbnail_s3_url, caption, hashtags, post_age_hours
  - Alembic migration 003 (a3f9c1d7e2b8) at head
  - Config settings for Redis, AWS S3, Apify, PhantomBuster
affects:
  - 03-02-scan-api (imports celery_app for task dispatch)
  - 03-03-apify-integration (uses ViralPost model with new fields)
  - 03-04-scan-results (consumes error_message, scan_type, thumbnail_s3_url)

# Tech tracking
tech-stack:
  added: [celery[redis]>=5.3.0, redis>=5.0.0, boto3>=1.34.0]
  patterns:
    - Celery configured with JSON serializer, task_acks_late=True, worker_prefetch_multiplier=1 (prevents task loss on worker crash)
    - BigInteger for all engagement counts (avoids overflow on viral posts with 100M+ likes)
    - Dual thumbnail fields: thumbnail_url (ephemeral ~1hr) + thumbnail_s3_url (persistent S3 cache)

key-files:
  created:
    - backend/app/celery_app.py
    - backend/migrations/versions/003_scan_engine_enhancements.py
  modified:
    - backend/requirements.txt
    - backend/app/config.py
    - backend/app/models/scan.py
    - backend/app/models/viral_post.py

key-decisions:
  - "task_acks_late=True + worker_prefetch_multiplier=1 prevents scan job loss if Celery worker crashes mid-execution"
  - "instagram_post_id unique constraint dropped — same post can appear in multiple scans without constraint violation"
  - "BigInteger over Integer for engagement counts — viral posts can exceed 2.1B Integer limit on highly shared content"
  - "thumbnail_s3_url column added alongside thumbnail_url — Instagram URLs expire in ~1hr, S3 provides persistence for UX"

patterns-established:
  - "Celery app imported as: from app.celery_app import celery_app"
  - "All scan tasks dispatch via @celery_app.task decorator in backend/app/tasks/"

# Metrics
duration: 4min
completed: 2026-02-19
---

# Phase 3 Plan 1: Celery Task Queue Infrastructure + Model Enhancements Summary

**Celery + Redis task queue wired to FastAPI config, with Scan/ViralPost models enhanced for scan_type, error_message, BigInteger counts, S3 thumbnail caching, and Alembic migration 003 applied**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-19T13:45:59Z
- **Completed:** 2026-02-19T13:49:35Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Created `celery_app.py` with `instagram_analyzer` Celery application, JSON serialization, and crash-safe worker settings
- Enhanced Scan model with `scan_type` (hashtag/url), `target_url`, and `error_message` fields
- Enhanced ViralPost model with BigInteger engagement counts, `thumbnail_s3_url`, `caption`, `hashtags`, `post_age_hours`; dropped unique constraint on `instagram_post_id`
- Applied Alembic migration 003 (`a3f9c1d7e2b8`) cleanly against existing schema — now at head
- Extended config.py with Celery/Redis, AWS S3, Apify, and PhantomBuster settings (all with safe defaults)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Celery/Redis/boto3 dependencies and create celery_app.py** - `15e9d98` (feat)
2. **Task 2: Enhance Scan/ViralPost models and apply migration 003** - `7c5222b` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `backend/app/celery_app.py` - Celery application instance for background scan job orchestration
- `backend/migrations/versions/003_scan_engine_enhancements.py` - Alembic migration adding scan_type, error_message, BigInteger counts, thumbnail_s3_url
- `backend/requirements.txt` - Added celery[redis]>=5.3.0, redis>=5.0.0, boto3>=1.34.0
- `backend/app/config.py` - Added CELERY_BROKER_URL, CELERY_RESULT_BACKEND, AWS_*, APIFY_API_KEY, PHANTOMBUSTER_API_KEY
- `backend/app/models/scan.py` - Added scan_type, target_url, error_message; enhanced nullable annotations
- `backend/app/models/viral_post.py` - BigInteger counts, thumbnail_s3_url, caption, hashtags, post_age_hours; removed unique constraint

## Decisions Made

- `task_acks_late=True` + `worker_prefetch_multiplier=1`: scan jobs are acknowledged only after completion, preventing job loss if worker crashes during a 5-30s Apify call
- Dropped `unique=True` from `instagram_post_id`: the same viral post can be discovered across multiple independent scans; uniqueness was incorrect semantics
- BigInteger over Integer for all engagement counts: Instagram posts can exceed 2.1B Integer limit for highly viral content
- `thumbnail_s3_url` stored separately from `thumbnail_url`: Instagram CDN URLs expire in ~1 hour; S3 provides persistent thumbnail storage for UX requirements (UX-10)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The unique constraint name `viral_posts_instagram_post_id_key` matched PostgreSQL's auto-generated name exactly (confirmed from migration 001 `sa.UniqueConstraint('instagram_post_id')` without explicit name).

## User Setup Required

**External services require manual configuration before running Celery workers:**

- `CELERY_BROKER_URL` — Redis connection string (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND` — Redis result backend (default: `redis://localhost:6379/1`)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, `AWS_S3_REGION` — S3 thumbnail caching (needed in Phase 3 task implementations)
- `APIFY_API_KEY`, `PHANTOMBUSTER_API_KEY` — third-party scan APIs (needed in Phase 3 actor tasks)

**Redis setup (local dev):**
- Windows: `winget install Redis.Redis` then `redis-server`
- Mac: `brew install redis && redis-server`

## Next Phase Readiness

- Celery app ready for `@celery_app.task` decorated scan job tasks (Phase 3 Plan 2+)
- Scan model ready to accept `scan_type="url"` or `"hashtag"` from API endpoints
- ViralPost model ready to store full post data including captions, hashtags, S3 thumbnails
- Migration chain at head; no pending schema work for Phase 3 Plan 1 scope

---
*Phase: 03-core-scanning-engine*
*Completed: 2026-02-19*
