# Instagram Viral Content Analyzer

## What This Is

A multi-user SaaS platform that helps content creators, marketers, and researchers understand what makes Instagram content go viral. Users connect their Instagram accounts to scan for the top 20 viral posts (by growth velocity) from the last 24 hours and receive AI-powered analysis explaining why each post succeeded, including detailed breakdowns of hooks, audience engagement, algorithm factors, and actionable patterns.

## Core Value

Users can identify and understand viral content patterns to create better performing Instagram content themselves.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User authentication and account management for the SaaS platform
- [ ] Instagram account connection for each user (OAuth integration)
- [ ] On-demand scan trigger to fetch top 20 viral posts by growth velocity (last 24 hours)
- [ ] Summary card view showing key metrics and viral factors for each post
- [ ] Detailed drill-down analysis for individual posts
- [ ] Comprehensive algorithm analysis covering 7 key factors: posting time optimization, content hook strength, engagement velocity, save/share ratio, hashtag strategy, audience retention, and comment quality/sentiment
- [ ] Post details extraction and analysis: hook (first 3 seconds, caption opening, emotional trigger, pattern/template), audience (demographics, follower count, engagement rate, inferred interests), content type (Instagram native + extended format categories), video length/duration, and niche categorization
- [ ] Filtering system by niche/category, content type, engagement metrics, and account size
- [ ] Export capabilities: PDF reports, CSV/Excel data export, and shareable links
- [ ] Niche detection: AI auto-suggest with user refinement option
- [ ] Historical data storage for tracking viral posts and trends over time
- [ ] Subscription tier system with free and paid plans

### Out of Scope

- Instagram posting or automation — Read-only analysis tool focused on insights, not content management
- Real-time continuous monitoring — On-demand scanning keeps costs manageable and gives users control
- Web scraping Instagram directly — Using third-party APIs instead to comply with ToS and ensure reliability
- Mobile native apps for v1 — Web-first approach, mobile apps deferred to future versions
- Direct Instagram Graph API integration — Limited to owned accounts; third-party APIs provide broader discovery

## Context

**Problem:** Content creators struggle to understand why certain Instagram posts go viral while others don't. The Instagram algorithm is opaque, and identifying patterns manually across viral content is time-consuming and requires domain expertise.

**Solution Approach:** Combine third-party Instagram data APIs (RapidAPI, Apify, or PhantomBuster) with OpenAI GPT-powered analysis and rule-based heuristics to provide both quantitative metrics and qualitative insights.

**Tech Environment:**
- Backend: Python with FastAPI framework
- Frontend: React for web interface
- AI Analysis: OpenAI GPT API for content analysis and pattern recognition
- Instagram Data: Third-party API services (not Instagram Graph API)
- Authentication: Each user connects their own Instagram account (distributes rate limiting across user base)

**Target Users:**
- Content creators wanting to improve their Instagram performance
- Marketing agencies tracking competitor content and trends
- Social media researchers studying virality patterns and algorithm behavior
- Consultants who package insights and reports for clients

## Constraints

- **Budget**: Cost-conscious architecture required for both API costs (OpenAI, Instagram data APIs) and infrastructure (hosting, database, storage). Design for efficiency and consider usage-based pricing to offset API costs.
- **Tech Stack**: Python FastAPI backend + React frontend (already decided based on user preference for Python data processing)
- **Data Access**: Dependent on third-party API reliability and rate limits; design with fallback strategies and rate limit handling
- **Instagram ToS Compliance**: Must use approved third-party APIs, not direct scraping, to avoid account bans or service disruption

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Third-party APIs for Instagram data | Instagram Graph API doesn't provide viral post discovery; third-party services aggregate this data legally while avoiding ToS violations from direct scraping | — Pending |
| Per-user Instagram authentication | Distributes rate limiting across user base, provides personalized discovery, enables future features like analyzing user's own content | — Pending |
| OpenAI GPT + rule-based heuristics | Combines quantitative metrics (heuristics) with qualitative insights (LLM) for comprehensive analysis that goes beyond simple engagement numbers | — Pending |
| Subscription tiers with free plan | Allows user acquisition through free tier while monetizing power users who need more scans and features; aligns with SaaS best practices | — Pending |
| Store historical data | Enables trend analysis and pattern recognition over time, adds significant value for users studying algorithm evolution | — Pending |
| Growth velocity as virality metric | More sophisticated than raw engagement numbers; identifies posts gaining traction fast, which signals algorithm boost | — Pending |

---
*Last updated: 2026-02-15 after initialization*
