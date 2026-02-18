---
phase: 02-instagram-integration
plan: "03"
subsystem: ui
tags: [react, typescript, react-router, tailwind, layout, navigation]

# Dependency graph
requires:
  - phase: 01-10
    provides: ProfilePage and ProtectedRoute components for wrapping
  - phase: 02-01
    provides: InstagramAccount model (account count will come from 02-04)
provides:
  - AppLayout component with persistent nav bar for all protected pages
  - /settings/integrations route (placeholder, wired in 02-04)
  - Dashboard empty state with CTA to connect Instagram
  - Unified layout infrastructure for Phase 2+ pages
affects:
  - 02-04 (will provide accountCount prop to AppLayout)
  - All future protected pages will use AppLayout

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AppLayout wrapper pattern: protected pages receive layout from App.tsx, not self-managed"
    - "NavLink with isActive for active link highlighting in shared nav"
    - "accountCount prop pattern: layout accepts count as optional prop (defaults 0)"

key-files:
  created:
    - frontend/src/components/AppLayout.tsx
  modified:
    - frontend/src/App.tsx
    - frontend/src/pages/DashboardPage.tsx
    - frontend/src/pages/ProfilePage.tsx

key-decisions:
  - "AppLayout wraps pages in App.tsx (not self-applied) so pages stay layout-agnostic"
  - "accountCount prop defaults to 0 — real count wired in Plan 02-04 via Instagram accounts hook"
  - "ProfilePage inline nav removed — AppLayout provides unified nav including Sign out"
  - "Dashboard empty state CTA uses <a href> not Link to trigger full navigation (avoids SPA state issues)"

patterns-established:
  - "Layout pattern: all protected pages are pure content, AppLayout owns chrome"
  - "Nav active state: NavLink isActive callback with border-b-2 border-blue-600 for active, text-gray-600 hover:text-gray-900 for inactive"

# Metrics
duration: 5min
completed: 2026-02-18
---

# Phase 02 Plan 03: AppLayout Nav Infrastructure Summary

**Shared AppLayout component with persistent nav bar wrapping all protected pages — brand link, Dashboard/Settings NavLinks with active highlighting, user email, and 0-account placeholder badge**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-02-18T14:24:53Z
- **Completed:** 2026-02-18T14:29:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Created AppLayout component with nav bar: brand, Dashboard + Settings links, user email + account count
- Updated App.tsx to wrap all three protected routes (Dashboard, Profile, Settings/Integrations) in AppLayout
- Added /settings/integrations protected route with placeholder content
- Refactored DashboardPage to remove inline nav and show empty state CTA to connect Instagram
- Refactored ProfilePage to remove inline nav (AppLayout's "Sign out" replaces it)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create AppLayout component with persistent nav** - `85ac93d` (feat)
2. **Task 2: Update App.tsx routing and refactor DashboardPage/ProfilePage** - `2ec7872` (feat)

## Files Created/Modified
- `frontend/src/components/AppLayout.tsx` - Shared layout wrapper with persistent nav bar, user info, account count
- `frontend/src/App.tsx` - Added AppLayout wrapping, /settings/integrations route
- `frontend/src/pages/DashboardPage.tsx` - Removed inline nav, added empty state with CTA
- `frontend/src/pages/ProfilePage.tsx` - Removed inline nav and outer layout wrapper

## Decisions Made
- AppLayout wraps pages from App.tsx rather than pages self-applying layout — keeps page components layout-agnostic and simpler
- accountCount defaults to 0 and is passed as prop — Plan 02-04 will provide real count from Instagram accounts API
- Removed ProfilePage's "Back to Dashboard" link since AppLayout nav provides persistent Dashboard link
- Dashboard CTA uses `<a href="/settings/integrations">` not React Router `<Link>` — acceptable for now since it's a simple internal link

## Deviations from Plan

**1. [Rule 2 - Missing Critical] Refactored ProfilePage inline nav**
- **Found during:** Task 2 (updating App.tsx)
- **Issue:** Plan specified "ProfilePage uses AppLayout instead of its own inline nav" but ProfilePage had a full inline nav (with "Back to Dashboard" link and Logout button) — these conflict with AppLayout's nav
- **Fix:** Removed ProfilePage's outer `min-h-screen` wrapper, inline `<nav>`, and the Logout button (AppLayout "Sign out" replaces it). Removed unused `Link` import.
- **Files modified:** frontend/src/pages/ProfilePage.tsx
- **Verification:** TypeScript compiles without errors; nav structure is now consistent
- **Committed in:** 2ec7872 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical consistency fix)
**Impact on plan:** Required for correct nav behavior — without removing ProfilePage's inline nav, users would see two nav bars on /profile.

## Issues Encountered
None - TypeScript compiled clean on first attempt.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Nav infrastructure complete for all Phase 2+ pages
- AppLayout accepts `accountCount` prop — Plan 02-04 will wire in real count from Instagram accounts hook
- /settings/integrations route placeholder is protected and ready to receive IntegrationsPage component in Plan 02-04

## Self-Check: PASSED

- FOUND: frontend/src/components/AppLayout.tsx
- FOUND: frontend/src/App.tsx
- FOUND: frontend/src/pages/DashboardPage.tsx
- FOUND: frontend/src/pages/ProfilePage.tsx
- FOUND: .planning/phases/02-instagram-integration/02-03-SUMMARY.md
- FOUND: commit 85ac93d (AppLayout component)
- FOUND: commit 2ec7872 (routing and page refactors)

---
*Phase: 02-instagram-integration*
*Completed: 2026-02-18*
