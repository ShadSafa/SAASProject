---
phase: 02-instagram-integration
plan: 05
subsystem: infra
tags: [apscheduler, fastapi, background-tasks, token-refresh, email, instagram]

# Dependency graph
requires:
  - phase: 02-02
    provides: Instagram service layer with refresh_access_token, encrypt_token, decrypt_token
  - phase: 02-01
    provides: InstagramAccount model with AccountStatus enum and token fields

provides:
  - APScheduler background job running every 50 days for Instagram token refresh
  - Token expiry email notification via send_token_expired_email
  - FastAPI lifespan context manager for clean startup/shutdown lifecycle

affects: [02-06, future-phases-using-instagram-accounts]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - APScheduler AsyncIOScheduler wired into FastAPI lifespan context manager
    - Per-account exception isolation (one failure does not stop others)
    - Synchronous email function pattern (consistent with existing email service)
    - Inline import of get_user_by_id to avoid circular imports in task module

key-files:
  created:
    - backend/app/tasks/__init__.py
    - backend/app/tasks/token_refresh.py
  modified:
    - backend/app/main.py
    - backend/app/services/email.py

key-decisions:
  - "AsyncIOScheduler over BackgroundScheduler: FastAPI uses asyncio event loop; AsyncIOScheduler integrates natively without threading issues"
  - "start_scheduler/stop_scheduler called in lifespan not on_event: lifespan is the modern FastAPI pattern replacing deprecated @app.on_event"
  - "send_token_expired_email is synchronous: consistent with existing email service pattern (send_verification_email, send_password_reset_email are both sync)"
  - "get_user_by_id imported inline in _notify_token_expired: avoids potential circular import between tasks and crud modules"
  - "logging import added to email.py: needed for error logging in send_token_expired_email"

patterns-established:
  - "Background task pattern: AsyncIOScheduler in app/tasks/, wired via lifespan in main.py"
  - "Per-account isolation: try/except per account ensures one failure does not abort entire batch"

# Metrics
duration: 5min
completed: 2026-02-18
---

# Phase 02 Plan 05: Token Refresh Scheduler Summary

**APScheduler AsyncIOScheduler background job wired into FastAPI lifespan, refreshing all Instagram tokens every 50 days with email notification on expiry**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-18T14:31:11Z
- **Completed:** 2026-02-18T14:36:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Background scheduler starts automatically on FastAPI app startup via lifespan context manager
- Token refresh job runs every 50 days, queries all non-revoked accounts, refreshes each token individually with per-account exception isolation
- Failed refresh marks account as revoked and sends email notification with reconnect link
- Scheduler shuts down cleanly on app shutdown (no hanging threads)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create token refresh background task** - `afea979` (feat)
2. **Task 2: Wire scheduler into FastAPI app lifecycle** - `926cd4d` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `backend/app/tasks/__init__.py` - Python module init (empty)
- `backend/app/tasks/token_refresh.py` - AsyncIOScheduler, refresh_instagram_tokens, _notify_token_expired, start_scheduler, stop_scheduler
- `backend/app/main.py` - Added lifespan context manager, start_scheduler/stop_scheduler on startup/shutdown
- `backend/app/services/email.py` - Added send_token_expired_email function and logging import

## Decisions Made

- Used `AsyncIOScheduler` (not `BackgroundScheduler`) since FastAPI runs on asyncio event loop
- `lifespan` context manager replaces deprecated `@app.on_event("startup")` pattern
- `send_token_expired_email` is synchronous — consistent with all other email functions in the service
- `get_user_by_id` already existed in `crud/user.py` — no addition needed
- Inline import of `get_user_by_id` in `_notify_token_expired` to avoid circular import risk

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] get_user_by_id already existed, no duplicate added**
- **Found during:** Task 1 (reading crud/user.py before writing)
- **Issue:** Plan instructed adding get_user_by_id to crud/user.py, but it already existed
- **Fix:** Skipped the addition — used existing function
- **Files modified:** None (no change needed)
- **Verification:** Import worked in Task 1 verification
- **Committed in:** afea979 (Task 1 commit, no change to crud/user.py)

**2. [Rule 2 - Missing Critical] Added logging import to email.py**
- **Found during:** Task 1 (adding send_token_expired_email)
- **Issue:** send_token_expired_email uses logger.error() but email.py had no logging import
- **Fix:** Added `import logging` and `logger = logging.getLogger(__name__)` to email.py
- **Files modified:** backend/app/services/email.py
- **Verification:** Module imports without errors
- **Committed in:** afea979 (Task 1 commit)

---

**Total deviations:** 2 (1 avoided redundant change, 1 missing critical import added)
**Impact on plan:** Both deviations necessary for correctness. No scope creep.

## Issues Encountered

None — APScheduler 3.11.2 already installed; all dependencies available.

## User Setup Required

None - no external service configuration required for this plan. The scheduler uses existing INSTAGRAM_APP_ID/SECRET and RESEND_API_KEY settings already configured.

## Next Phase Readiness

- Token refresh infrastructure complete for INSTA-03
- Plan 02-04 (Instagram account connection UI) and Plan 02-06 (account management endpoints) can proceed independently
- Scheduler will be active on next server startup

## Self-Check: PASSED

- backend/app/tasks/__init__.py: FOUND
- backend/app/tasks/token_refresh.py: FOUND
- backend/app/services/email.py: FOUND (modified)
- backend/app/main.py: FOUND (modified)
- .planning/phases/02-instagram-integration/02-05-SUMMARY.md: FOUND
- Commit afea979: FOUND
- Commit 926cd4d: FOUND

---
*Phase: 02-instagram-integration*
*Completed: 2026-02-18*
