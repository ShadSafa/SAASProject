---
phase: 05-content-deepdive
plan: 05
subsystem: AI Analysis
tags: [niche-detection, openai, ai, structured-output, content-analysis]

dependency_graph:
  requires:
    - "04-01: OpenAI SDK Integration (structured output pattern)"
    - "05-01: Analysis model with niche field"
  provides:
    - "NicheDetectionService with detect_niche() function"
    - "30-category niche taxonomy for Instagram content"
    - "AI-powered niche classification with confidence scoring"
  affects:
    - "05-06: Advanced Insights API (will consume niche detection)"
    - "05-07: Analysis UI (will display detected niches)"

tech_stack:
  added:
    - OpenAI GPT-4o with structured output (client.beta.chat.completions.parse)
    - NicheDetectionResult Pydantic model for type-safe responses
  patterns:
    - Lazy client initialization to avoid import-time errors
    - Graceful error handling with fallback niche
    - Context-rich prompts with post metadata and creator size classification
    - Temperature 0.3 for consistent niche detection

key_files:
  created:
    - backend/app/services/niche_detection_service.py
    - backend/tests/test_niche_detection.py
  modified: []

decisions:
  - title: "30-category niche taxonomy"
    rationale: "Comprehensive coverage of major Instagram content categories from Fitness to Real Estate"
    alternatives: ["Smaller 10-category taxonomy", "Hierarchical niche structure"]
    trade_offs: "30 categories provide good granularity without overwhelming users; can be grouped later for UI display"

  - title: "Lazy OpenAI client initialization"
    rationale: "Prevents import-time authentication errors when OPENAI_API_KEY not set"
    alternatives: ["Import-time client creation", "Dependency injection"]
    trade_offs: "Lazy init allows tests to mock _get_client() without real API key; cleaner test setup"

  - title: "Fallback to 'Other' niche on API errors"
    rationale: "Graceful degradation instead of crashing analysis pipeline"
    alternatives: ["Raise exception and halt", "Retry with exponential backoff"]
    trade_offs: "Low-confidence 'Other' niche is better than no analysis; user can refine later in Phase 05-06"

  - title: "Creator size classification in prompt"
    rationale: "Mega-creators often have different niche patterns than micro-creators"
    alternatives: ["Omit follower count from prompt", "Use exact follower numbers"]
    trade_offs: "Size brackets provide context without overwhelming prompt with exact numbers"

metrics:
  duration: "3 minutes"
  tasks_completed: 3
  files_created: 2
  commits: 3
  tests_added: 6
  test_pass_rate: "100%"
  completed_date: "2026-02-21"
---

# Phase 05 Plan 05: Niche Detection Service Summary

**One-liner:** AI-powered Instagram niche detection using OpenAI GPT-4o with structured output, classifying posts into 30 categories (Fitness, Beauty, Tech, etc.) with confidence scoring.

## What Was Built

### Core Service
- **NicheDetectionService** (`backend/app/services/niche_detection_service.py`)
  - `detect_niche()` async function analyzes caption, hashtags, content format, and creator metrics
  - Returns `NicheDetectionResult` with primary niche, optional secondary niche, confidence (0.0-1.0), reasoning, and keywords
  - Uses OpenAI GPT-4o with structured output (same pattern as Phase 04-01)
  - Temperature 0.3 for consistent classification across similar posts

### Niche Taxonomy
30 comprehensive Instagram content categories:
- Fitness & Wellness, Beauty & Cosmetics, Fashion & Styling
- Food & Cooking, Travel & Adventure, Technology & Gadgets
- Business & Entrepreneurship, Personal Development, Gaming & Esports
- Music & Entertainment, Art & Design, Photography
- Education & Learning, Parenting & Family, Home & Decor
- Automotive, Sports & Fitness, DIY & Crafts
- Pets & Animals, Finance & Investing, Comedy & Humor
- Motivational & Inspiration, Lifestyle, Sports
- Mental Health, Sustainability, Dating & Relationships
- Real Estate, Healthcare, Other

### Testing
6 comprehensive test cases (100% passing):
1. `test_niche_detection_result_model` - Validates Pydantic model structure
2. `test_niche_options_comprehensive` - Verifies taxonomy completeness (30+ categories)
3. `test_niche_detection_result_validation` - Tests confidence bounds (0.0-1.0)
4. `test_niche_detection_with_mock_openai` - Mocked OpenAI integration test
5. `test_niche_detection_fallback_on_error` - Error handling with "Other" fallback
6. `test_creator_size_classification` - Helper function validation

All tests use mocks - zero API costs during testing.

## Technical Implementation

