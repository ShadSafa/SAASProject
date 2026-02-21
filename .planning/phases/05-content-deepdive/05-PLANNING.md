# Phase 05: Content Deepdive - Complete Planning

**Phase Goal:** Extract and analyze audience insights and content categorization to enrich viral post analysis with demographic data, engagement metrics, content categorization, and niche detection.

**Status:** Planning Phase Complete ✓

---

## Overview

Phase 05 adds audience insights (demographics, engagement rates, interests) and content categorization (Instagram native types, extended formats, niche detection) to the analysis system built in Phase 04. The phase introduces 3 new service layers that work together:

1. **Engagement Service** - Calculates engagement rate relative to follower count
2. **Categorization Service** - Classifies content by Instagram native type and extended formats
3. **Niche Detection Service** - AI-powered niche auto-detection using OpenAI GPT-4o

These services are integrated into the existing analysis workflow through enrichment functions, then exposed via updated UI components.

---

## Requirements Mapping

| Requirement | Plan | Description |
|------------|------|-------------|
| ANALYSIS-12 | 05-01, 05-07 | Audience demographics extraction (age, location, gender) |
| ANALYSIS-13 | 05-01, 05-07 | Audience size display (follower count) |
| ANALYSIS-14 | 05-02, 05-04, 05-07 | Engagement rate calculation |
| ANALYSIS-15 | 05-03, 05-04, 05-07 | Audience interest inference |
| ANALYSIS-16 | 05-03, 05-04, 05-07 | Instagram native type categorization |
| ANALYSIS-17 | 05-03, 05-04, 05-07 | Extended format categorization |
| ANALYSIS-18 | 05-05, 05-06 | Niche auto-detection (AI) |
| ANALYSIS-19 | Future (05-08) | User niche refinement UI |

---

## 7 Plans in 4 Waves

### Wave 1: Foundation (Parallel Execution)

**05-01: Audience Demographics Data Model & Migration**
- Extends Analysis model with new fields
- Creates database migration for audience_demographics, engagement_rate, audience_interests
- Key: Foundation for all subsequent enrichment

**05-02: Engagement Rate Calculation Service**
- Creates EngagementService with calculate_engagement_rate() function
- Formula: (likes + comments + saves + shares) / follower_count * 100
- Handles edge cases (zero followers)
- 100% test coverage with TDD approach

**Wave 1 Dependencies:** Both depend only on Phase 04 completion
**Wave 1 Duration:** Can run in parallel
**Wave 1 Output:** Database schema extended, engagement calculation service ready

---

### Wave 2: Content Classification (Sequential Dependency)

**05-03: Content Type Taxonomy & Categorization Logic**
- Defines 6 Instagram native types (Reel, Story, Post, Guide, Video, Carousel)
- Defines 23+ extended format categories (Tutorial, Comedy, ASMR, Educational, etc.)
- Implements categorize_content() with keyword-based format detection
- Calculates categorization confidence based on signal clarity

**05-04: Analysis Enrichment Service Integration**
- Creates analysis_enrichment_service.py with enrich_analysis_complete() orchestrator
- Integrates engagement calculation (05-02)
- Integrates content categorization (05-03)
- Updates analysis_jobs.py to call enrichment after OpenAI analysis
- Ensures enrichment failures don't break analysis (graceful degradation)

**Wave 2 Dependencies:** 05-04 depends on 05-01, 05-02, 05-03
**Wave 2 Duration:** Sequential (05-03 first, then 05-04)
**Wave 2 Output:** All posts enriched with engagement + categorization data

---

### Wave 3: Niche Detection (Parallel to Wave 2)

**05-05: Niche Detection Service (OpenAI Integration)**
- Uses same structured output pattern as Phase 04-01
- Implements detect_niche() using OpenAI GPT-4o with Pydantic models
- Defines 30+ niche options (Fitness, Fashion, Technology, etc.)
- Returns NicheDetectionResult with confidence score
- Graceful fallback to "Other" niche on API failure

**05-06: Niche Detection Workflow Integration**
- Integrates niche detection into analysis enrichment
- Updates enrich_analysis_complete() to call enrich_analysis_with_niche()
- Stores niche in Analysis.niche field
- Stores niche metadata (confidence, reasoning, keywords) in audience_interests JSON
- Updates frontend Analysis TypeScript interface with Phase 05 fields

**Wave 3 Dependencies:** 05-06 depends on 05-01, 05-04, 05-05
**Wave 3 Duration:** Can run partially in parallel with Wave 2 (05-05 independent)
**Wave 3 Output:** All posts auto-detected with niche classification

---

### Wave 4: UI Integration (Dependent on All Previous)

**05-07: Analysis UI Enhancement for New Fields**
- Creates EngagementMetricsCard component (3-column layout, color-coded rates)
- Creates NicheBadge component (confidence indicator)
- Creates ContentCategoryBadges component (native type + extended formats)
- Creates audience demographics section (age, gender, location display)
- Updates AnalysisPanel to display all enriched fields
- Follows Phase 04 design patterns (Tailwind CSS)

**Wave 4 Dependencies:** 05-07 depends on 05-01, 05-04, 05-06
**Wave 4 Duration:** Single execution (depends on backend)
**Wave 4 Output:** Full Phase 05 feature complete and visible to users

---

## Parallel Execution Strategy

