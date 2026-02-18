---
phase: 02-instagram-integration
plan: 06
subsystem: ui
tags: [react, typescript, zustand, instagram, dashboard, banner]

# Dependency graph
requires:
  - phase: 02-instagram-integration
    provides: accountsStore Zustand store with InstagramAccount list and AccountStatus types
  - phase: 02-instagram-integration
    provides: /settings/integrations page for reconnect flow (Fix now link target)
provides:
  - ExpiryBanner component for dismissible expired/revoked token alerts on dashboard
  - DashboardPage updated with ExpiryBanner integration and conditional content area
  - Dashboard shows Phase 3 placeholder when accounts exist, empty state when none
affects: [03-viral-content-scanning, dashboard-features]

# Tech tracking
tech-stack:
  added: []
  patterns: [local useState for dismiss (not persisted), filter expired/revoked from store, conditional empty-vs-placeholder content area]

key-files:
  created:
    - frontend/src/components/ExpiryBanner.tsx
  modified:
    - frontend/src/pages/DashboardPage.tsx

key-decisions:
  - "Dismiss is local useState only — banner reappears on page reload per spec (not persisted)"
  - "Fix now navigates to /settings/integrations via useNavigate (not inline OAuth from banner — per CONTEXT.md)"
  - "DashboardPage splits on accounts.length === 0 for empty state vs Phase 3 placeholder"
  - "Phase 3 placeholder shows active account count to orient users during wait"

patterns-established:
  - "Banner pattern: yellow-50 bg, yellow-200 border, flex layout with icon + message + dismiss"
  - "Expired account filter: accounts.filter(a => a.status === 'expired' || a.status === 'revoked')"

# Metrics
duration: 5min
completed: 2026-02-18
---

# Phase 02 Plan 06: Dashboard Expiry Banner Summary

**Dismissible yellow ExpiryBanner on dashboard alerts users to expired/revoked Instagram tokens with @username context and Fix now navigation to /settings/integrations**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-18T15:27:48Z
- **Completed:** 2026-02-18T15:32:00Z
- **Tasks:** 1 of 2 (Task 2 is human verification checkpoint — awaiting approval)
- **Files modified:** 2

## Accomplishments
- ExpiryBanner component: yellow warning banner with account username, revoked vs expired message distinction, Fix now link, dismiss button
- DashboardPage: integrates ExpiryBanner, conditional content (empty state vs Phase 3 placeholder), reads from accountsStore
- TypeScript compiles without errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ExpiryBanner component and integrate into DashboardPage** - `ca34c27` (feat)
2. **Task 2: Human verification of complete Phase 2 feature set** - awaiting checkpoint approval

## Files Created/Modified
- `frontend/src/components/ExpiryBanner.tsx` - Dismissible banner for expired/revoked Instagram tokens; shows @username, status message, Fix now link, and X dismiss button
- `frontend/src/pages/DashboardPage.tsx` - Dashboard with ExpiryBanner, expired account filter from store, conditional empty-state vs placeholder content

## Decisions Made
- Dismiss is local useState only — banner reappears on page reload per spec. No sessionStorage persistence needed.
- Fix now uses useNavigate('/settings/integrations') not window.location.href — stays within SPA, per CONTEXT.md decision against inline OAuth from banner.
- DashboardPage Phase 3 placeholder shows active account count to orient users while scanning features are not yet available.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None - TypeScript compiled cleanly after task 1.

## User Setup Required
None - no external service configuration required for this plan.

## Next Phase Readiness
- ExpiryBanner complete and integrated into DashboardPage
- Full Phase 2 feature set ready for human end-to-end verification
- After checkpoint approval, Phase 2 is complete and Phase 3 (viral content scanning) can begin

## Self-Check: PASSED

All created files exist on disk. Task commit ca34c27 confirmed in git log.

---
*Phase: 02-instagram-integration*
*Completed: 2026-02-18*
