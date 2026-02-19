---
phase: 03-core-scanning-engine
plan: 02
subsystem: api
tags: [python, pytest, tdd, viral-scoring, engagement-rate, velocity]

# Dependency graph
requires: []
provides:
  - "calculate_viral_score(engagement_count, follower_count, post_age_hours) -> float in [0.0, 100.0]"
  - "calculate_growth_velocity(current, previous, time_delta_hours) -> float"
  - "Full test suite: 25 passing tests covering all edge cases and multiplier boundaries"
affects: [03-03, 03-04, scan_jobs, viral_discovery]

# Tech tracking
tech-stack:
  added: [pytest==9.0.2]
  patterns: [TDD RED-GREEN-REFACTOR, velocity-multiplier scoring, zero-division safety guards]

key-files:
  created:
    - backend/app/services/viral_scoring.py
    - backend/tests/test_viral_scoring.py
    - backend/tests/__init__.py
  modified: []

key-decisions:
  - "age <= 24h uses multiplier 1.0, not 0.5 — plan example explicitly shows age=24.0 -> 10.0"
  - "round() applied to 10 decimal places to absorb IEEE 754 float arithmetic artifacts"
  - "Dedicated _get_velocity_multiplier() helper keeps calculate_viral_score() readable"
  - "pytest installed into venv (was missing from requirements.txt)"

patterns-established:
  - "Zero-division safety: return 0.0 immediately when denominator is 0"
  - "Score capping: min(raw_score, 100.0) ensures hard ceiling before rounding"
  - "Velocity-weighted scoring: engagement_rate * multiplier * 100 normalized to percentage"

# Metrics
duration: 15min
completed: 2026-02-19
---

# Phase 3 Plan 02: Viral Scoring Algorithm Summary

**Engagement-rate formula with 6-tier velocity multiplier (3.0 to 0.5 by post age), capped at 100.0, with zero-division safety — TDD: 25/25 tests passing**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-02-19T00:00:00Z
- **Completed:** 2026-02-19
- **Tasks:** 3 (RED, GREEN, REFACTOR)
- **Files modified:** 3

## Accomplishments

- `calculate_viral_score()` implemented: (engagement / followers) * velocity_multiplier * 100, capped at 100.0, returns 0.0 on zero followers
- `calculate_growth_velocity()` implemented: (current - previous) / time_delta_hours, returns 0.0 on zero time delta
- 25 pytest test cases covering all 6 velocity multiplier tiers, boundary conditions, edge cases (zero followers, zero engagement, cap at 100), return type assertions, and fast-vs-slow comparison

## Task Commits

Each TDD phase was committed atomically:

1. **RED: Failing tests** - `5dd98fc` (test) — 22 test cases written before any implementation
2. **GREEN: Implementation** - `57fe519` (feat) — viral_scoring.py passing all 25 tests
3. **REFACTOR: Docstring cleanup** - `f6ae268` (refactor) — docstring boundary accuracy fix

## Files Created/Modified

- `backend/app/services/viral_scoring.py` — Core scoring module with calculate_viral_score() and calculate_growth_velocity()
- `backend/tests/test_viral_scoring.py` — 25-test suite covering all specified behaviors and edge cases
- `backend/tests/__init__.py` — Empty init for test package discovery

## Decisions Made

- **age <= 24h uses multiplier 1.0**: Plan text says `>= 24: 0.5` but plan examples show `age=24.0 -> 10.0 (multiplier 1.0)`. Examples are authoritative — boundary is `> 24` for 0.5 multiplier.
- **round() to 10 decimal places**: IEEE 754 float arithmetic produces artifacts like `30.000000000000004`. Rounding to 10 decimal places eliminates these without losing meaningful precision.
- **Separate _get_velocity_multiplier() helper**: Keeps calculate_viral_score() focused on the formula, makes the lookup logic testable in isolation if needed.
- **pytest installed to venv**: Was not in requirements.txt — installed as blocking fix (Rule 3).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing pytest dependency**
- **Found during:** RED phase setup
- **Issue:** `venv/Scripts/pytest` did not exist; pytest was not in requirements.txt
- **Fix:** `pip install pytest` into existing venv
- **Files modified:** None (package install only)
- **Verification:** `python -m pytest --version` returned pytest 9.0.2
- **Committed in:** 5dd98fc (part of RED phase commit)

**2. [Rule 1 - Bug] Fixed age boundary: <= 24h maps to multiplier 1.0**
- **Found during:** GREEN phase — 4 tests failing after initial implementation
- **Issue:** Plan text said `>= 24 hours: 0.5` but plan-provided examples show `age=24.0` returns `10.0` (which requires multiplier 1.0). Implementation used `< 24` (exclusive), giving 0.5 to age=24.
- **Fix:** Changed `elif post_age_hours < 24.0` to `elif post_age_hours <= 24.0` so age=24 uses 1.0 multiplier
- **Files modified:** backend/app/services/viral_scoring.py
- **Verification:** Test `test_score_age_12_to_24_hours_multiplier_1` passes (age=24.0 -> 10.0)
- **Committed in:** 57fe519 (GREEN phase commit)

**3. [Rule 1 - Bug] Added round() to eliminate float precision artifacts**
- **Found during:** GREEN phase — tests asserting `== 30.0` failing with `30.000000000000004`
- **Issue:** `(1000/10000) * 3.0 * 100` produces floating point artifact due to IEEE 754 representation
- **Fix:** `round(min(raw_score, 100.0), 10)` — 10 decimal places eliminates artifacts while preserving precision
- **Files modified:** backend/app/services/viral_scoring.py
- **Verification:** 25/25 tests pass with exact float equality assertions
- **Committed in:** 57fe519 (GREEN phase commit)

---

**Total deviations:** 3 auto-fixed (1 blocking install, 2 bugs)
**Impact on plan:** All auto-fixes necessary for correctness. The boundary bug would have caused wrong scores for 24h-old posts in production. Float precision fix ensures reliable equality in downstream comparison logic.

## Issues Encountered

- Python 3.13 venv used (not 3.12 as noted in STATE.md) — no functional difference for this pure-Python module.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `calculate_viral_score` is ready for import by `backend/app/tasks/scan_jobs.py`
- Import pattern: `from app.services.viral_scoring import calculate_viral_score`
- Function signature locked: `calculate_viral_score(engagement_count: int, follower_count: int, post_age_hours: float) -> float`
- All edge cases tested and documented

---
*Phase: 03-core-scanning-engine*
*Completed: 2026-02-19*
