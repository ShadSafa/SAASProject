# Roadmap: Instagram Viral Content Analyzer

**Created:** 2026-02-15
**Milestone:** v1.0 - Initial Launch
**Total Requirements:** 79
**Phases:** 11

---

## Overview

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Foundation & Database | AUTH-01 to AUTH-09 (9) | ○ Pending |
| 2 | Instagram Integration | INSTA-01 to INSTA-06 (6) | ○ Pending |
| 3 | Core Scanning Engine | SCAN-01 to SCAN-08, UX-01, UX-10 (10) | ○ Pending |
| 4 | AI Analysis - Algorithm Factors | ANALYSIS-01 to ANALYSIS-11 (11) | ○ Pending |
| 5 | AI Analysis - Content Deep Dive | ANALYSIS-12 to ANALYSIS-19 (8) | ○ Pending |
| 6 | User Interface & Display | UX-02 to UX-04, UX-11 (4) | ○ Pending |
| 7 | Filtering & Search | UX-05 to UX-09 (5) | ○ Pending |
| 8 | Export System | EXPORT-01 to EXPORT-07 (7) | ○ Pending |
| 9 | Historical Data & Trends | HISTORY-01 to HISTORY-07 (7) | ○ Pending |
| 10 | Subscription & Monetization | SUB-01 to SUB-10 (10) | ○ Pending |
| 11 | Polish & Launch Preparation | Testing, optimization, deployment (2) | ○ Pending |

**Total:** 79 requirements mapped ✓

---

## Phase Details

### Phase 1: Foundation & Database

**Goal:** Establish core infrastructure with complete user authentication and database schema

**Requirements:**
- AUTH-01: Email/password signup
- AUTH-02: Email verification sending
- AUTH-03: Email verification requirement
- AUTH-04: Login flow
- AUTH-05: Session persistence
- AUTH-06: Logout
- AUTH-07: Password reset
- AUTH-08: Profile management
- AUTH-09: Account deletion

**Success Criteria:**
1. User can create account, receive verification email, and log in
2. Session persists across browser restarts
3. User can reset password via email link
4. User can update profile and delete account
5. Database schema for all entities (users, instagram_accounts, scans, viral_posts, analyses, user_usage) created with migrations

**Dependencies:** None (starting phase)

**Plans:** 10 plans in 5 waves

Plans:
- [ ] 01-01-PLAN.md — Database schema and migrations (all entities)
- [ ] 01-02-PLAN.md — Email service integration (Resend)
- [ ] 01-03-PLAN.md — Auth service layer (Argon2id, JWT, tokens)
- [ ] 01-04-PLAN.md — Frontend setup (React, Vite, Zustand)
- [ ] 01-05-PLAN.md — Backend signup and email verification
- [ ] 01-06-PLAN.md — Frontend signup and login pages
- [ ] 01-07-PLAN.md — Backend password reset
- [ ] 01-08-PLAN.md — Frontend password reset pages
- [ ] 01-09-PLAN.md — Backend profile management and account deletion
- [ ] 01-10-PLAN.md — Frontend profile page

---

### Phase 2: Instagram Integration

**Goal:** Enable users to connect their Instagram accounts via OAuth with robust token management

**Requirements:**
- INSTA-01: OAuth connection flow
- INSTA-02: Multiple account support
- INSTA-03: Token auto-refresh
- INSTA-04: Connection status display
- INSTA-05: Reconnection flow
- INSTA-06: Account disconnection

**Success Criteria:**
1. User can authorize app via Instagram OAuth and see account connected
2. User can connect multiple Instagram accounts to one profile
3. Tokens automatically refresh before expiration without user intervention
4. User sees clear status for each connected account (active, expired, error)
5. User can reconnect expired accounts or disconnect accounts

**Dependencies:** Phase 1 (user auth required)

**Estimated Plans:** 5-7
- Instagram OAuth flow (backend endpoints)
- Token storage and encryption
- Token refresh job (background worker)
- Multiple account data model
- Connection status API endpoints
- Frontend Instagram connection UI
- Error handling and user notifications

---

### Phase 3: Core Scanning Engine

**Goal:** Build viral content discovery using third-party APIs with configurable parameters and URL analysis

**Requirements:**
- SCAN-01: On-demand scan trigger
- SCAN-02: Top 20 viral posts discovery
- SCAN-03: Configurable time ranges
- SCAN-04: Growth velocity calculation
- SCAN-05: Specific URL analysis
- SCAN-06: Post data extraction
- SCAN-07: Scan progress indicators
- SCAN-08: Error handling
- UX-01: Summary card view (basic display)
- UX-10: Thumbnail previews

