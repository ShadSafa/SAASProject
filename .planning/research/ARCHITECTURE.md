# Architecture Research: Instagram Viral Content Analyzer

**Research Date:** 2026-02-15
**Domain:** Social Media Analytics SaaS Architecture
**Context:** Python FastAPI backend + React frontend, budget-conscious

---

## System Overview

Typical social media analytics SaaS platforms follow a **three-tier architecture**:

```
┌─────────────┐
│   Frontend  │  React SPA - Dashboard UI
│   (React)   │
└──────┬──────┘
       │ REST API
       │
┌──────▼──────┐
│   Backend   │  FastAPI - Business Logic
│  (FastAPI)  │
└──────┬──────┘
       │
   ┌───┴────┬─────────┬──────────┐
   │        │         │          │
┌──▼──┐ ┌──▼───┐  ┌──▼────┐  ┌──▼────┐
│ DB  │ │ IG   │  │ OpenAI│  │ Queue │
│(PG) │ │ API  │  │  API  │  │(Redis)│
└─────┘ └──────┘  └───────┘  └───────┘
```

---

## Core Components

### 1. Frontend (React SPA)

**Responsibilities:**
- User interface rendering
- User interactions and form handling
- API communication
- Client-side state management
- Data visualization (charts, tables)

**Sub-components:**
- **Auth pages**: Login, signup, password reset
- **Dashboard**: Scan trigger, results display
- **Analysis views**: Detailed post analysis drill-down
- **Filters panel**: Niche, type, engagement, account size filters
- **Export controls**: PDF, CSV, shareable link generation

**Technology:**
- React 18+ with TypeScript
- State management: Zustand or React Query (for server state)
- UI components: Tremor + shadcn/ui
- Charts: Recharts
- Routing: React Router
- Forms: React Hook Form + Zod validation

**Data flow:**
- User action → API call → Update state → Re-render UI

---

### 2. Backend (FastAPI)

**Responsibilities:**
- REST API endpoints
- Business logic orchestration
- Authentication & authorization
- Rate limiting and quota enforcement
- Job scheduling (background scans)

**Sub-components:**

#### Auth Service
- User registration, login, logout
- JWT token generation/validation
- Password hashing (bcrypt)
- Email verification flow

#### Instagram Integration Service
- OAuth flow handling
- Token storage and refresh
- Instagram account management

#### Scan Service
- Trigger viral content discovery
- Call third-party Instagram API
- Parse and normalize data
- Store results in database

#### Analysis Service
- Call OpenAI API with prompts
- Extract hooks, sentiment, patterns
- Apply rule-based heuristics (posting time, engagement velocity)
- Combine LLM + heuristics into unified analysis

#### Filter Service
- Query database with user-specified filters
- Apply niche, type, engagement, account size criteria
- Return filtered results

#### Export Service
- Generate PDF reports (using ReportLab or WeasyPrint)
- Create CSV files
- Generate shareable links with access tokens

#### Subscription Service
- Stripe webhook handling
- Usage tracking (scans per month)
- Tier limit enforcement
- Billing portal integration

**Technology:**
- FastAPI with async endpoints
- SQLAlchemy (ORM) + Alembic (migrations)
- Celery or ARQ (background jobs)
- Redis (caching + job queue)

**Data flow:**
- API request → Auth middleware → Service layer → Database/External API → Response

---

### 3. Database (PostgreSQL)

**Schema:**

**users**
- id, email, hashed_password, created_at, subscription_tier

**instagram_accounts**
- id, user_id, instagram_user_id, access_token, token_expires_at

**scans**
- id, user_id, created_at, time_range, status (pending, running, complete)

**viral_posts**
- id, scan_id, instagram_post_id, author_username, author_follower_count, post_type, caption, hashtags, engagement_metrics (JSON), created_at, viral_score

**analyses**
- id, viral_post_id, hook_analysis (JSON), audience_analysis (JSON), algorithm_factors (JSON), ai_summary, created_at

**user_usage**
- id, user_id, month, scans_count, last_reset_at

**Indexes:**
- users.email (unique)
- instagram_accounts.user_id
- scans.user_id, scans.created_at
- viral_posts.scan_id, viral_posts.viral_score
- analyses.viral_post_id

**Time-series optimization:**
- Consider TimescaleDB extension for viral_posts table (efficient historical queries)

---

### 4. External APIs

#### Instagram Data API (Apify)
- **Purpose:** Fetch trending/viral posts
- **Call pattern:** Async HTTP requests (httpx library)
- **Error handling:** Retry with exponential backoff, fallback to PhantomBuster
- **Rate limiting:** Track API quotas, surface to user if hitting limits

