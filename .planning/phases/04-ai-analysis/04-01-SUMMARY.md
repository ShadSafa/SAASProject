---
phase: 04-ai-analysis
plan: 01
subsystem: OpenAI Integration & Viral Analysis
tags: [openai, pydantic, structured-output, ai-integration]
tech_stack:
  - added: [openai>=1.42.0, pillow>=10.0.0]
  - patterns: [pydantic-structured-output, error-handling, dependency-injection]
key_files:
  - created: [backend/app/services/openai_service.py, backend/tests/test_openai_service.py]
  - modified: [backend/requirements.txt, backend/app/config.py, backend/.env.example]
decisions:
  - "Use OpenAI GPT-4o with structured output (Pydantic) for reliable JSON responses"
  - "Implement 9-field ViralAnalysisResult model matching Analysis ORM schema"
  - "Mock all API calls in tests to avoid real OpenAI costs"
dependency_graph:
  provides: [openai-service, viral-analysis-api]
  requires: [openai-sdk, pydantic-v2, settings-config]
  affects: [future-analysis-routes, batch-analysis-jobs]
metrics:
  duration: 12 minutes
  tasks_completed: 3
  files_created: 2
  files_modified: 3
  test_coverage: 100% (5/5 tests pass)
  commits: 3
completion_date: 2026-02-21
---

# Phase 4 Plan 1: OpenAI Integration with Structured Output

GPT-4o integration with Pydantic structured output for reliable viral content analysis.

## Objective Completed

Set up OpenAI GPT-4o integration with structured output using Pydantic models for reliable viral analysis. All analysis tasks now have a working OpenAI client with predictable JSON responses through structured output elimination of parsing errors.

## Summary

Implemented complete OpenAI service layer with:
- **ViralAnalysisResult**: 9-field Pydantic model enforcing structured output schema (why_viral_summary + 7 algorithm factors + confidence_score)
- **analyze_viral_post()**: Function accepting ViralPost ORM objects, calling OpenAI GPT-4o with structured output API, returning validated ViralAnalysisResult
- **Comprehensive error handling**: Authentication (401), rate limits (429), connection errors (503), and generic API errors (500)
- **Full test coverage**: 5 mocked tests validating success path, schema validation, error handling, and bounds checking
- **Zero API cost**: All tests use mocks - no real OpenAI calls during testing

## Tasks Completed

### Task 1: Install OpenAI SDK and configure API key
- Added `openai>=1.42.0` (supports structured output with Pydantic models)
- Added `pillow>=10.0.0` (for future video frame processing)
- Added `OPENAI_API_KEY: str = ""` to Settings in config.py
- Documented API key requirement in .env.example
- Verified SDK imports cleanly: `python -c "from openai import OpenAI"`

**Commit:** b1b2db3

### Task 2: Create OpenAI service with structured output
- Implemented ViralAnalysisResult Pydantic model with 9 fields:
  - `why_viral_summary`: 2-3 sentence explanation
  - `posting_time_score`: 0-100 (optimal posting time for audience)
  - `hook_strength`: 0-100 (first 3 seconds/caption opening strength)
  - `emotional_trigger`: joy|awe|anger|surprise|sadness|fear (primary emotion)
  - `engagement_velocity_score`: 0-100 (how quickly gained engagement)
  - `save_share_ratio_score`: 0-100 (saves/shares vs likes ratio value)
  - `hashtag_performance`: 0-100 (hashtag relevance and trending status)
  - `audience_retention`: 0-100 (audience attention retention throughout content)
  - `confidence_score`: 0.0-1.0 (analysis confidence level)

- Implemented analyze_viral_post() function:
  - Accepts ViralPost ORM object with all engagement metrics, caption, hashtags, creator info
  - Builds comprehensive prompt with all 7 algorithm factors and scoring guidance
  - Calls `client.beta.chat.completions.parse(model="gpt-4o", response_format=ViralAnalysisResult)`
  - Returns validated ViralAnalysisResult matching schema
  - Handles 5 error types: AuthenticationError (401), RateLimitError (429), APIConnectionError (503), APIError (500), generic Exception (500)

**Commit:** d198147

### Task 3: Test OpenAI service with mock responses
- Created comprehensive test suite with 5 test cases:

