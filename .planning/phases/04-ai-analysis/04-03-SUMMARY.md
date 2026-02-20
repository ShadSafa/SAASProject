---
phase: 04
plan: 03
subsystem: AI Analysis - Background Task Worker
tags:
  - celery
  - async-tasks
  - cache-integration
  - openai
  - background-jobs
dependency_graph:
  requires:
    - "04-01: OpenAI SDK Integration"
    - "04-02: Redis Caching Layer"
    - "03-05: Scan Job Orchestration (Celery app setup)"
  provides:
    - "analyze_posts_batch: Celery task for batch analysis"
    - "Cache-before-OpenAI pattern for cost optimization"
  affects:
    - "04-04: Analysis Result Caching Integration"
    - "Scan workflow: will dispatch analysis tasks after scan completion"
tech_stack:
  added:
    - "Celery task: analyze_posts_batch with cache-first strategy"
    - "Async/await pattern inside Celery task (asyncio.run wrapper)"
    - "Per-post error handling with graceful degradation"
  patterns:
    - "Cache-before-API for cost optimization (OpenAI calls cost $0.01-0.10 each)"
    - "Fire-and-forget task dispatch from FastAPI routes"
    - "SQLAlchemy async session within sync Celery task"
key_files:
  created:
    - backend/app/tasks/analysis_jobs.py (140 lines, analyze_posts_batch task)
    - backend/tests/test_analysis_jobs.py (227 lines, 9 test cases)
  modified:
    - none
decisions:
  - "asyncio.run() wrapper needed because Celery tasks are sync but we use async SQLAlchemy"
  - "Per-post error handling prevents single post failure from aborting entire batch"
  - "Cache checked before every OpenAI call (even if DB has Analysis record)"
  - "Task returns summary dict with analyzed/cached/failed counts for monitoring"
metrics:
  duration: 5 minutes
  completed_date: "2026-02-21"
  tasks_completed: 2
  files_created: 2
  test_coverage: 9 test cases (all passing)
---

# Phase 04 Plan 03: Celery Background Tasks for AI Analysis Summary

Cache-first Celery task for viral post analysis with OpenAI integration and per-post error handling.

## Objective

Create `analyze_posts_batch` Celery task that processes viral posts in the background without blocking FastAPI endpoints. Task checks Redis cache first (cost optimization), calls OpenAI on cache miss, and stores results in both database and cache.

## What Was Built

### Task 1: analyze_posts_batch Celery Task (140 lines)

**File:** `backend/app/tasks/analysis_jobs.py`

**Key Features:**
- Registered as `analysis.analyze_posts_batch` with Celery
- Accepts `scan_id` (int) and `viral_post_ids` (list[int])
- Per-post analysis loop with try/except error handling
- Cache-first strategy: get_cached_analysis() before OpenAI call
- Creates Analysis ORM records from both cached and fresh results
- Stores results in Redis cache with 7-day TTL
- Returns summary: `{"analyzed": int, "cached": int, "failed": int}`

**Cache Integration:**
- Check: `get_cached_analysis(post_id)` returns ViralAnalysisResult
- Miss: Call `analyze_viral_post(viral_post)` -> ViralAnalysisResult from OpenAI
- Store: `cache_analysis(post_id, result)` -> Redis with 7-day TTL