#### OpenAI GPT-4o API
- **Purpose:** Content analysis (hooks, sentiment, patterns)
- **Call pattern:** Async batch requests where possible
- **Cost optimization:**
  - Cache common pattern analyses
  - Use structured outputs to reduce token usage
  - Batch similar posts for analysis
- **Error handling:** Retry transient errors, graceful degradation on failures

#### Stripe API
- **Purpose:** Payment processing, subscription management
- **Call pattern:** Webhooks for events (payment succeeded, subscription updated)
- **Security:** Verify webhook signatures

---

### 5. Background Job Queue (Redis + Celery/ARQ)

**Purpose:** Offload long-running tasks from API requests

**Job types:**
- **Scan job**: Fetch viral posts from Instagram API
- **Analysis job**: Call OpenAI for content analysis
- **Export job**: Generate PDF/CSV files
- **Email job**: Send verification emails, reports

**Benefits:**
- Non-blocking API responses
- Retry failed jobs
- Scale workers independently

---

## Data Flow Diagrams

### User Triggers Scan

```
User → Frontend → POST /scans → Backend
                               ↓
                     Create scan record (DB)
                               ↓
                     Enqueue scan job (Redis)
                               ↓
                     Return scan_id to Frontend
                               ↓
                     Frontend polls GET /scans/{id}
                               ↓
Worker picks up job → Call Apify API → Store posts (DB)
                               ↓
                     For each post: Enqueue analysis job
                               ↓
Analysis worker → Call OpenAI API → Store analysis (DB)
                               ↓
Update scan status = complete
```

### User Views Analysis

```
User → Frontend → GET /scans/{id}/posts?filters=...
                               ↓
Backend → Query viral_posts + analyses (DB)
                               ↓
Apply filters (niche, type, engagement, account size)
                               ↓
Return paginated results
                               ↓
Frontend renders cards/grid
```

---

## Build Order (Dependencies)

### Phase 1: Foundation
1. **Database schema + migrations**
2. **User auth (signup, login, JWT)**
3. **Frontend auth pages**

**Rationale:** Can't build features without users and data storage.

### Phase 2: Core Integration
4. **Instagram OAuth integration**
5. **Third-party API integration (Apify)**
6. **Basic scan trigger + data storage**

**Rationale:** Core data pipeline must work before analysis.

### Phase 3: Analysis Engine
7. **OpenAI API integration**
8. **Analysis service (hook, algorithm factors)**
9. **Frontend display (summary cards)**

**Rationale:** Analysis depends on having post data.

### Phase 4: User Experience
10. **Filtering system**
11. **Drill-down detailed views**
12. **Export functionality (PDF/CSV)**

**Rationale:** Polish on top of working core.

### Phase 5: Monetization
13. **Stripe integration**
14. **Subscription tiers + usage limits**
15. **Billing portal**

**Rationale:** Can launch without payments, add before public release.

---

## Deployment Architecture

### Development
- Local: Docker Compose (backend + PostgreSQL + Redis)
- Frontend: Vite dev server

### Production
- **Frontend:** Vercel (global CDN, auto-deploy from Git)
- **Backend:** Railway (auto-scaling, managed PostgreSQL + Redis)
- **Database:** Railway PostgreSQL (automated backups)
- **Queue workers:** Railway background workers (same codebase)
- **File storage:** Cloudflare R2 (for exports)

### Monitoring & Observability
- **Logs:** Railway built-in logs
- **Errors:** Sentry
- **Metrics:** Simple custom dashboard (API latency, job queue length)
- **Uptime:** UptimeRobot (free tier)

---

## Security Considerations

- **Auth:** JWT tokens, httpOnly cookies for refresh tokens
- **API keys:** Environment variables, never in code
- **Rate limiting:** Per-user, per-endpoint (using slowapi)
- **CORS:** Whitelist frontend domain only
- **SQL injection:** Use parameterized queries (SQLAlchemy ORM)
- **Data privacy:** Encrypt sensitive tokens at rest

---

## Scalability Considerations

**For v1 (0-1000 users):**
- Single backend instance can handle traffic
- PostgreSQL on Railway sufficient
- Celery workers = 2-4 instances

**Future scaling (1000+ users):**
- Horizontal scaling: Add more backend instances behind load balancer
- Database: Read replicas for analytics queries
- Cache: Redis for frequently accessed data (user profiles, scan results)
- CDN: Cache static assets, API responses where appropriate

---

*This architecture balances simplicity for MVP with clear scaling paths.*