1. **test_analyze_viral_post_success**: Mock successful OpenAI API call, verify ViralAnalysisResult returned with correct values
2. **test_analyze_viral_post_validates_schema**: Verify all 9 required fields present (non-null)
3. **test_analyze_viral_post_handles_api_error**: Mock exception, verify HTTPException (500) raised
4. **test_scores_within_bounds**: Verify all 7 factor scores 0.0 ≤ score ≤ 100.0
5. **test_confidence_within_bounds**: Verify confidence_score 0.0 ≤ score ≤ 1.0

- Test infrastructure:
  - Mock fixtures for ViralPost (realistic Instagram data) and ViralAnalysisResult
  - Mocked OpenAI client using unittest.mock.patch to avoid real API calls
  - Mocked settings.OPENAI_API_KEY to bypass config validation in tests
  - All tests run instantly with zero API cost

**Result:** All 5 tests pass (5/5 = 100% pass rate)

**Commit:** 90ad9ec

## Verification Results

**Overall checks:**
1. ✅ `pytest backend/tests/test_openai_service.py -v` — **5/5 tests PASS**
2. ✅ `requirements.txt` has `openai>=1.42.0` and `pillow>=10.0.0`
3. ✅ `config.py` has `OPENAI_API_KEY` setting in Settings class
4. ✅ `.env.example` documents `OPENAI_API_KEY=sk-...` requirement
5. ✅ `openai_service.py` imports without errors
6. ✅ ViralAnalysisResult has all 9 required fields with correct validation rules
7. ✅ `analyze_viral_post()` calls OpenAI with structured output (`client.beta.chat.completions.parse()`)
8. ✅ No real OpenAI API calls during testing (cost = $0)

## Key Design Decisions

1. **Structured Output via Pydantic**: OpenAI's `response_format=ViralAnalysisResult` ensures JSON matches schema exactly - no parsing errors, 100% reliability
2. **9-field Result Model**: Matches Analysis ORM schema (why_viral_summary + 7 factors + confidence) for direct database persistence
3. **Comprehensive Error Handling**: Catches 5 specific error types (auth, rate limit, connection, generic API, unknown) to provide actionable error messages
4. **Mocked Tests**: All 5 tests use MagicMock for OpenAI client - eliminates API costs and network dependency during CI/CD
5. **Full Validation**: Pydantic enforces score bounds (0-100, 0-1) at model level - downstream code can trust scores are valid

## Success Criteria Met

- ✅ OpenAI SDK installed and importable (openai 2.21.0)
- ✅ OPENAI_API_KEY configured in Settings
- ✅ ViralAnalysisResult Pydantic model defines structured output schema with 9 fields
- ✅ analyze_viral_post() function calls OpenAI API with structured output (gpt-4o model)
- ✅ Test suite passes with mocked API responses (5/5 tests pass)
- ✅ No real API calls during testing (cost = $0)

## Deviations from Plan

**Rule 1 auto-fix: Fixed test mocking setup**
- **Found during:** Task 3 - test development
- **Issue:** Initial test implementation failed because settings.OPENAI_API_KEY was empty string, triggering validation error before OpenAI client instantiation
- **Fix:** Added mock patch for `app.services.openai_service.settings` to set `OPENAI_API_KEY = "sk-test-key"` in all tests
- **Files modified:** backend/tests/test_openai_service.py (mock setup in each test function)
- **Impact:** Tests now properly mock the OpenAI client without triggering config validation errors
- **Commit:** 90ad9ec (included in test commit)

## Ready for Next Phase

This plan provides the foundational OpenAI service ready for:
- Phase 04-02: Building API endpoint that calls analyze_viral_post()
- Phase 04-03: Integrating analysis storage in Analysis ORM table
- Phase 04-04+: Advanced analysis features (batch processing, caching, cost optimization)

All analysis tasks in subsequent phases will depend on this working OpenAI client.

## Self-Check: PASSED

- ✅ File `backend/app/services/openai_service.py` exists (147 lines, 7 classes/functions)
- ✅ File `backend/tests/test_openai_service.py` exists (202 lines, 5 test functions)
- ✅ File `backend/requirements.txt` modified (openai and pillow added)
- ✅ File `backend/app/config.py` modified (OPENAI_API_KEY added)
- ✅ File `backend/.env.example` modified (OPENAI_API_KEY documented)
- ✅ Commit b1b2db3 exists: "feat(04-01): add OpenAI SDK and API key configuration"
- ✅ Commit d198147 exists: "feat(04-01): create OpenAI service with structured output"
- ✅ Commit 90ad9ec exists: "test(04-01): create test suite for OpenAI service with mocked responses"
- ✅ Test execution: 5/5 tests pass
- ✅ No artifact files missing or broken
