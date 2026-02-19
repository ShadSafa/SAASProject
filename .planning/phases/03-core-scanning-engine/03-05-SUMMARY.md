---
phase: 03-core-scanning-engine
plan: 05
subsystem: frontend-data-layer
tags: [typescript, zustand, react-hooks, polling, api-client]
dependency_graph:
  requires: ["03-04"]
  provides: ["frontend-scan-data-layer"]
  affects: ["03-07-scan-page-ui"]
tech_stack:
  added: []
  patterns: ["zustand-store", "react-polling-hook", "axios-api-client"]
key_files:
  created:
    - frontend/src/types/scan.ts
    - frontend/src/api/scans.ts
    - frontend/src/store/scanStore.ts
    - frontend/src/hooks/useScan.ts
  modified: []
decisions:
  - "useScan uses useRef for interval ID so stopPolling closure is stable across re-renders"
  - "Polling timeout set to 5 minutes with setError('Scan timed out') on expiry"
  - "Network errors during polling are logged but do not stop polling — retry on next interval"
  - "startScan and startUrlScan call clearScan() first so stale state never leaks across invocations"
metrics:
  duration: "2 min"
  completed_date: "2026-02-19"
  tasks: 2
  files_created: 4
  files_modified: 0
---

# Phase 03 Plan 05: Frontend Scan Data Layer Summary

**One-liner:** Axios API client, Zustand scan store, and useScan hook with 2-second polling and 5-minute timeout for scan lifecycle management.

---

## What Was Built

The frontend scan data layer separates all data-fetching concerns from UI. Four files were created:

1. **`frontend/src/types/scan.ts`** — TypeScript interfaces: `ScanStatus`, `ScanType`, `TimeRange`, `EngagementMetrics`, `ViralPost`, `ScanTriggerResponse`, `ScanResponse`, `ScanHistoryItem`.

2. **`frontend/src/api/scans.ts`** — Four Axios-based API functions:
   - `triggerScan(timeRange)` — POST /scans/trigger
   - `analyzeUrl(instagramUrl)` — POST /scans/analyze-url
   - `getScanStatus(scanId)` — GET /scans/status/{id}
   - `getScanHistory()` — GET /scans/history

3. **`frontend/src/store/scanStore.ts`** — Zustand store holding `currentScanId`, `currentStatus`, `scanResults`, `isScanning`, `error`, `lastScan` with granular setter actions and `clearScan()` reset.

4. **`frontend/src/hooks/useScan.ts`** — `useScan()` hook with:
   - `startScan(timeRange)` — triggers hashtag scan and starts polling
   - `startUrlScan(instagramUrl)` — triggers URL scan and starts polling
   - `clearResults()` — resets all state to idle
   - Polls `GET /scans/status/{id}` every 2000ms
   - Stops polling automatically on `completed`, `failed`, or 5-minute timeout
   - Clears `setInterval` via `useEffect` cleanup on unmount (no memory leaks)

---

## Verification Results

- `npx tsc --noEmit` — zero errors across all four new files
- All required exports confirmed present
- Hook wires correctly: `useScan` → `getScanStatus` (API) + `useScanStore` (store)

---

## Deviations from Plan

None - plan executed exactly as written.

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| `useRef` for interval ID | Stable across re-renders; closure in `stopPolling` always captures same ref |
| 5-minute poll timeout | Prevents indefinite polling if backend hangs; surfaces clear error message |
| Network errors don't stop polling | Transient connection issues should retry; only terminal statuses stop polling |
| `clearScan()` called at start of each scan | Prevents stale results from previous scan leaking into new scan UI |

---

## Self-Check

- [x] `frontend/src/types/scan.ts` — FOUND
- [x] `frontend/src/api/scans.ts` — FOUND
- [x] `frontend/src/store/scanStore.ts` — FOUND
- [x] `frontend/src/hooks/useScan.ts` — FOUND
- [x] Commit `9c31b49` (Task 1) — EXISTS
- [x] Commit `8364892` (Task 2) — EXISTS
- [x] TypeScript: PASS (zero errors)

## Self-Check: PASSED
