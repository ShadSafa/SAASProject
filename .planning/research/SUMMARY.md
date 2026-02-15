# Research Summary: Instagram Viral Content Analyzer

**Generated:** 2026-02-15
**Project:** Multi-user SaaS for Instagram viral content analysis with AI insights

---

## Executive Summary

Building an Instagram viral content analyzer requires balancing **powerful features** with **cost control**. The recommended stack (FastAPI + React + PostgreSQL + Apify + OpenAI) provides the right mix of performance, developer experience, and budget efficiency.

**Key insight:** Third-party API dependency and AI costs are the biggest risks. Mitigation through caching, fallbacks, and usage limits is critical from day 1.

---

## Recommended Stack (from STACK.md)

### Core Technologies
- **Backend:** Python FastAPI 0.110+
- **Frontend:** React 18+ with Vite, TypeScript, Tremor UI
- **Database:** PostgreSQL 16 with TimescaleDB extension
- **Instagram Data:** Apify (primary) + PhantomBuster (fallback)
- **AI Analysis:** OpenAI GPT-4o
- **Infrastructure:** Railway (backend/DB) + Vercel (frontend)

### Cost Projection
- **100 users, 10 scans/user/month:** $100-180/month
- **Target subscription:** $20/user/month = $2000 revenue
- **Healthy margin** if costs stay controlled

**Confidence:** ✓ High for all core tech choices

---

## Table Stakes Features (from FEATURES.md)

These are **mandatory** for v1 launch:

1. ✓ User auth (email/password, verification, reset)
2. ✓ Instagram OAuth integration
3. ✓ On-demand viral post scanning (top 20, 24h, growth velocity)
4. ✓ Basic post display (thumbnail, metrics, creator info)
5. ✓ AI-powered "why viral" analysis
6. ✓ Hook analysis (opening, caption, emotion, pattern)
7. ✓ Audience insights (demographics, follower count, engagement rate)
8. ✓ Algorithm factor analysis (7 factors: posting time, hook, velocity, save/share, hashtags, retention, comments)
9. ✓ Filtering (niche, content type, engagement, account size)
10. ✓ Export (PDF, CSV)
11. ✓ Subscription tiers (free + paid)

**Defer to v2:**
- Shareable links
- Historical trend visualization
- Team/workspace features
- Email reports
- API access

---

## Architecture Highlights (from ARCHITECTURE.md)

### Build Order (Critical Path)
1. **Phase 1:** Database + User Auth + Frontend auth pages
2. **Phase 2:** Instagram OAuth + Apify integration + Basic scanning
3. **Phase 3:** OpenAI integration + Analysis engine + Display
4. **Phase 4:** Filtering + Drill-down + Exports
5. **Phase 5:** Stripe + Subscriptions + Usage limits

### Data Flow
```
User triggers scan → Backend creates job → Queue worker fetches posts (Apify)
→ Analysis worker calls OpenAI → Store results → Frontend displays
```

### Scalability
- **v1 (0-1000 users):** Single backend instance sufficient
- **Future:** Horizontal scaling + read replicas + Redis caching

---

## Critical Pitfalls to Avoid (from PITFALLS.md)

### Top 5 Risks

1. **Runaway AI costs** 💸
   - Cache analysis for 7 days
   - Batch OpenAI calls
   - Monitor spend daily

2. **Third-party API dependency** ⚠️
   - Build abstraction layer
   - Implement Apify + PhantomBuster fallback
   - Circuit breaker pattern

3. **Instagram OAuth token expiration** 🔒
   - Proactive refresh (check expiry before scans)
   - Clear error messages
   - User notifications

4. **Insufficient usage limits** 💣
   - Hard caps: Free tier = 5 scans/month
   - Rate limiting: 1 scan per 5 min
   - Email verification required

5. **Poor performance** 🐌
   - Pagination (10 posts at a time)
   - Database indexing
   - Lazy loading for details

### Unit Economics Warning
- **Target:** $0.30/scan (Instagram API + OpenAI + infrastructure)
- **Reality check:** May need $30/month minimum subscription, not $20
- **Mitigation:** Aggressive caching, batching, usage caps

---

## Key Decisions to Make

### Before Phase 1
- [ ] Choose specific Apify actor/API endpoint
- [ ] Design viral score formula (growth velocity calculation)
- [ ] Define free tier limits (5 scans/month confirmed?)
- [ ] Select UI component library (Tremor vs shadcn/ui vs both)

### Before Phase 3
- [ ] OpenAI prompt engineering for analysis
- [ ] Structured output schema design
- [ ] Hook analysis taxonomy (emotional triggers list)

### Before Phase 5
- [ ] Stripe pricing model (monthly vs usage-based)
- [ ] Tier structure (# of tiers, limits per tier)
- [ ] Trial period (if any)

---

## Success Metrics

**Technical:**
- API latency <2s for scan trigger
- Analysis quality score >4/5 (user survey)
- Uptime >99.5%

**Business:**
- Free→Paid conversion >5%
- Monthly churn <10%
- User satisfaction (NPS) >40

**Cost:**
- COGS <40% of revenue
- OpenAI costs <15% of revenue

---

## Immediate Next Steps

1. **Define requirements** based on this research
2. **Scope v1** using table stakes features
3. **Create roadmap** following build order (5 phases recommended)
4. **Plan Phase 1:** Foundation (DB + Auth + Frontend)

---

## References

Research drew from:
- [Best Web Development Stacks for SaaS (2026)](https://penninetechnolabs.com/blog/web-development-stacks/)
- [FastAPI Best Practices (2026)](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026)
- [React Admin Dashboard Guide (2026)](https://refine.dev/blog/react-admin-dashboard/)
- [Social Media Scraping APIs (2026)](https://sociavault.com/blog/best-social-media-scraping-apis-2026)
- [Apify Instagram Scraper](https://apify.com/apidojo/instagram-scraper-api)

---

**This research provides a comprehensive foundation for requirements definition and roadmap creation.**
