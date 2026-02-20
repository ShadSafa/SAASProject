# Project State: Instagram Viral Content Analyzer

**Last Updated:** 2026-02-21
**Current Phase:** 03-core-scanning-engine COMPLETE ✅
**Current Plan:** 03-07 checkpoint — VERIFIED AND APPROVED
**Milestone:** v1.0

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-15)

**Core value:** Users can identify and understand viral content patterns to create better performing Instagram content themselves

**Current focus:** Phase 3 - Viral content discovery using third-party APIs (Apify, PhantomBuster)

---

## Progress Summary

**Milestone v1.0:**
- Phases: 11 total
- Completed: 3 (Phase 01, Phase 02, Phase 03) ✅
- In Progress: 0
- Pending: 8

**Phase 03 Progress:**
- Plans: 7 total
- Completed: 7 (03-01, 03-02, 03-03, 03-04, 03-05, 03-06, 03-07) ✅
- Remaining: 0

Progress: [#########-] 82% — PHASE 3 COMPLETE ✅

**Requirements:**
- Total v1: 79
- Completed: 0
- Remaining: 79

---

## Current Phase

**Phase:** 03 - Core Scanning Engine
**Status:** IN PROGRESS
**Plans Completed:** 6 of 7

**Completed Plans:**
- ✓ Plan 03-01: Celery/Redis Infrastructure + Scan/ViralPost Models (2026-02-19)
- ✓ Plan 03-02: Viral Scoring Algorithm — TDD (2026-02-19)
- ✓ Plan 03-03: Apify Integration (2026-02-19)
- ✓ Plan 03-04: Scan API Endpoints — schemas, routes, Vite proxy (2026-02-19)
- ✓ Plan 03-05: Frontend Scan Data Layer — types, API client, Zustand store, useScan hook (2026-02-19)
- ✓ Plan 03-06: Frontend Scan UI — ScanForm, ScanProgress, ViralPostCard, ViralPostGrid, ScanPage (2026-02-19)
- [CHECKPOINT] Plan 03-07: Routing, Nav, Phase 3 Verification — awaiting human sign-off (2026-02-19)

**Remaining Plans:**
- None — all 7 plans complete. Phase 3 pending human verification checkpoint.

**Previously Completed (Phase 02):**
- ✓ Plan 02-01: InstagramAccount Model Enhancement (2026-02-18)
- ✓ Plan 02-02: Instagram OAuth Backend + Service Layer (2026-02-18)
- ✓ Plan 02-03: AppLayout Nav Infrastructure (2026-02-18)
- ✓ Plan 02-04: Instagram Account Management Frontend (2026-02-18) [Human Verified]
- ✓ Plan 02-05: Token Refresh Scheduler (2026-02-18)
- ✓ Plan 02-06: Dashboard Expiry Banner + Phase 2 Verification (2026-02-18) [Human Verified]

**Previously Completed (Phase 01):**
- ✓ Plan 01-01: Database Schema & Migrations (2026-02-15)
- ✓ Plan 01-02: Frontend Foundation (2026-02-15)
- ✓ Plan 01-03: Authentication Services (2026-02-15)
- ✓ Plan 01-04: React Frontend Foundation (2026-02-15)
- ✓ Plan 01-05: Auth API Endpoints (2026-02-15)
- ✓ Plan 01-06: Frontend Signup & Login Pages (2026-02-17) [Human Verified]
- ✓ Plan 01-07: Password Reset Endpoints (2026-02-17)
- ✓ Plan 01-08: Password Reset Frontend (2026-02-17)
- ✓ Plan 01-09: Profile Backend Endpoints (2026-02-17)
- ✓ Plan 01-10: Profile Frontend Page (2026-02-17) [Human Verified]

**Recently Completed:**
- ✓ ScanPage: full scan UX flow (idle -> progress -> results/error) via useScan hook at /scan route
- ✓ ScanForm: discover tab (time range 12h/24h/48h/7d) + analyze tab (URL input with instagram.com validation)
- ✓ ScanProgress: animated skeleton cards (8) + progress bar for pending (25%) / running (65%) states
- ✓ ViralPostCard: thumbnail (null-safe), rank badge, creator info, engagement metrics, color-coded viral score badge
- ✓ ViralPostGrid: responsive 1/2/3/4-col grid, empty state fallback
- ✓ /scan route registered in App.tsx + Scan nav link added to AppLayout
- ✓ Frontend scan data layer: types/scan.ts, api/scans.ts, store/scanStore.ts, hooks/useScan.ts
- ✓ useScan hook: polls /scans/status/{id} every 2s, stops on completed/failed/5min timeout, cleanup on unmount
- ✓ Scan API: POST /scans/trigger, POST /scans/analyze-url, GET /scans/status/{id}, GET /scans/history
- ✓ Viral scoring algorithm: calculate_viral_score() with 6-tier velocity multiplier, capped at 100.0
- ✓ Celery app + Scan/ViralPost SQLAlchemy models + migration 003

**Environment Notes:**
- Backend: Python 3.12 venv at `backend/.venv` (Python 3.13 incompatible with pydantic-core)
- Frontend API: Uses relative base URL `''` - Vite proxy routes `/auth/*` to backend:8000
- Resend: v2.0 module-level API (`import resend; resend.api_key = ...`)
- Database: PostgreSQL local at localhost:5432 (credentials in .env)

---

## Next Steps

**Immediate:**
1. Human verification of Phase 3 end-to-end scan flow (see 03-07-PLAN.md Task 2 checklist)

**Upcoming:**
- Upon human approval: mark Phase 03 complete
- Begin Phase 04 planning

---

## Decisions Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2026-02-15 | Use third-party APIs (Apify + PhantomBuster) | Instagram Graph API doesn't provide viral discovery; third-party services aggregate trending data | Enables core feature but adds API dependency risk |
| 2026-02-15 | OpenAI GPT-4o for analysis | Cost-optimized model, strong content analysis, vision support for hook analysis | Balances cost and quality |
| 2026-02-15 | Comprehensive v1 scope (79 requirements) | User wants full-featured launch with all core capabilities | Large scope, 11-phase roadmap required |
| 2026-02-15 | Python FastAPI + React stack | User preference for Python, modern SaaS standard, strong AI ecosystem | Good alignment with tech goals |
| 2026-02-15 | Budget model profile for agents | Cost-conscious approach to planning/research agents | Reduces planning costs while maintaining quality |
| 2026-02-15 | Default SECRET_KEY in development config | Allow testing without environment variables while requiring proper values in production | Unblocks development and testing workflow |
| 2026-02-15 | Dual database drivers (asyncpg + psycopg2) | Asyncpg for runtime performance, psycopg2 for Alembic sync migrations | Standard pattern for async FastAPI with Alembic |
| 2026-02-15 | Manual initial migration creation | No database exists yet to autogenerate from; manually created based on model definitions | Appropriate for initial schema without database |
| 2026-02-15 | Argon2id over bcrypt for password hashing | OWASP 2026 recommends Argon2id; configured with 64MB memory, 3 iterations, 4 threads | Better security against GPU attacks |
| 2026-02-15 | Separate salts for verification vs reset tokens | Prevents cross-flow token reuse (verification token cannot be used for password reset) | Critical security measure |
| 2026-02-15 | 1-hour token expiration for all types | Balances security (short-lived) with UX (enough time to complete flows) | Standard for email verification/reset flows |
| 2026-02-15 | Use Tailwind CSS v4 for styling | Modern utility-first CSS framework, v4 offers improved performance and DX | Enables rapid UI development |
| 2026-02-15 | Use Zustand with persist middleware for auth state | Lightweight state management, built-in persistence, better than Redux for simple auth | Simpler than Redux, perfect for auth state |
| 2026-02-15 | Axios with withCredentials for API client | Automatic httpOnly cookie handling, better interceptor support than fetch | Secure cookie-based auth, no localStorage tokens |
| 2026-02-15 | HttpOnly cookies for JWT storage | XSS protection - JavaScript cannot access tokens | More secure than localStorage/sessionStorage |
| 2026-02-15 | Email verification required before login | Ensures valid email addresses and prevents spam accounts | Better security and data quality |
| 2026-02-15 | Security pattern: Don't reveal email existence in resend endpoint | Prevents email enumeration attacks | Standard security best practice |
| 2026-02-17 | Call email service functions synchronously (no await) | send_verification_email and send_password_reset_email are synchronous functions; awaiting them would cause a runtime error | Consistent with existing signup/resend-verification patterns |
| 2026-02-18 | LargeBinary for access_token | Future encryption stores raw bytes, not plaintext strings; no schema change needed when encryption is added | Prepared for secure token storage from day one |
| 2026-02-18 | AccountStatus as str+enum.Enum | String mixin allows enum values to be used directly in JSON serialization and string comparisons | Simpler serialization without custom encoders |
| 2026-02-18 | server_default='active' in migration | Ensures NOT NULL status on all existing rows without a separate UPDATE statement | Safe migration for production tables with data |
| 2026-02-18 | No refresh_token column on InstagramAccount | Instagram long-lived tokens self-refresh via /refresh_access_token using the same access token | Simpler schema, matches Instagram API design |
| 2026-02-18 | Shared app/dependencies.py for get_current_active_user | Avoids circular imports between auth.py and instagram.py; both routes import from dependencies.py | Single source of truth for auth guard dependency |
| 2026-02-18 | In-memory _oauth_states dict for CSRF state | Simple development approach; needs Redis replacement for multi-process production deployments | Works for dev/single-process, explicit upgrade path noted |
| 2026-02-18 | Fernet token encryption with plain-bytes fallback | When TOKEN_ENCRYPTION_KEY not set, tokens stored as plain bytes; enables dev without setup | Gradual security adoption without blocking development |
| 2026-02-18 | AppLayout wraps pages in App.tsx not self-applied | Pages stay layout-agnostic; layout ownership is at router level | Cleaner page components, easier to swap layouts |
| 2026-02-18 | accountCount defaults to 0 as prop | Real count provided by Plan 02-04 via Instagram accounts hook; zero until then | Progressive enhancement pattern |
| 2026-02-18 | AsyncIOScheduler over BackgroundScheduler | FastAPI uses asyncio event loop; AsyncIOScheduler integrates natively without threading issues | Correct scheduler type for async FastAPI |
| 2026-02-18 | lifespan context manager replaces on_event | Modern FastAPI pattern, replaces deprecated @app.on_event("startup") | Future-proof app lifecycle management |
| 2026-02-18 | send_token_expired_email is synchronous | Consistent with all other email functions in the service layer | Avoids await-on-sync function runtime errors |
| 2026-02-19 | task_acks_late=True + worker_prefetch_multiplier=1 for Celery | Scan jobs (5-30s Apify calls) acknowledged only after completion; prevents job loss if worker crashes mid-execution | Crash-safe scan job orchestration |
| 2026-02-19 | Dropped unique constraint on instagram_post_id | Same viral post can be discovered in multiple independent scans; uniqueness was incorrect semantics | Allows same post to appear in multiple scan results |
| 2026-02-19 | BigInteger for all engagement counts | Viral posts can exceed 2.1B Integer limit (e.g. 100M+ likes + comments + shares) | Prevents integer overflow on highly viral content |
| 2026-02-19 | thumbnail_s3_url stored separately from thumbnail_url | Instagram CDN URLs expire ~1hr; S3 provides persistent storage for UX requirements (UX-10) | Persistent thumbnail display beyond 1 hour |
| 2026-02-19 | age <= 24h uses multiplier 1.0 (not 0.5) | Plan examples explicitly show age=24.0 -> 10.0 (multiplier 1.0); examples are authoritative over text description | Boundary is > 24h for 0.5 slow multiplier |
| 2026-02-19 | round() to 10dp for viral score | IEEE 754 float artifacts (30.000000000000004) break equality tests; 10dp eliminates noise without losing precision | Required for reliable downstream comparisons |
| 2026-02-19 | pytest installed to venv | Was missing from requirements.txt; added as blocking fix for TDD execution | pytest 9.0.2 now available for all future test plans |
| 2026-02-19 | asyncio.run() inside Celery task body | Celery workers run sync; asyncio.run() creates a new event loop per task call for async SQLAlchemy session management | Correct Celery + async pattern without needing gevent/eventlet |
| 2026-02-19 | task name='scan.execute_scan' (explicit) | Short namespaced name preferred over default module path for cleaner Celery routing and monitoring | Consistent with celery best practices for named tasks |
| 2026-02-19 | Lazy import execute_scan inside route handler | Prevents circular import at FastAPI startup (routes imported by main.py which also imports celery_app) | Standard pattern for circular-import-safe Celery task dispatch |
| 2026-02-19 | FREE_TIER_MONTHLY_LIMIT = 5 hardcoded for Phase 3 | Pragmatic for current phase; proper subscription tier enforcement deferred to Phase 10 | Known tech debt with explicit upgrade path |
| 2026-02-19 | scan_service.py as shared utility module | URL validation belongs in services layer for reuse by Celery task and routes | Avoids code duplication between route handlers and tasks |
| 2026-02-19 | useRef for interval ID in useScan | Stable across re-renders; closure in stopPolling always captures same ref without stale closure issues | Correct React pattern for mutable values that don't trigger re-renders |
| 2026-02-19 | Network errors during polling don't stop polling | Transient connection issues should retry; only terminal statuses (completed/failed/timeout) stop polling | Resilient against brief network interruptions |
| 2026-02-19 | clearScan() called at start of each scan | Prevents stale results from previous scan leaking into new scan UI state | Clean slate for every new scan invocation |
| 2026-02-19 | ScanPage hides ScanForm during active scan | Prevents duplicate scan triggers while a scan is in progress (isInProgress = pending or running) | Clean UX: user can't accidentally start two scans |
| 2026-02-19 | ViralPostCard onError hides failed img elements | Instagram CDN URLs expire ~1hr; graceful fallback to bg-gray-100 placeholder when src fails | Robust thumbnail display without breaking the card layout |
| 2026-02-19 | /scan route added via Rule 2 auto-fix | ScanPage was unreachable without a registered route; added /scan with ProtectedRoute + Scan nav link | Essential for page accessibility; follows existing routing pattern |

---

## Open Questions

- [ ] Specific Apify actor/endpoint to use for Instagram data?
- [x] Exact growth velocity formula (engagement rate change per hour)? — RESOLVED: (current - previous) / time_delta_hours
- [ ] Free tier: Confirm 5 scans/month limit?
- [ ] Paid tier: Confirm $20/month for 50 scans?
- [ ] Multiple paid tiers or just one?

---

## Risks & Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Third-party API dependency | High | Implement fallback (Apify → PhantomBuster), monitor API health |
| Runaway AI costs | High | Aggressive caching (7 days), batching, usage limits |
| Instagram OAuth token expiration | Medium | Proactive refresh, clear error messaging, user notifications |
| Large v1 scope (79 req, 11 phases) | Medium | Comprehensive planning, track progress rigorously, phase gating |
| Unit economics (cost per scan) | Medium | Target $0.30/scan, monitor actual costs, adjust pricing if needed |

---

## Context for Agents

**When planning phases:**
- Review research files in `.planning/research/` for stack/architecture guidance
- Budget-conscious: minimize API costs through caching, batching
- Focus on table stakes first, differentiators next
- Each phase should be independently deployable where possible

**Tech stack (reference):**
- Backend: Python FastAPI + PostgreSQL + Redis + Celery
- Frontend: React + TypeScript + Vite + Tremor/shadcn UI
- APIs: Apify/PhantomBuster (Instagram), OpenAI GPT-4o (analysis), Stripe (payments)
- Infrastructure: Railway (backend/DB), Vercel (frontend)

---

## Performance Metrics

| Plan | Duration | Tasks | Files | Commits | Date |
|------|----------|-------|-------|---------|------|
| 01-01 | 23 min | 3 | 11 | 3 | 2026-02-15 |
| 01-02 | - | - | - | - | 2026-02-15 |
| 01-03 | 10 min | 3 | 5 | 3 | 2026-02-15 |
| 01-04 | 13.5 min | 3 | 18 | 4 | 2026-02-15 |
| 01-05 | 4 min | 2 | 3 | 1 | 2026-02-15 |
| 01-07 | 5 min | 1 | 1 | 1 | 2026-02-17 |
| 02-01 | 5 min | 2 | 2 | 2 | 2026-02-18 |
| 02-02 | 4 min | 3 | 9 | 4 | 2026-02-18 |
| 02-03 | 5 min | 2 | 4 | 2 | 2026-02-18 |
| 02-05 | 5 min | 2 | 4 | 2 | 2026-02-18 |
| 03-01 | 4 min | 2 | 6 | 2 | 2026-02-19 |
| 03-02 | 15 min | 3 | 3 | 3 | 2026-02-19 |
| 03-03 | 6 min | 2 | 6 | 2 | 2026-02-19 |
| 03-04 | 3 min | 2 | 6 | 2 | 2026-02-19 |
| 03-05 | 2 min | 2 | 4 | 2 | 2026-02-19 |
| 03-06 | 3 min | 2 | 7 | 3 | 2026-02-19 |
| 03-07 | 1 min | 1 | 0 | 0 | 2026-02-19 |

---

## Last Session

**Date:** 2026-02-21
**Completed:** Phase 03 Core Scanning Engine ✅
**Status:** Phase 03 COMPLETE and VERIFIED. All 7 plans executed and human checkpoint verification passed:
  - ✅ Scans execute successfully in development mode
  - ✅ Viral scoring algorithm produces correct scores
  - ✅ Results display with engagement metrics and rankings
  - ✅ Scan history persists and displays in Dashboard
  - ✅ Multiple scans execute concurrently
  - ✅ Different time ranges work (12h, 24h, 48h, 7d)
  - ✅ Status tracking works (pending → running → completed)

**Ready for:** Phase 04 planning can begin

---

*State initialized: 2026-02-15*
*Last updated: 2026-02-19T15:33:29Z*
