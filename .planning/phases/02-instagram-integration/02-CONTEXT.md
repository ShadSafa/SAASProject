# Phase 2: Instagram Integration - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Users connect their Instagram accounts via OAuth, manage multiple connected accounts, and see connection status. This phase covers the account connection experience — OAuth flow, token storage/refresh, status display, reconnect/disconnect. Scanning and analysis are Phase 3+.

</domain>

<decisions>
## Implementation Decisions

### Connection Entry Point
- Instagram accounts are managed on a dedicated **Settings/Integrations page**
- Settings is accessible via a **top nav or sidebar link** (always visible in main navigation)
- Nav also shows connected account count alongside the user's name (e.g. "2 accounts")
- **Account limits are tier-based**: free tier gets 1 account, paid tier gets more (exact limits for planner to define based on subscription tiers from Phase 10)
- Whether one Instagram account can be shared across multiple app users: **Claude's discretion** (standard SaaS approach — one-to-one is safer, prevents data leakage)

### OAuth Flow
- OAuth window behavior: **Claude's discretion** (full-page redirect is more reliable cross-browser than popups)
- After successful OAuth: **Claude's discretion** (redirect to Settings/Integrations page showing the newly connected account is the clearest UX)
- Dashboard empty state (no accounts connected): **Claude's discretion** (should prompt with a clear CTA to connect)

### Account List Display
- Layout: **Claude's discretion** (cards or list — pick the cleanest for account management)
- Each account shows: **profile picture, username, follower count, account type (Personal/Creator/Business)**
- Date connected and last synced: not required
- Empty state: **illustration + prominent "Connect Instagram Account" CTA button**
- "Add another account" button placement: **Claude's discretion**

### Status Indicators
- Connection status shown as **colored badge on each account card**: green (Active), yellow (Expired), red (Error/Revoked)
- **Expired vs Error are visually distinct**: yellow warning for expired tokens, red error for revoked/permission errors
- When a token expires:
  - **Inline status badge** on the account card (Settings page)
  - **Dismissible banner on the dashboard** until reconnected
- **Account count shown in main nav** alongside user's name

### Reconnect Flow
- Expired accounts show a **"Reconnect" button directly on the account card** (replaces or appears next to status badge)
- Dashboard expiry banner includes a **"Fix now" link that navigates to Settings** page (not inline OAuth from banner)
- Users receive an **email notification when their token expires** (with reconnect link)

### Disconnect Flow
- Disconnecting requires a **confirmation dialog** warning that all data will be deleted
- On confirm: **hard delete** — remove account and all associated scan history permanently
- No soft delete / data retention after disconnect

### Claude's Discretion
- OAuth window type (full-page redirect vs popup) — use full-page redirect for reliability
- Post-OAuth redirect destination — Settings/Integrations page showing the account
- Dashboard empty state design — CTA card prompting to connect first account
- "Add another account" button placement — bottom of account list or top, whichever is cleaner
- Whether same Instagram account can link to multiple app users — default to one-to-one
- Account card vs list layout — pick what's cleanest

</decisions>

<specifics>
## Specific Ideas

- Connection status uses traffic-light color system: green/yellow/red
- Nav shows account count ("2 accounts") so users can see at a glance how many they have connected
- "Fix now" in the expiry banner should deep-link to the specific expired account in Settings
- Disconnect warning should be explicit about data loss: "This will permanently delete all scan history for @username"

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-instagram-integration*
*Context gathered: 2026-02-17*