**Success Criteria:**
1. User can trigger scan and system fetches top 20 posts by growth velocity
2. User can select time range (12h, 24h, 48h, 7d) for discovery
3. User can input specific Instagram URL for analysis
4. System calculates viral score based on engagement rate over time
5. Scan progress shows loading states, results display in summary cards with thumbnails

**Dependencies:** Phase 2 (Instagram connection required)

**Estimated Plans:** 7-9
- Third-party API integration (Apify primary)
- PhantomBuster fallback implementation
- Growth velocity algorithm
- URL parsing and single-post analysis
- Scan job orchestration (background workers)
- Scan result storage
- Frontend scan trigger UI
- Summary card component
- Loading/progress states

---

### Phase 4: AI Analysis - Algorithm Factors

**Goal:** Implement AI-powered analysis of core Instagram algorithm factors

**Requirements:**
- ANALYSIS-01: "Why viral" summary
- ANALYSIS-02: Posting time analysis
- ANALYSIS-03: Hook strength (video/reel first 3 seconds)
- ANALYSIS-04: Caption hook analysis
- ANALYSIS-05: Emotional trigger identification
- ANALYSIS-06: Pattern/template recognition
- ANALYSIS-07: Engagement velocity
- ANALYSIS-08: Save/share ratio
- ANALYSIS-09: Hashtag strategy analysis
- ANALYSIS-10: Audience retention (videos)
- ANALYSIS-11: Comment quality/sentiment

**Success Criteria:**
1. System generates comprehensive "why viral" summary using OpenAI GPT-4o
2. All 7 algorithm factors calculated and displayed for each post
3. Hook analysis includes first 3 seconds (video), caption opening, emotional trigger, pattern recognition
4. Engagement velocity, save/share ratio, hashtag performance quantified
5. Analysis results cached to minimize API costs

**Dependencies:** Phase 3 (scan data required)

**Estimated Plans:** 8-10
- OpenAI API integration
- Prompt engineering for viral analysis
- Hook analysis (video thumbnails + captions)
- Emotional trigger taxonomy
- Engagement velocity calculations
- Hashtag performance metrics
- Comment sentiment analysis
- Analysis caching layer
- Structured output validation
- Cost monitoring

---

### Phase 5: AI Analysis - Content Deep Dive

**Goal:** Extract and analyze audience insights and content categorization

**Requirements:**
- ANALYSIS-12: Audience demographics extraction
- ANALYSIS-13: Audience size display
- ANALYSIS-14: Engagement rate calculation
- ANALYSIS-15: Audience interest inference
- ANALYSIS-16: Instagram native type categorization
- ANALYSIS-17: Extended format categorization
- ANALYSIS-18: Niche auto-detection
- ANALYSIS-19: User niche refinement

**Success Criteria:**
1. System extracts and displays audience demographics (age, location, gender) where available
2. Engagement rate relative to follower count calculated for all posts
3. Audience interests inferred from niche, hashtags, content type
4. Content categorized by both Instagram native types and extended formats
5. AI auto-detects niche with user ability to refine/override

**Dependencies:** Phase 4 (analysis engine established)

**Estimated Plans:** 5-7
- Demographics extraction from Instagram data
- Engagement rate formulas
- Interest inference logic
- Content type taxonomy (native + extended)
- Niche detection with OpenAI
- User niche override UI
- Content categorization storage

---

### Phase 6: User Interface & Display

**Goal:** Build comprehensive UI for viewing and interacting with analyzed posts

**Requirements:**
- UX-02: Summary cards with key metrics
- UX-03: Detailed drill-down view
- UX-04: Complete analysis display
- UX-11: Link to original Instagram post

**Success Criteria:**
1. Summary cards show all key metrics (likes, comments, saves, shares, viral score, niche)
2. User can click any post to open detailed drill-down modal/page
3. Detailed view displays complete analysis (all algorithm factors, hook, audience, content type)
4. User can click through to view original Instagram post
5. UI is responsive and performant (renders 20 posts quickly)

**Dependencies:** Phases 4-5 (analysis data available)

**Estimated Plans:** 4-6
- Summary card component enhancement (add all metrics)
- Detailed analysis view component
- Drill-down modal/page routing
- Data visualization components (charts for trends)
- External link handling
- Responsive design polish

---

### Phase 7: Filtering & Search

**Goal:** Enable users to filter and search results to find relevant content

**Requirements:**
- UX-05: Filter by niche/category
- UX-06: Filter by content type
- UX-07: Filter by engagement metrics
- UX-08: Filter by account size
- UX-09: Search by keyword/creator/hashtag

**Success Criteria:**
1. User can apply multiple filters simultaneously (niche, type, engagement, account size)
2. Filters update results in real-time without page reload
3. User can search within results by keyword, creator name, or hashtag
4. Filter state persists across page navigation
5. Clear filter button resets all filters

**Dependencies:** Phase 6 (UI must exist to add filters)

