# Stack Research: Instagram Viral Content Analyzer

**Research Date:** 2026-02-15
**Domain:** Instagram Analytics SaaS with AI-Powered Insights
**Context:** Greenfield project, budget-conscious, Python FastAPI + React

---

## Recommended Stack

### Backend: Python + FastAPI

**Choice:** FastAPI 0.110+ (current stable in 2026)

**Rationale:**
- **Async performance**: Native async/await support critical for concurrent API calls (Instagram data + OpenAI)
- **Fast development**: Auto-generated API docs, type hints, dependency injection
- **Cost efficiency**: Better performance per dollar than Django for API-heavy workloads
- **AI ecosystem**: Seamless integration with Python ML/AI libraries

**Confidence:** ✓ High - Industry standard for AI-powered SaaS in 2026

**What NOT to use:**
- Flask: Lacks native async, slower development
- Django: Overkill for API-first architecture, heavier footprint

### Frontend: React 18+ with Modern Tooling

**Choice:**
- React 18.3+ with Vite 5+ (build tool)
- TypeScript for type safety

**Rationale:**
- **Component ecosystem**: Rich dashboard/chart libraries (Tremor, Recharts, Victory)
- **Performance**: React 18 concurrent features + Vite's fast HMR
- **Cost**: Vite reduces build times = faster iteration = lower dev costs

**Confidence:** ✓ High - Dominant choice for analytics dashboards

**UI Component Libraries:**
- **Tremor** (recommended): 35+ open-source dashboard components, built on Tailwind + Radix UI
- **Recharts 3.0**: Mature charting library, 2025 update added accessibility + animations
- **shadcn/ui**: Copy-paste components, full control, no bundle bloat

**What NOT to use:**
- Next.js: Overkill for SPA, SSR not needed for authenticated dashboard
- Heavy admin templates: Pre-built but inflexible, hard to customize

### Database: PostgreSQL 16+

**Choice:** PostgreSQL 16 with TimescaleDB extension (for time-series data)

**Rationale:**
- **Cost efficiency**: Open-source, no licensing fees
- **JSON support**: Store flexible Instagram post data structures
- **TimescaleDB**: Optimized for historical viral post tracking (time-series queries)
- **Reliability**: Battle-tested for SaaS applications

**Confidence:** ✓ High

**What NOT to use:**
- MongoDB: Higher managed hosting costs, weaker consistency guarantees
- MySQL: Inferior JSON handling, weaker for analytics workloads

### Instagram Data API: Third-Party Aggregators

**Choice:** Apify (primary) + PhantomBuster (backup)

**Rationale:**
- **Legal compliance**: Avoids Instagram ToS violations from direct scraping
- **Reliability**: Apify handles 4-5M requests/day, professional SLA
- **Cost control**: Pay-per-use pricing aligns with usage-based business model
- **Viral discovery**: These APIs aggregate trending/viral content metrics not available via Instagram Graph API

**Pricing considerations:**
- Apify: ~$0.01-0.05 per profile/post scraped (varies by plan)
- PhantomBuster: $30-400/month depending on volume

**Confidence:** ⚠️ Medium - Third-party APIs have rate limits and cost unpredictability

**What NOT to use:**
- Instagram Graph API: Only accesses owned accounts, no viral discovery
- Direct web scraping: ToS violation risk, fragile, account ban risk
- RapidAPI generic scrapers: Quality inconsistent, many unmaintained

### AI Analysis: OpenAI GPT-4o

**Choice:** OpenAI GPT-4o (cost-optimized model)

**Rationale:**
- **Cost efficiency**: GPT-4o is 50% cheaper than GPT-4 Turbo
- **Quality**: Strong content analysis for hooks, sentiment, patterns
- **Vision support**: Can analyze image/video thumbnails for hook analysis

**Pricing:** ~$2.50 per 1M input tokens, $10 per 1M output tokens

**Confidence:** ✓ High

**Cost optimization strategies:**
- Batch analysis requests
- Cache common pattern analyses
- Use structured outputs to minimize tokens

**What NOT to use:**
- Claude (Anthropic): More expensive, less vision support
- Local LLMs: Infrastructure costs outweigh API savings at scale

### Infrastructure & Hosting

**Choice:**
- **Backend**: Railway or Render (PaaS)
- **Frontend**: Vercel or Netlify
- **Database**: Supabase (PostgreSQL managed) or Railway
- **File storage**: Cloudflare R2 (S3-compatible, cheaper egress)

**Rationale:**
- **Cost**: Railway/Render offer free tiers + affordable scaling
- **Simplicity**: Managed infrastructure reduces DevOps overhead
- **Performance**: Global CDN for frontend assets

**Confidence:** ✓ High for MVP, revisit at scale

**What NOT to use:**
- AWS/GCP raw: Overkill complexity, higher costs for small teams
- Heroku: More expensive than Railway/Render

### Authentication & Payments

**Auth:** Supabase Auth or Auth0 (free tier)
**Instagram OAuth:** Instagram Basic Display API (free)
**Payments:** Stripe (industry standard)

**Rationale:**
- Supabase Auth: Free, integrates with PostgreSQL
- Stripe: Best developer experience, transparent pricing

---

## Development Tools

- **API documentation**: FastAPI auto-generated OpenAPI docs
- **Testing**: pytest (backend), Vitest (frontend)
- **Type checking**: mypy (Python), TypeScript
- **Code quality**: Ruff (Python linting), ESLint + Prettier (JS/TS)

---

## Cost Projection (Monthly, 100 users, 10 scans/user/month)

| Service | Estimated Cost |
|---------|----------------|
| Apify (1000 scans) | $50-100 |
| OpenAI GPT-4o | $30-60 |
| Railway (backend + DB) | $20 |
| Vercel (frontend) | $0 (free tier) |
| Supabase Auth | $0 (free tier) |
| **Total** | **$100-180/month** |

At $20/user/month subscription = $2000/month revenue = healthy margin.

---

## Sources

- [Best Web Development Stacks for SaaS Startups Guide 2026](https://penninetechnolabs.com/blog/web-development-stacks/)
- [FastAPI Best Practices for Production: Complete 2026 Guide](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026)
- [React Admin Dashboard - Best Templates & Frameworks (2026 Guide)](https://refine.dev/blog/react-admin-dashboard/)
- [Tremor – Tailwind CSS UI Components for Charts and Dashboards](https://www.tremor.so/)
- [The Ultimate Guide to the Best Social Media Scraping APIs in 2026](https://sociavault.com/blog/best-social-media-scraping-apis-2026)
- [Fast Instagram Scraper API - Apify](https://apify.com/apidojo/instagram-scraper-api)

---

*Confidence levels: ✓ High (proven) | ⚠️ Medium (workable, monitor) | ✗ Low (risky)*
