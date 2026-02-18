---
phase: 02-instagram-integration
plan: 02
subsystem: api
tags: [instagram, oauth, fastapi, httpx, cryptography, fernet, token-encryption]

# Dependency graph
requires:
  - phase: 02-01
    provides: InstagramAccount model with AccountStatus enum, LargeBinary token column, profile fields

provides:
  - Instagram OAuth authorization redirect endpoint at GET /integrations/instagram/authorize
  - OAuth callback handler at GET /integrations/instagram/callback (CSRF, code exchange, token storage)
  - Account list endpoint at GET /integrations/instagram/accounts
  - Account disconnect endpoint at DELETE /integrations/instagram/accounts/{id}
  - Fernet symmetric encryption/decryption for Instagram access tokens
  - Shared get_current_active_user dependency in app/dependencies.py

affects:
  - 02-03 (frontend OAuth UI will hit these endpoints)
  - 02-04 (token refresh service uses services/instagram.py refresh_access_token)
  - 02-05 (account management builds on these CRUD operations)

# Tech tracking
tech-stack:
  added:
    - httpx>=0.27.0 (async HTTP client for Instagram Graph API calls)
    - apscheduler>=3.10.0 (background scheduler, used in plan 02-05)
    - cryptography>=42.0.0 (Fernet token encryption)
  patterns:
    - Fernet symmetric encryption with fallback to plain bytes in development (no TOKEN_ENCRYPTION_KEY)
    - In-memory OAuth state dict for CSRF protection (to be replaced with Redis in production)
    - Shared dependency module (app/dependencies.py) to avoid circular imports between routes
    - Free tier account limit enforced in callback with TODO comment for Phase 10 subscription check

key-files:
  created:
    - backend/app/schemas/instagram.py
    - backend/app/crud/instagram.py
    - backend/app/services/instagram.py
    - backend/app/routes/instagram.py
    - backend/app/dependencies.py
  modified:
    - backend/requirements.txt
    - backend/app/config.py
    - backend/app/main.py
    - backend/app/routes/auth.py
    - frontend/vite.config.ts

key-decisions:
  - "Use shared app/dependencies.py for get_current_active_user to prevent circular imports between auth.py and instagram.py"
  - "In-memory _oauth_states dict for CSRF state validation during development (Redis in production)"
  - "Free tier limit of 1 Instagram account enforced in callback route with Phase 10 upgrade hook"
  - "Fernet encryption fallback to plain bytes when TOKEN_ENCRYPTION_KEY not set (dev convenience)"

patterns-established:
  - "Shared dependency: auth guards imported from app.dependencies, not from app.routes.auth"
  - "OAuth callback redirects to frontend URL with query params for success/error signaling"
  - "One-to-one Instagram account constraint checked in application layer (not just DB constraint)"

# Metrics
duration: 4min
completed: 2026-02-18
---

# Phase 02 Plan 02: Instagram OAuth Backend Summary

**FastAPI Instagram OAuth backend with Fernet token encryption, four REST endpoints (authorize, callback, accounts list, disconnect), and shared dependency module to prevent circular imports**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-18T14:24:52Z
- **Completed:** 2026-02-18T14:28:25Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments
- Complete Instagram OAuth flow: authorization redirect, callback with CSRF state validation, code-to-long-lived-token exchange, profile fetching, and encrypted token storage
- Fernet symmetric encryption for access tokens with development fallback when TOKEN_ENCRYPTION_KEY is not set
- Free tier account limit (1 account/user) with hooks for Phase 10 subscription tier upgrades
- Shared `app/dependencies.py` module to centralize `get_current_active_user` and eliminate duplication from auth.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Install dependencies and update config** - `7307e4b` (chore)
2. **Task 2: Create Instagram schemas, CRUD, and service layer** - `ddda351` (feat)
3. **Task 3: Create Instagram routes and wire into app** - `e3bb857` (feat)
4. **Refactor: Deduplicate get_current_active_user** - `a0d4da9` (refactor)