**Estimated Plans:** 4-5
- Filter API endpoints (query builder)
- Filter UI components (dropdowns, ranges, multi-select)
- Search functionality (client-side or server-side)
- Filter state management
- Performance optimization (indexing)

---

### Phase 8: Export System

**Goal:** Enable users to export and share scan results in multiple formats

**Requirements:**
- EXPORT-01: PDF export
- EXPORT-02: Formatted PDF reports
- EXPORT-03: CSV/Excel export
- EXPORT-04: Raw data CSV
- EXPORT-05: Shareable link generation
- EXPORT-06: Public/password-protected links
- EXPORT-07: Link revocation

**Success Criteria:**
1. User can download scan results as formatted PDF report with charts
2. User can download raw data as CSV/Excel with all fields
3. User can generate shareable link (public or password-protected)
4. Shared links render same UI as authenticated users see
5. User can revoke/delete shareable links

**Dependencies:** Phase 6 (complete UI required for exports)

**Estimated Plans:** 6-7
- PDF generation service (ReportLab or WeasyPrint)
- CSV export endpoint
- Shareable link system (token generation, storage)
- Public share page (unauthenticated access)
- Password protection for links
- Link revocation API
- Export UI controls

---

### Phase 9: Historical Data & Trends

**Goal:** Store scan history and provide trend visualization over time

**Requirements:**
- HISTORY-01: Store all scans
- HISTORY-02: List past scans
- HISTORY-03: View past scan results
- HISTORY-04: Trend visualization
- HISTORY-05: Compare scans
- HISTORY-06: Trending niches/types
- HISTORY-07: Delete past scans

**Success Criteria:**
1. All scans stored indefinitely with timestamps
2. User sees chronological list of past scans
3. User can open any past scan and see identical results
4. Trend charts show viral pattern evolution (which niches trending up/down)
5. User can select two scans for side-by-side comparison

**Dependencies:** Phase 3 (scan storage), Phase 6 (display components)

**Estimated Plans:** 6-8
- Scan history list UI
- Scan archive viewer
- Time-series queries (TimescaleDB optimization)
- Trend visualization components (Recharts)
- Comparison view (side-by-side layout)
- Trending algorithms (growth over time)
- Delete scan functionality

---

### Phase 10: Subscription & Monetization

**Goal:** Implement subscription tiers with Stripe and enforce usage limits

**Requirements:**
- SUB-01: Free tier (5 scans/month)
- SUB-02: Enforce scan limits
- SUB-03: Display remaining scans
- SUB-04: Upgrade via Stripe
- SUB-05: Paid tier (50 scans/month, $20/month)
- SUB-06: Usage tracking
- SUB-07: Billing portal
- SUB-08: Webhook handling
- SUB-09: Email notifications
- SUB-10: Pricing page

**Success Criteria:**
1. Free tier users limited to 5 scans/month, enforced server-side
2. Paid tier users get 50 scans/month for $20/month
3. User sees remaining scans clearly displayed
4. User can upgrade seamlessly via Stripe Checkout
5. Stripe webhooks handled correctly (payment success, subscription canceled, etc.)
6. User can manage subscription via Stripe billing portal

**Dependencies:** Phase 1 (user system), Phase 3 (scans to meter)

**Estimated Plans:** 7-9
- Stripe integration (API keys, SDK)
- Subscription tier data model
- Usage tracking (scans per user per month)
- Limit enforcement middleware
- Stripe Checkout flow
- Webhook endpoint + handlers
- Billing portal link
- Pricing page UI
- Email notifications (subscription events)

---

### Phase 11: Polish & Launch Preparation

**Goal:** Finalize product with testing, optimization, and deployment

**Requirements:**
- Performance optimization
- Production deployment

**Success Criteria:**
1. All 79 v1 requirements verified complete
2. End-to-end testing completed (happy path + edge cases)
3. Performance optimized (page load <3s, API latency <2s)
4. Production deployment successful (Railway backend, Vercel frontend)
5. Monitoring and error tracking configured (Sentry)
6. Documentation complete (user guide, API docs)

**Dependencies:** Phases 1-10 (all features complete)

**Estimated Plans:** 5-6
- End-to-end testing suite
- Performance profiling and optimization
- Production environment setup
- Deployment automation (CI/CD)
- Monitoring setup (Sentry, logs)
- User documentation

---

## Milestone Success Criteria

v1.0 is complete when:

- ✓ User can sign up, connect Instagram, and trigger scans
- ✓ System discovers viral posts and explains why they went viral
- ✓ User can filter, search, and drill into detailed analysis
- ✓ User can export results as PDF, CSV, or shareable links
- ✓ User can track historical trends and compare scans
- ✓ Free and paid subscription tiers enforced
- ✓ All 79 v1 requirements verified ✓

---

*Roadmap created: 2026-02-15*