### OpenAI Integration Pattern
```python
# Lazy client initialization (avoids import-time errors)
_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

# Structured output with Pydantic
message = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    response_format=NicheDetectionResult,
    temperature=0.3
)
result = message.choices[0].message.parsed
```

### Prompt Engineering
Rich context includes:
- Post caption
- Hashtags (JSON array)
- Extended content formats (Tutorial, Educational, etc.)
- Instagram native type (Reel, Post, Story)
- Creator size classification (Micro/Small/Medium/Macro/Mega-creator)
- Full list of 30 available niches

AI returns:
1. Primary niche (must be from taxonomy)
2. Secondary niche (optional)
3. Confidence score (0.0 = uncertain, 1.0 = very confident)
4. Reasoning explaining the choice
5. Key indicators/keywords from the post

### Error Handling
Graceful fallback on API failures:
```python
except Exception as e:
    logger.error(f"Niche detection failed: {str(e)}")
    return NicheDetectionResult(
        primary_niche="Other",
        secondary_niche=None,
        confidence=0.3,
        reasoning="Detection failed, defaulting to Other",
        keywords=[]
    )
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Lazy OpenAI client initialization**
- **Found during:** Task 2 - Service verification
- **Issue:** Import-time client creation (`client = OpenAI(...)`) raised authentication error when `OPENAI_API_KEY` not set, breaking all imports including tests
- **Fix:** Implemented lazy initialization pattern with `_get_client()` function that creates client only when detect_niche() is actually called
- **Files modified:** `backend/app/services/niche_detection_service.py`
- **Commit:** 625ddf2 (included in Task 2 commit)
- **Rationale:** Tests use mocks and don't need real API key; lazy init allows clean imports and test execution without environment setup

## Integration Points

### Upstream Dependencies
- **Phase 04-01 OpenAI SDK Integration**: Uses identical structured output pattern (client.beta.chat.completions.parse)
- **Phase 05-01 Analysis Model**: Analysis.niche field ready to store detected niche strings

### Downstream Consumers
- **Phase 05-06 Advanced Insights API**: Will call detect_niche() and persist result to Analysis.niche
- **Phase 05-07 Analysis UI**: Will display detected niche with confidence indicator
- **Requirement ANALYSIS-19**: User niche refinement feature will allow manual override of AI-detected niche

## Verification Results

All verification checks passed:

1. Test suite: 6/6 tests passing (pytest)
   ```
   test_niche_detection_result_model PASSED
   test_niche_options_comprehensive PASSED
   test_niche_detection_result_validation PASSED
   test_niche_detection_with_mock_openai PASSED
   test_niche_detection_fallback_on_error PASSED
   test_creator_size_classification PASSED
   ```

2. Service imports successfully:
   ```python
   from app.services.niche_detection_service import detect_niche, NicheDetectionResult, NICHE_OPTIONS
   ```

3. Niche taxonomy count: 30 categories defined

4. No real OpenAI API calls during test execution (all mocked)

5. Error handling verified: Falls back to "Other" niche with confidence 0.3 on failures

## Self-Check: PASSED

### Created Files Verification
```bash
# backend/app/services/niche_detection_service.py
FOUND: backend/app/services/niche_detection_service.py

# backend/tests/test_niche_detection.py
FOUND: backend/tests/test_niche_detection.py
```

### Commits Verification
```bash
# Task 1: Niche taxonomy
FOUND: 7ca092c

# Task 2: OpenAI integration
FOUND: 625ddf2

# Task 3: Test suite
FOUND: b4fc3f7
```

All claimed files and commits exist in repository.

## Performance

- **Duration:** 3 minutes
- **Tasks:** 3/3 completed
- **Commits:** 3 (one per task)
- **Tests:** 6 added, 100% passing
- **API Costs:** $0 (all tests use mocks)

## Next Steps

**Immediate:**
1. Execute Plan 05-06: Advanced Insights API - integrate niche detection into analysis enrichment flow
2. Execute Plan 05-07: Audience Demographics UI - display detected niche in viral post cards

**Future Enhancements:**
- Multi-niche posts: Detect when content spans multiple niches (e.g., "Fitness Food" = Fitness + Food)
- Niche confidence thresholds: Only show niche to user if confidence > 0.7
- Niche trend analysis: Track which niches go viral most frequently in user's scans
- Custom niche definitions: Allow users to define their own niche categories

## Requirements Satisfied

- **ANALYSIS-18**: Niche auto-detection for posts ✅
  - AI-powered classification into 30 Instagram categories
  - Confidence scoring for detection quality
  - Graceful fallback on API errors

This plan provides the foundation for Requirement ANALYSIS-19 (user niche refinement), which will be implemented in Phase 05-06 when the Advanced Insights API allows users to override AI-detected niches.
