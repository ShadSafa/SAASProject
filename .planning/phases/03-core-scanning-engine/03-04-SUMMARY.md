---
phase: 03-core-scanning-engine
plan: 04
subsystem: api
tags: [fastapi, pydantic, celery, sqlalchemy, vite, rest-api]

# Dependency graph
requires:
  - phase: 03-core-scanning-engine
    plan: 01
    provides: Celery app, Scan/ViralPost models, celery_app.py
  - phase: 01-foundation
    provides: get_current_active_user dependency, database session, User model

provides:
  - POST /scans/trigger — time-range scan dispatch (returns scan_id immediately)
  - POST /scans/analyze-url — single Instagram post URL scan dispatch
  - GET /scans/status/{scan_id} — poll scan state + results
  - GET /scans/history — list past scans for current user
  - ScanRequest, AnalyzeUrlRequest, ViralPostResponse, ScanResponse Pydantic schemas
  - extract_post_id_from_url() URL validator in scan_service.py
  - execute_scan Celery task stub in scan_jobs.py
  - Vite proxy rule for /scans/* -> localhost:8000

affects:
  - 03-05-content-analysis (imports execute_scan from scan_jobs.py)
  - 03-06-results-storage (uses ScanResponse schema)
  - 03-07-frontend-scan-ui (consumes /scans/* endpoints via Vite proxy)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Scan dispatch is non-blocking: create DB record, return scan_id, dispatch Celery task async
    - Rate limit check via _check_scan_limit() counts scans in rolling 30-day window
    - Instagram account guard on trigger/analyze-url: 400 if no accounts connected
    - Thumbnail fallback: thumbnail_s3_url preferred over thumbnail_url (S3 persistent vs Instagram ephemeral ~1hr)
    - Lazy imports of Celery tasks inside route handlers prevent circular import issues

key-files:
  created:
    - backend/app/schemas/scan.py
    - backend/app/routes/scans.py
    - backend/app/services/scan_service.py
    - backend/app/tasks/scan_jobs.py
  modified:
    - backend/app/main.py
    - frontend/vite.config.ts

key-decisions:
  - "Lazy import execute_scan inside route handler (not at module top) — prevents circular import between routes and tasks at FastAPI startup"
  - "execute_scan task is a stub in this plan — full Apify/scoring wiring deferred to 03-03/03-05"
  - "scan_service.py created as shared utility module — extract_post_id_from_url() validates URL before scan creation, avoiding unnecessary DB records"
  - "FREE_TIER_MONTHLY_LIMIT = 5 hardcoded for Phase 3 — proper subscription tier enforcement deferred to Phase 10"

patterns-established:
  - "Scan endpoints return ScanTriggerResponse immediately (non-blocking); frontend polls /scans/status/{id}"
  - "All scan endpoints guarded by get_current_active_user from app.dependencies"
  - "ViralPost -> ViralPostResponse conversion via _build_post_response() helper"

# Metrics
duration: 3min
completed: 2026-02-19
---

# Phase 3 Plan 4: Scan API Endpoints Summary

**FastAPI REST endpoints for scan operations exposing POST /trigger, POST /analyze-url, GET /status/{id}, GET /history with Pydantic validation, Celery task dispatch, rate limiting, and Vite proxy wiring**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-19T15:16:33Z
- **Completed:** 2026-02-19T15:19:28Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Created `schemas/scan.py` with 6 Pydantic models: ScanRequest (time_range regex validation), AnalyzeUrlRequest, EngagementResponse, ViralPostResponse, ScanResponse, ScanTriggerResponse, ScanHistoryItem
- Created `routes/scans.py` with 4 authenticated endpoints; includes free-tier rate limit (5/30d), Instagram account guard (400), non-existent scan 404, and invalid URL 422
- Wired scans router into `main.py` and added `/scans` proxy to `vite.config.ts` (5th proxy entry)
- Created `scan_service.py` with `extract_post_id_from_url()` (regex-based Instagram URL validator for /p/, /reel/, /tv/ paths)
- Created `scan_jobs.py` with `execute_scan` Celery task stub (stub dispatches job ID logging; full implementation in 03-03/03-05)

## Task Commits

Each task was committed atomically:

1. **Task 1: Scan schemas and FastAPI routes** - `74edd39` (feat)
2. **Task 2: Wire scans router into FastAPI app and add Vite proxy** - `99b5cc7` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `backend/app/schemas/scan.py` - Pydantic request/response models for all scan operations
- `backend/app/routes/scans.py` - 4 FastAPI endpoints with auth, rate limit, 404/422/429 error handling
- `backend/app/services/scan_service.py` - URL validator and S3 thumbnail caching utilities
- `backend/app/tasks/scan_jobs.py` - execute_scan Celery task stub dispatched by scan routes
- `backend/app/main.py` - Added scans router import and include_router call
- `frontend/vite.config.ts` - Added /scans proxy rule (5 rules total: /api, /auth, /health, /integrations, /scans)

## Decisions Made

- **Lazy import of execute_scan inside route handler:** Avoids circular import at startup (routes imported by main.py which also imports celery_app; top-level task import creates import cycle). Lazy import pattern resolves this cleanly.
- **execute_scan as stub:** Full Apify integration (Plan 03-03) and OpenAI analysis (Plan 03-05) will replace the stub body; the .delay() dispatch interface is unchanged.
- **FREE_TIER_MONTHLY_LIMIT = 5 hardcoded:** Pragmatic for Phase 3. Phase 10 will replace with subscription database query.
- **scan_service.py as shared utility module:** URL validation belongs in services layer (not inline in route), so it can be reused by Celery task in 03-03.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created scan_service.py with extract_post_id_from_url()**
- **Found during:** Task 1 (creating routes/scans.py)
- **Issue:** routes/scans.py imports `from app.services.scan_service import extract_post_id_from_url` but `scan_service.py` did not exist — would cause ImportError on startup
- **Fix:** Created `backend/app/services/scan_service.py` with regex-based Instagram URL validator supporting /p/, /reel/, and /tv/ URL patterns
- **Files modified:** backend/app/services/scan_service.py (created)
- **Verification:** `from app.routes.scans import router` succeeds; 4 routes confirmed
- **Committed in:** `74edd39` (Task 1 commit)

**2. [Rule 3 - Blocking] Created scan_jobs.py with execute_scan Celery task stub**
- **Found during:** Task 1 (creating routes/scans.py)
- **Issue:** routes/scans.py lazy-imports `from app.tasks.scan_jobs import execute_scan` but `scan_jobs.py` did not exist — would cause ImportError at scan dispatch time
- **Fix:** Created `backend/app/tasks/scan_jobs.py` with `execute_scan` Celery task stub using `@celery_app.task` decorator; logs scan_id and returns pending status
- **Files modified:** backend/app/tasks/scan_jobs.py (created)
- **Verification:** Router imports cleanly; task dispatch will not raise ImportError
- **Committed in:** `74edd39` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - Blocking)
**Impact on plan:** Both fixes essential for the routes to function. scan_service.py and scan_jobs.py are explicitly part of the plan's dependency graph; plan simply didn't include their creation as separate tasks.

## Issues Encountered

None. All imports resolved cleanly after creating the two stub files.

## Next Phase Readiness

- `/scans/trigger` and `/scans/analyze-url` dispatch `execute_scan.delay(scan_id)` — ready to receive full implementation in Plan 03-03 (Apify) and 03-05 (OpenAI analysis) without changing the route layer
- `scan_service.py` provides `extract_post_id_from_url()` reusable by scan task implementations
- `scan_service.py` also provides `cache_thumbnail_to_s3()` and `get_scan_with_posts()` utilities for Plan 03-06 (Results Storage)
- All 4 scan endpoints verified in FastAPI app routing table
- Vite proxy ready for frontend scan UI (Plan 03-07)

---
*Phase: 03-core-scanning-engine*
*Completed: 2026-02-19*