## Files Created/Modified
- `backend/app/schemas/instagram.py` - InstagramAccountResponse and InstagramAccountCreate Pydantic schemas
- `backend/app/crud/instagram.py` - CRUD: create, list by user, get by instagram_id, delete, update_status
- `backend/app/services/instagram.py` - Fernet encryption, build_authorize_url, exchange_code_for_token (short→long-lived), fetch_instagram_profile, refresh_access_token
- `backend/app/routes/instagram.py` - Four OAuth/account management routes with auth, CSRF, tier limits
- `backend/app/dependencies.py` - Shared get_current_active_user dependency (avoids circular imports)
- `backend/requirements.txt` - Added httpx, apscheduler, cryptography
- `backend/app/config.py` - Added INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET, INSTAGRAM_REDIRECT_URI, TOKEN_ENCRYPTION_KEY
- `backend/app/main.py` - Include instagram router
- `backend/app/routes/auth.py` - Import get_current_active_user from dependencies.py, removed duplicate definition
- `frontend/vite.config.ts` - Added /integrations proxy entry

## Decisions Made
- **Shared dependencies module:** Created `app/dependencies.py` to host `get_current_active_user` and avoid circular import between `auth.py` and `instagram.py`. Both routes now import from `dependencies.py`.
- **In-memory CSRF state store:** `_oauth_states` dict used for OAuth state validation during development. Needs Redis replacement in production for multi-process deployments.
- **Free tier limit in callback route:** Account limit check hardcoded to 1 in callback. Comment marks the Phase 10 hook point where subscription tier lookup will replace the hardcoded limit.
- **Fernet fallback:** When `TOKEN_ENCRYPTION_KEY` is empty (dev), tokens stored as plain bytes. Production requires a generated Fernet key in environment.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Refactor] Removed duplicate get_current_active_user from auth.py**
- **Found during:** Task 3 (creating instagram routes)
- **Issue:** Plan said to extract `get_current_active_user` to `dependencies.py` and import in both files. auth.py still had the original definition after creating dependencies.py, creating a duplication.
- **Fix:** Removed the duplicate definition from auth.py and added import from app.dependencies
- **Files modified:** backend/app/routes/auth.py
- **Verification:** Full app import (`from app.main import app`) succeeds and all routes present
- **Committed in:** a0d4da9

---

**Total deviations:** 1 auto-fixed (Rule 1 - code cleanup/correctness)
**Impact on plan:** Necessary cleanup step called out in plan but not counted as a separate task. No scope creep.

## Issues Encountered
None - plan executed without unexpected blockers.

## User Setup Required

**External services require manual configuration.** Users must configure a Meta Developer App before the OAuth flow works:

- `INSTAGRAM_APP_ID` - Meta Developer Dashboard -> App -> Settings -> Basic -> App ID
- `INSTAGRAM_APP_SECRET` - Meta Developer Dashboard -> App -> Settings -> Basic -> App Secret
- `INSTAGRAM_REDIRECT_URI` - Set to `http://localhost:8000/integrations/instagram/callback` in development
- `TOKEN_ENCRYPTION_KEY` - Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

Dashboard tasks:
1. Create Meta Developer App at https://developers.facebook.com/apps/
2. Add Instagram Graph API product
3. Add redirect URI to valid OAuth redirect URIs
4. Set app to Development mode for testing with test accounts

## Next Phase Readiness
- All four backend endpoints ready: authorize, callback, accounts list, disconnect
- Frontend OAuth UI (plan 02-03) can integrate immediately against these endpoints
- Token refresh service (plan 02-04) can use `refresh_access_token` from services/instagram.py
- Accounts need the 002_instagram_enhancements migration applied (from plan 02-01) before the DB is ready

---
*Phase: 02-instagram-integration*
*Completed: 2026-02-18*

## Self-Check: PASSED

All created files verified present on disk. All task commits verified in git log.

| Item | Status |
|------|--------|
| backend/app/schemas/instagram.py | FOUND |
| backend/app/crud/instagram.py | FOUND |
| backend/app/services/instagram.py | FOUND |
| backend/app/routes/instagram.py | FOUND |
| backend/app/dependencies.py | FOUND |
| .planning/phases/02-instagram-integration/02-02-SUMMARY.md | FOUND |
| Commit 7307e4b (chore: dependencies + config) | FOUND |
| Commit ddda351 (feat: schemas, CRUD, service) | FOUND |
| Commit e3bb857 (feat: routes + app wiring) | FOUND |
| Commit a0d4da9 (refactor: deduplicate dependency) | FOUND |
