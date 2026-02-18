# Project State: Instagram Viral Content Analyzer

**Last Updated:** 2026-02-18
**Current Phase:** 02-instagram-integration
**Current Plan:** 02-05 complete — 5/6 plans done
**Milestone:** v1.0

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-15)

**Core value:** Users can identify and understand viral content patterns to create better performing Instagram content themselves

**Current focus:** Instagram OAuth integration - connecting Instagram accounts to the platform

---

## Progress Summary

**Milestone v1.0:**
- Phases: 11 total
- Completed: 1 (Phase 01)
- In Progress: 1 (Phase 02)
- Pending: 9

**Phase 02 Progress:**
- Plans: 6 total
- Completed: 5 ✓
- Remaining: 1

Progress: [####------] 36% — Plan 02-05 complete

**Requirements:**
- Total v1: 79
- Completed: 0
- Remaining: 79

---

## Current Phase

**Phase:** 02 - Instagram Integration
**Status:** IN PROGRESS
**Plans Completed:** 5 of 6

**Completed Plans:**
- ✓ Plan 02-01: InstagramAccount Model Enhancement (2026-02-18)
- ✓ Plan 02-02: Instagram OAuth Backend + Service Layer (2026-02-18)
- ✓ Plan 02-03: AppLayout Nav Infrastructure (2026-02-18)
- ✓ Plan 02-04: Instagram Account Management Frontend (2026-02-18) [Human Verified]
- ✓ Plan 02-05: Token Refresh Scheduler (2026-02-18)

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
- ✓ APScheduler background job: Instagram token refresh every 50 days, wired into FastAPI lifespan
- ✓ Token expiry email notification (send_token_expired_email) with reconnect link
- ✓ InstagramAccountCard, DisconnectConfirmDialog, IntegrationsPage, useAccountsStore
- ✓ AppLayout wired to real account count via useInstagramAccounts hook
- ✓ AppLayout component with persistent nav bar (brand, Dashboard + Settings links, user email, account count)
- ✓ Instagram OAuth backend: authorization URL, callback, token exchange, service layer

**Environment Notes:**
- Backend: Python 3.12 venv at `backend/.venv` (Python 3.13 incompatible with pydantic-core)
- Frontend API: Uses relative base URL `''` - Vite proxy routes `/auth/*` to backend:8000
- Resend: v2.0 module-level API (`import resend; resend.api_key = ...`)
- Database: PostgreSQL local at localhost:5432 (credentials in .env)

---

## Next Steps

**Immediate:**
1. Execute Plan 02-06 (final plan in Phase 02)

**Upcoming:**
- Complete Phase 02 with Plan 02-06
- Begin Phase 03

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

---

## Open Questions

- [ ] Specific Apify actor/endpoint to use for Instagram data?
- [ ] Exact growth velocity formula (engagement rate change per hour)?
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

---

## Last Session

**Date:** 2026-02-18
**Stopped at:** Checkpoint: 02-06 Task 2 — awaiting human verification of complete Phase 2 feature set
**Status:** Phase 02 IN PROGRESS. Plan 02-05 complete: APScheduler background job wired into FastAPI lifespan, token refresh every 50 days, email notification on expiry. Only Plan 02-06 remains.

---

*State initialized: 2026-02-15*
*Last updated: 2026-02-18T14:36:00Z*