```
Wave 1: ━━━━━━━━━━━━━ (5-02) Can run independently
        ━━━━━━━━━━━━━ (05-01) Can run independently
                       ↓
Wave 2: ━━━━━━━━━━━━━ (05-03)
                       ↓
        ━━━━━━━━━━━━━ (05-04)
                       ↓
Wave 3:        ━━━━━━━━━━━━━ (05-05) Can run independently
                            ↓
               ━━━━━━━━━━━━━ (05-06) Depends on 05-04, 05-05
                            ↓
Wave 4:        ━━━━━━━━━━━━━ (05-07) Depends on all above
```

**Estimated Timeline:**
- Wave 1: 2-3 hours (both plans parallel)
- Wave 2: 3-4 hours (sequential execution)
- Wave 3: 2-3 hours (05-05 parallel, 05-06 sequential)
- Wave 4: 2-3 hours (UI component creation)
- **Total: 9-13 hours** (with parallelization: 4-6 hours critical path)

---

## Tech Stack & Patterns

### Backend
- **OpenAI Integration:** Structured output with Pydantic (like Phase 04)
- **Service Pattern:** Separate services for each concern (engagement, categorization, niche)
- **Enrichment Pattern:** Orchestrator function chains services
- **Error Handling:** Graceful degradation (optional enrichment failures don't break analysis)
- **Testing:** TDD approach with mocked OpenAI/services

### Frontend
- **Components:** Reusable cards following Phase 04 patterns
- **Styling:** Tailwind CSS with color-coding for metrics
- **Types:** Full TypeScript support with extended Analysis interface
- **Hooks:** useAnalysis hook automatically supports new fields

### Database
- **Migrations:** Alembic for schema updates
- **JSON Fields:** audience_demographics, audience_interests for flexible metadata
- **Nullable:** All Phase 05 fields nullable (graceful handling of missing data)

---

## Success Criteria

### Data Layer (05-01)
- Analysis model extended with new fields
- Database migration creates/updates columns
- No Phase 04 fields modified
- ORM correctly persists/retrieves enriched data

### Engagement Service (05-02)
- Engagement rate calculated correctly: (interactions / followers) * 100
- Handles zero followers (returns 0, no crash)
- 100% test coverage, zero API calls

### Categorization Service (05-03)
- 6+ Instagram native types, 23+ extended formats
- Keyword-based format detection working
- Confidence scoring reflects signal clarity
- All formats testable with mock data

### Enrichment Integration (05-04, 05-05, 05-06)
- All enrichment services called by enrich_analysis_complete()
- Services chain without circular imports
- Enrichment failures handled gracefully
- Analysis saved even if enrichment partially fails
- All tests pass

### Niche Detection (05-05)
- Structured output from OpenAI working (like Phase 04)
- 30+ niches available
- Confidence score 0.0-1.0
- Fallback to "Other" niche on API failure

### UI (05-07)
- Engagement rate displays with color coding
- Niche displays with confidence badge
- Content type badges show native + extended formats
- Demographics display when available (age, gender, location)
- All components responsive (mobile-first)
- No breaking changes to Phase 04 UI

### E2E Verification
- User can view engagement rate for at least 1 post
- User can see detected niche and confidence
- User can see content type classification
- User can see audience demographics (where available)
- No console errors or API failures
- All 10 Phase 04 tests still pass (no regression)

---

## Risk Mitigation

| Risk | Mitigation | Plan |
|------|-----------|------|
| OpenAI API failures during niche detection | Graceful fallback to "Other" niche with low confidence | 05-05 |
| Missing audience demographics data | Fields nullable, UI handles missing data gracefully | 05-01, 05-07 |
| Enrichment slow down analysis tasks | Run enrichment after OpenAI, cache results, optional | 05-04 |
| Circular imports between services | Lazy imports in functions, clear dependency graph | All |
| TypeScript type mismatches | Frontend Analysis interface updated before UI work | 05-06 |
| Edge cases (zero followers, no hashtags) | Comprehensive testing with boundary conditions | All |

---

## Post-Phase 05 Roadmap

**Future Plans (05-08+):**
- **05-08:** User niche refinement UI (override AI suggestion) — ANALYSIS-19
- **05-09:** Save audience insights to user preferences for filtering
- **05-10:** Audience interest inference API endpoint
- **06-01:** Filtering system by niche/category (Phase 06)
- **06-02:** Historical trend analysis by niche
- **06-03:** Export capabilities with new fields

---

## Autonomous Execution

All 7 plans are **autonomous** (can be executed independently with proper dependency order):
- Each plan has clear objectives, measurable success criteria, test coverage
- No human checkpoints required between plans
- Errors and edge cases documented with fallback strategies
- Test coverage ensures quality gates

**Execution Order (to respect dependencies):**
1. Execute 05-01 (foundation)
2. Execute 05-02 and 05-03 in parallel
3. Execute 05-04 (depends on 05-02, 05-03)
4. Execute 05-05 in parallel with 05-04
5. Execute 05-06 (depends on 05-04, 05-05)
6. Execute 05-07 (depends on 05-06)
7. Run comprehensive UAT (all 10 Phase 04 tests + 10+ Phase 05 tests)

---

## Summary

Phase 05 adds intelligence to the analysis system by enriching viral posts with:
- **Engagement metrics** relative to follower count
- **Content categorization** by type and format
- **AI-detected niche** with confidence scoring
- **Audience demographics** where available
- **Inferred audience interests** from content analysis

The 7 plans organize this work into logical waves, each building on Phase 04's foundation. The phased approach enables parallel execution while maintaining clear dependencies. All plans include comprehensive testing and graceful error handling to ensure robust operation in production.

**Phase 05 is ready for execution.**
