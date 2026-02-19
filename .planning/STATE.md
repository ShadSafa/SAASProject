# Project State: Instagram Viral Content Analyzer

**Last Updated:** 2026-02-19
**Current Phase:** 03-core-scanning-engine IN PROGRESS
**Current Plan:** 03-04 complete — 4/7 plans done
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
- Completed: 2 (Phase 01, Phase 02)
- In Progress: 1 (Phase 03)
- Pending: 8

**Phase 03 Progress:**
- Plans: 7 total
- Completed: 4 (03-01, 03-02, 03-03, 03-04)
- Remaining: 3

Progress: [####------] 43% — IN PROGRESS

**Requirements:**
- Total v1: 79
- Completed: 0
- Remaining: 79

---

## Current Phase

**Phase:** 03 - Core Scanning Engine
**Status:** IN PROGRESS
**Plans Completed:** 4 of 7

**Completed Plans:**
- ✓ Plan 03-01: Celery/Redis Infrastructure + Scan/ViralPost Models (2026-02-19)
- ✓ Plan 03-02: Viral Scoring Algorithm — TDD (2026-02-19)
- ✓ Plan 03-03: Apify Integration (2026-02-19)
- ✓ Plan 03-04: Scan API Endpoints — schemas, routes, Vite proxy (2026-02-19)

**Remaining Plans:**
- Plan 03-05: Content Analysis (OpenAI)
- Plan 03-06: Results Storage + API Endpoints
- Plan 03-07: Frontend Scan UI

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
- ✓ Scan API: POST /scans/trigger, POST /scans/analyze-url, GET /scans/status/{id}, GET /scans/history — all with auth, rate limit, 404/422/429
- ✓ Pydantic schemas: ScanRequest (time_range regex), AnalyzeUrlRequest, ViralPostResponse, ScanResponse, ScanTriggerResponse, ScanHistoryItem
- ✓ scan_service.py: extract_post_id_from_url(), cache_thumbnail_to_s3(), get_scan_with_posts()
- ✓ execute_scan Celery task wired in scan_jobs.py (full orchestration stub)
- ✓ Vite proxy: /scans/* -> localhost:8000 (5th proxy rule)
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
1. Execute Plan 03-05: Content Analysis (OpenAI)

**Upcoming:**
- Execute Phase 03 plans 03-05 through 03-07
- Integrate OpenAI GPT-4o for viral content analysis
- Results storage and final scan results API

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
| 2026-02-19 | Lazy import execute_scan inside route handler | Prevents circular import at FastAPI startup (routes imported by main.py which also imports celery_app) | Standard pattern for circular-import-safe Celery task dispatch |
| 2026-02-19 | FREE_TIER_MONTHLY_LIMIT = 5 hardcoded for Phase 3 | Pragmatic for current phase; proper subscription tier enforcement deferred to Phase 10 | Known tech debt with explicit upgrade path |
| 2026-02-19 | scan_service.py as shared utility module | URL validation belongs in services layer for reuse by Celery task and routes | Avoids code duplication between route handlers and tasks |

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
| 03-04 | 3 min | 2 | 6 | 2 | 2026-02-19 |

---

## Last Session

**Date:** 2026-02-19
**Stopped at:** Completed 03-04-PLAN.md — Scan API Endpoints
**Status:** Phase 03 IN PROGRESS. Plans 03-01 through 03-04 complete. 4 of 7 plans done. Next: Plan 03-05 Content Analysis (OpenAI). Scan endpoints live at /scans/trigger, /scans/analyze-url, /scans/status/{id}, /scans/history.

---

*State initialized: 2026-02-15*
*Last updated: 2026-02-19T15:19:28Z*
