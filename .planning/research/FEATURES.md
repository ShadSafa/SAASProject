# Features Research: Instagram Viral Content Analyzer

**Research Date:** 2026-02-15
**Domain:** Social Media Analytics SaaS
**Context:** Viral content discovery and AI-powered analysis platform

---

## Table Stakes Features

These features are **mandatory** - users expect them in any social media analytics SaaS. Missing these = immediate churn.

### User Management (Complexity: Low)
- Email/password signup and login
- Email verification
- Password reset flow
- User profile management
- Session persistence

**Rationale:** Basic security and UX hygiene. Users won't trust a platform without proper auth.

### Instagram Account Connection (Complexity: Medium)
- OAuth integration with Instagram
- Multiple account support (optional, but nice-to-have)
- Account re-authentication handling (when tokens expire)
- Clear connection status indicators

**Rationale:** Core functionality - can't analyze Instagram without access.

### Content Discovery (Complexity: High)
- Scan trigger (on-demand)
- Top N viral posts by growth velocity
- Time range filtering (last 24h standard)
- Loading states and progress indicators

**Rationale:** The core value proposition.

### Basic Data Display (Complexity: Medium)
- List/grid view of discovered posts
- Post thumbnail preview
- Basic engagement metrics (likes, comments, shares, saves)
- Creator information (username, follower count)
- Link to original Instagram post

**Rationale:** Users need to see what was found before diving into analysis.

### Analysis Results (Complexity: High)
- "Why it went viral" summary
- Key metrics breakdown
- Hook analysis
- Audience insights
- Algorithm factors

**Rationale:** The differentiating value - raw data alone isn't enough.

---

## Differentiators

These features **set you apart** from competitors. Pick the right ones for v1, defer others to v2.

### AI-Powered Hook Analysis (Complexity: High) ⭐
- First 3 seconds/opening frame analysis
- Caption opening line extraction
- Emotional trigger identification
- Pattern/template recognition

**Rationale:** Unique insight competitors don't provide. GPT excels at this.

**Dependencies:** OpenAI API integration, image/video processing

**v1 Priority:** ✓ High - core differentiator

### Advanced Filtering System (Complexity: Medium) ⭐
- Filter by niche/category
- Filter by content type (Reels, Carousels, etc.)
- Filter by engagement thresholds
- Filter by account size ranges

**Rationale:** Power users need to focus on relevant content for their niche.

**Dependencies:** Good data structure, search/filter UI

**v1 Priority:** ✓ High - requested by users

### Multi-Format Export (Complexity: Medium) ⭐
- PDF report generation
- CSV/Excel data export
- Shareable links (public or authenticated)

**Rationale:** Consultants/agencies need to share insights with clients.

**Dependencies:** Report templating, file storage

**v1 Priority:** ✓ Medium-High - enables B2B use case

### Historical Trend Tracking (Complexity: High) ⭐
- Store all scan results
- Compare scans over time
- Trend visualization (what's working this week vs last week)
- Pattern evolution tracking

**Rationale:** One-time scans are useful; trend data is invaluable.

**Dependencies:** Time-series database, charting library

**v1 Priority:** ⚠️ Medium - adds retention but complex

### Niche Auto-Detection with AI (Complexity: High) ⭐
- AI suggests niche/category
- User can refine/override
- Learn from user corrections

**Rationale:** Manual categorization is tedious; AI saves time.

**Dependencies:** OpenAI API, good prompt engineering

**v1 Priority:** ⚠️ Medium - nice-to-have, not critical path

### Subscription Tier System (Complexity: Medium)
- Free tier (limited scans/month)
- Paid tiers (more scans + premium features)
- Usage tracking and limits enforcement
- Billing portal

**Rationale:** Required for monetization, standard SaaS practice.

**Dependencies:** Stripe integration

**v1 Priority:** ✓ High - needed for launch if monetizing

### Comprehensive Algorithm Analysis (Complexity: High) ⭐
- Posting time optimization insights
- Engagement velocity metrics
- Save/share ratio analysis
- Hashtag performance breakdown
- Audience retention (for videos)
- Comment quality/sentiment

**Rationale:** Deep insights justify premium pricing.

**Dependencies:** OpenAI API, comprehensive data extraction

**v1 Priority:** ✓ High - core value proposition

---

## Anti-Features

Features to **deliberately avoid** - they seem useful but create problems.

### Instagram Posting/Automation ❌
**Why avoid:** Scope creep, ToS risk, shifts focus from analytics to content management. Many tools already do this.

**Alternative:** Stay focused on insights/analysis, not execution.

### Real-Time Continuous Monitoring ❌
**Why avoid:** Expensive (constant API calls), complex infrastructure, limited user value for "on-demand" use case.

**Alternative:** On-demand scanning is sufficient and cost-effective.

### Native Mobile Apps ❌
**Why avoid:** 2x development effort (iOS + Android), maintenance burden, web responsive is good enough for MVP.

**Alternative:** Progressive Web App (PWA) for mobile experience.

### Direct Instagram Scraping ❌
**Why avoid:** ToS violations, account ban risk, fragile (breaks when Instagram changes UI), legal liability.

**Alternative:** Use approved third-party APIs (Apify, PhantomBuster).

### Unlimited Free Tier ❌
**Why avoid:** API costs scale with usage - unlimited free = unsustainable burn.

**Alternative:** Generous but capped free tier (e.g., 5 scans/month).

---

## Feature Complexity Matrix

| Feature | Complexity | v1 Priority | Dependencies |
|---------|-----------|-------------|--------------|
| User auth | Low | ✓ Critical | Supabase/Auth0 |
| Instagram OAuth | Medium | ✓ Critical | Instagram API |
| Viral content scan | High | ✓ Critical | Third-party API |
| Basic display | Medium | ✓ Critical | React, UI library |
| AI analysis | High | ✓ Critical | OpenAI API |
| Hook analysis | High | ✓ High | OpenAI Vision |
| Filtering | Medium | ✓ High | Good data model |
| Exports (PDF/CSV) | Medium | ✓ Medium-High | Templating engine |
| Shareable links | Low | ⚠️ Medium | URL routing |
| Historical tracking | High | ⚠️ Medium | Time-series DB |
| Niche auto-detect | High | ⚠️ Medium | OpenAI API |
| Subscription tiers | Medium | ✓ High | Stripe |
| Algorithm analysis | High | ✓ High | OpenAI + data |

---

## Recommended v1 Scope

**Include:**
- Complete user auth flow
- Instagram account connection
- On-demand viral content scanning (top 20 posts, 24h)
- Summary + drill-down analysis views
- AI-powered "why viral" analysis with 7 algorithm factors
- Hook + audience + content type analysis
- Filtering by niche, type, engagement, account size
- PDF + CSV export
- Subscription tiers (free + paid)

**Defer to v2:**
- Shareable link generation
- Historical trend visualization
- Advanced niche learning/ML
- Email reports
- Team/workspace features
- API access for power users

---

*This feature set balances ambitious vision with realistic v1 scope.*