**Error Handling:**
- Wraps each post in try/except
- Logs error but continues to next post
- Failed posts tracked in return summary
- Task always completes successfully (errors don't fail task)

**Async Implementation:**
- Uses `asyncio.run(_run_analysis(...))` pattern from Phase 3
- Manages AsyncSessionLocal for DB operations
- Commits all Analysis records at end of batch

### Task 2: Test Suite (227 lines, 9 test cases)

**File:** `backend/tests/test_analysis_jobs.py`

**Test Coverage:**

1. **test_analyze_posts_batch_registered** - Verify task name is 'analysis.analyze_posts_batch'
2. **test_analyze_posts_batch_all_cache_hits** - All posts cached, 0 OpenAI calls, 3 Analysis records
3. **test_analyze_posts_batch_all_cache_misses** - No cache hits, 3 OpenAI calls, 3 cache_analysis() calls
4. **test_analyze_posts_batch_mixed_cache_hits_and_misses** - 2 cached, 1 OpenAI call
5. **test_analyze_posts_batch_handles_openai_error** - Mock error for 1 post, other 2 succeed
6. **test_analyze_posts_batch_empty_list** - viral_post_ids=[], returns {"analyzed": 0, "cached": 0, "failed": 0}
7. **test_analyze_posts_batch_task_failure_returns_failed_count** - Graceful failure handling
8. **test_analyze_posts_batch_result_schema** - Verify result dict has required keys
9. **test_analyze_posts_batch_large_batch** - Stress test with 50 posts

**Testing Strategy:**
- All mocked dependencies: no real OpenAI API calls, no real Redis
- Tests complete in <3 seconds
- Fixtures for mock viral posts, OpenAI results, cache results

## Verification

**All checks pass:**

```bash
# Load task from Python
python -c "from app.tasks.analysis_jobs import analyze_posts_batch; \
           print('Analysis task loaded:', analyze_posts_batch.name)"
# Output: Analysis task loaded: analysis.analyze_posts_batch

# Run test suite
pytest backend/tests/test_analysis_jobs.py -v
# Output: 9 passed in 2.29s
```

## Success Criteria Met

- [x] `analyze_posts_batch` Celery task registered and callable
- [x] Task checks cache before calling OpenAI (cost optimization)
- [x] Cache hits skip OpenAI entirely (no wasted API credits)
- [x] Analysis results stored in PostgreSQL (Analysis model) and Redis (7-day cache)
- [x] Error handling prevents single post failure from aborting batch
- [x] Test suite passes with mocked dependencies (no real API calls)
- [x] Task returns summary dict with analyzed/cached/failed counts
- [x] Ready to integrate with scan workflow in next task

## Deviations from Plan

None - plan executed exactly as written.

## Architecture Notes

**Why cache before API?**
- OpenAI calls: ~2-5 seconds, ~$0.01-0.10 per call
- Cache hit: <10ms, $0.00
- Expected cache hit rate: ~60% (same posts repeated across scans)
- Annual cost reduction: ~$10k with 85% hit rate (same math as Phase 4.2)

**Why asyncio.run() in Celery task?**
- Celery workers are synchronous (no event loop)
- FastAPI uses async SQLAlchemy (needs event loop)
- Pattern: task calls asyncio.run() to create event loop for async DB operations
- Standard for mixing Celery + async ORMs (confirmed in Phase 3.5)

**Why per-post error handling?**
- 20 posts per scan, 1 API error shouldn't fail all 20
- Log error, skip to next post, continue processing
- Better UX: user gets 19 analyses + 1 failed, not 0 analyses

## Next Phase

Task ready for integration in Phase 4.4 (Analysis Result Caching Integration) where:
1. Scan completion will trigger `analyze_posts_batch.delay(scan_id, viral_post_ids)`
2. ScanStatus polling will wait for analysis task completion
3. Frontend will display results once both scan + analysis complete

## Files Summary

| File | Lines | Type | Status |
|------|-------|------|--------|
| backend/app/tasks/analysis_jobs.py | 140 | Task Implementation | NEW |
| backend/tests/test_analysis_jobs.py | 227 | Test Suite | NEW |

## Test Results

```
======================== 9 passed in 2.29s ========================
test_analyze_posts_batch_registered PASSED
test_analyze_posts_batch_all_cache_hits PASSED
test_analyze_posts_batch_all_cache_misses PASSED
test_analyze_posts_batch_mixed_cache_hits_and_misses PASSED
test_analyze_posts_batch_handles_openai_error PASSED
test_analyze_posts_batch_empty_list PASSED
test_analyze_posts_batch_task_failure_returns_failed_count PASSED
test_analyze_posts_batch_result_schema PASSED
test_analyze_posts_batch_large_batch PASSED
```

All tests use mocked dependencies. No real API or Redis calls.

## Self-Check: PASSED

- [x] backend/app/tasks/analysis_jobs.py exists (140 lines, min 80)
- [x] backend/tests/test_analysis_jobs.py exists (227 lines, min 50)
- [x] analyze_posts_batch function exported from analysis_jobs.py
- [x] @celery_app.task decorator applied
- [x] analyze_viral_post() called (OpenAI integration)
- [x] get_cached_analysis() called (cache integration)
- [x] 9 test functions (min 6)
- [x] All tests passing
- [x] Task name: analysis.analyze_posts_batch
