# Phase 2: Instagram Integration - Research

**Researched:** 2026-02-18
**Domain:** Instagram OAuth 2.0 Integration, Token Management, Multi-Account Architecture
**Confidence:** HIGH

---

## Summary

Phase 2 enables users to connect and manage multiple Instagram accounts via OAuth 2.0, implementing robust token management with automatic refresh cycles and clear status visualization. The primary challenge is managing Instagram's token lifecycle (60-day expiration with automatic refresh capability) across multiple accounts per user while providing transparent connection status and seamless reconnection flows.

This phase requires three parallel workstreams: (1) Backend OAuth flow implementation with Instagram Graph API integration, (2) Frontend Settings/Integrations page with account card display and status indicators, (3) Token refresh scheduling with email notifications for expiration events.

Critical technical decisions center on full-page redirect OAuth (more reliable cross-browser than popups), automatic token refresh every 50-55 days (preventing 60-day expiration), and one-to-one Instagram account mapping (preventing cross-user data leakage).

**Primary recommendation:** Use Authlib for OAuth2 client-side handling in FastAPI, APScheduler for background token refresh every 50 days, encrypted token storage in database, and full-page redirect for OAuth flow with post-OAuth redirect to Settings/Integrations page.

---

## User Constraints (from CONTEXT.md)

<user_constraints>

### Locked Decisions

**Connection Entry Point:**
- Instagram accounts are managed on a dedicated **Settings/Integrations page**
- Settings is accessible via a **top nav or sidebar link** (always visible in main navigation)
- Nav also shows connected account count alongside the user's name (e.g. "2 accounts")
- **Account limits are tier-based**: free tier gets 1 account, paid tier gets more (exact limits for planner to define based on subscription tiers from Phase 10)

**Account List Display:**
- Each account shows: **profile picture, username, follower count, account type (Personal/Creator/Business)**
- Date connected and last synced: not required
- Empty state: **illustration + prominent "Connect Instagram Account" CTA button**

**Status Indicators:**
- Connection status shown as **colored badge on each account card**: green (Active), yellow (Expired), red (Error/Revoked)
- **Expired vs Error are visually distinct**: yellow warning for expired tokens, red error for revoked/permission errors
- When a token expires:
  - **Inline status badge** on the account card (Settings page)
  - **Dismissible banner on the dashboard** until reconnected
- **Account count shown in main nav** alongside user's name

**Reconnect Flow:**
- Expired accounts show a **"Reconnect" button directly on the account card** (replaces or appears next to status badge)
- Dashboard expiry banner includes a **"Fix now" link that navigates to Settings** page (not inline OAuth from banner)
- Users receive an **email notification when their token expires** (with reconnect link)

**Disconnect Flow:**
- Disconnecting requires a **confirmation dialog** warning that all data will be deleted
- On confirm: **hard delete** — remove account and all associated scan history permanently
- No soft delete / data retention after disconnect

### Claude's Discretion Areas

- **OAuth window type:** Use full-page redirect for reliability (better cross-browser compatibility than popups)
- **Post-OAuth redirect destination:** Settings/Integrations page showing the newly connected account
- **Dashboard empty state design:** CTA card prompting to connect first account
- **"Add another account" button placement:** Bottom of account list or top, whichever is cleaner UX
- **One-to-one mapping:** Default to one Instagram account per app user (prevents data leakage, standard SaaS approach)
- **Account card vs list layout:** Pick the cleanest presentation for account management

### Deferred Ideas (OUT OF SCOPE)

- None — discussion stayed within phase scope

</user_constraints>

---

## Standard Stack

### Backend OAuth & Token Management

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Authlib | 1.2+ | OAuth2 client & provider | Pure async OAuth2 implementation; excellent FastAPI integration; handles token refresh automatically |
| FastAPI | 0.110+ | REST API framework | Built-in async support; easy OAuth2 integration; auto-generated OpenAPI docs |
| SQLAlchemy | 2.0+ | ORM for storing OAuth accounts | Supports complex relationships (user has many Instagram accounts); async queries |
| APScheduler | 3.10+ | Background token refresh scheduler | Pure Python scheduling; works with FastAPI; no external dependencies (unlike Celery) |
| asyncpg | 0.29+ | PostgreSQL async driver | Native async for concurrent token refreshes and DB operations |
| httpx | 0.25+ | Async HTTP client | Used internally by Authlib; handles Instagram Graph API calls |

### Frontend OAuth & Settings UI

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| axios | 1.13+ | HTTP client for API calls | Already in stack; intercepts requests to add auth headers |
| react-router-dom | 7.13+ | Client routing | Navigate to OAuth endpoint and handle redirect back from Instagram |
| zustand | 5.0+ | State management for account list | Lightweight global state for connected accounts and loading states |
| react-hook-form | 7.71+ | Form handling | For any account settings modifications |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.0+ | Environment variable management | Store Instagram app credentials securely (dev only) |
| SQLAlchemy crypto extensions | 1.0+ | Token encryption at rest | Encrypt access_tokens and refresh_tokens in database |
| Resend | 2.0+ | Transactional email | Send "token expired" notifications to users |

### Installation (Backend)

```bash
# OAuth and token management
pip install authlib httpx

# Scheduling (for background token refresh)
pip install apscheduler

# Already installed
# pip install fastapi sqlalchemy asyncpg python-dotenv

# Optional: Token encryption at rest
pip install cryptography sqlalchemy-utils
```

### Installation (Frontend)

```bash
# Already in stack
# npm install axios zustand react-router-dom react-hook-form
```

---

## Architecture Patterns

### Recommended Backend Project Structure

```
backend/
├── app/
│   ├── routes/
│   │   ├── auth.py              # Existing auth routes
│   │   ├── instagram.py         # NEW: OAuth flow endpoints
│   │   └── integrations.py      # NEW: Account management endpoints
│   ├── models/
│   │   ├── user.py              # Existing
│   │   └── instagram_account.py # NEW: InstagramAccount model
│   ├── schemas/
│   │   ├── auth.py              # Existing
│   │   └── instagram.py         # NEW: InstagramAccount, TokenResponse schemas
│   ├── services/
│   │   ├── auth.py              # Existing
│   │   └── instagram.py         # NEW: OAuth flow, token refresh logic
│   ├── tasks/
│   │   └── token_refresh.py     # NEW: Scheduled token refresh task
│   ├── security/
│   │   └── oauth.py             # NEW: OAuth2 configuration
│   └── main.py                  # Add APScheduler startup
├── migrations/                  # NEW: Migration for instagram_accounts table
└── requirements.txt             # Updated with new deps
```

### Recommended Frontend Project Structure

```
frontend/src/
├── pages/
│   └── IntegrationsPage.tsx     # NEW: Settings/Integrations page
├── components/
│   └── InstagramAccountCard.tsx # NEW: Account card component
├── api/
│   └── instagram.ts             # NEW: Instagram API endpoints (oauth, disconnect, etc.)
├── hooks/
│   └── useInstagramAccounts.ts  # NEW: Hook for account list state
└── store/
    └── accountsStore.ts         # NEW: Zustand store for Instagram accounts
```

### Pattern 1: Instagram OAuth Flow (Full-Page Redirect)

**What:** User clicks "Connect Instagram" → redirects to `/integrations/instagram/authorize` → FastAPI calls Instagram OAuth endpoint → user authorizes on Instagram → Instagram redirects to `/integrations/instagram/callback` with authorization code → backend exchanges code for access/refresh tokens → redirects user back to Settings/Integrations page showing newly connected account.

**When to use:** This is the ONLY OAuth pattern for this phase (per CONTEXT.md decision).

**Backend example:**

```python
# Source: Phase 2 research - full-page redirect OAuth pattern
# File: backend/app/routes/instagram.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

router = APIRouter(prefix="/integrations/instagram", tags=["instagram"])

# OAuth configuration (in app/security/oauth.py)
INSTAGRAM_AUTHORIZE_URL = "https://api.instagram.com/oauth/authorize"
INSTAGRAM_TOKEN_URL = "https://graph.instagram.com/v19.0/oauth/access_token"
INSTAGRAM_USER_INFO_URL = "https://graph.instagram.com/me"

@router.get("/authorize")
async def authorize(request: Request):
    """Redirect user to Instagram OAuth authorization page."""
    redirect_uri = request.url_for("instagram_callback").url
    params = {
        "client_id": settings.INSTAGRAM_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": "instagram_business_profile,instagram_business_management",
        "response_type": "code",
        "state": generate_state_token(),  # Prevent CSRF
    }
    auth_url = f"{INSTAGRAM_AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exchange authorization code for access token."""
    # Verify state token (CSRF protection)
    verify_state_token(state)

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            INSTAGRAM_TOKEN_URL,
            data={
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": request.url_for("instagram_callback").url,
                "code": code,
            }
        )
        token_data = response.json()

    # Store tokens in database (encrypted)
    instagram_account = await create_instagram_account(
        db=db,
        user_id=current_user.id,
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_expires_in=token_data.get("expires_in", 5184000)  # 60 days default
    )

    # Redirect to Settings/Integrations page (showing newly connected account)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/settings/integrations?connected=true&account={instagram_account.id}"
    )
```

**Frontend example:**

```typescript
// Source: Phase 2 research - OAuth flow integration
// File: frontend/src/pages/IntegrationsPage.tsx

import { useNavigate, useSearchParams } from 'react-router-dom';

export function IntegrationsPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const handleConnectInstagram = async () => {
    // Redirect to backend OAuth authorization endpoint (full-page redirect)
    window.location.href = `${API_BASE_URL}/integrations/instagram/authorize`;
  };

  // Display success message if just connected
  const justConnected = searchParams.get('connected') === 'true';

  return (
    <div className="settings-page">
      <h1>Connected Accounts</h1>

      {justConnected && (
        <SuccessAlert>Instagram account connected successfully!</SuccessAlert>
      )}

      <AccountsList>
        {/* Account cards rendered here */}
      </AccountsList>

      <button onClick={handleConnectInstagram} className="btn-primary">
        Add Instagram Account
      </button>
    </div>
  );
}
```

### Pattern 2: Token Refresh Scheduling (Every 50-55 Days)

**What:** APScheduler runs a background job every 50 days that queries database for all Instagram accounts with non-revoked tokens, calls Instagram's refresh endpoint for each, stores new tokens, and updates last_refreshed timestamp. If refresh fails, marks token as expired and queues email notification.

**When to use:** Critical for preventing 60-day token expiration. Instagram tokens expire after 60 days of non-use, but can be refreshed anytime. Refresh every 50 days to prevent expiration.

**Backend example:**

```python
# Source: Instagram Graph API token refresh pattern - 2026
# File: backend/app/tasks/token_refresh.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from sqlalchemy import select
import httpx

async def refresh_instagram_tokens():
    """
    Scheduled task: Refresh all non-expired Instagram tokens.
    Runs every 50 days to prevent 60-day expiration.
    """
    async with AsyncSessionLocal() as db:
        # Get all tokens except already-revoked ones
        result = await db.execute(
            select(InstagramAccount).where(
                InstagramAccount.status != "revoked"
            )
        )
        accounts = result.scalars().all()

        for account in accounts:
            try:
                # Call Instagram refresh endpoint
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{INSTAGRAM_TOKEN_URL}?grant_type=ig_refresh_token&access_token={account.refresh_token}",
                        headers={"Authorization": f"Bearer {settings.INSTAGRAM_APP_SECRET}"}
                    )

                if response.status_code == 200:
                    token_data = response.json()

                    # Update token in database
                    account.access_token = encrypt_token(token_data["access_token"])
                    account.last_refreshed = datetime.utcnow()
                    account.status = "active"
                    await db.commit()

                else:
                    # Token revoked or permission error
                    account.status = "revoked"
                    await db.commit()
                    # Queue email notification (user reconnect needed)

            except Exception as e:
                # Log error, don't fail entire job
                logger.error(f"Token refresh failed for account {account.id}: {e}")

# Schedule in main.py startup
@app.on_event("startup")
async def startup():
    scheduler = AsyncIOScheduler()
    # Refresh tokens every 50 days
    scheduler.add_job(
        refresh_instagram_tokens,
        "interval",
        days=50,
        name="refresh_instagram_tokens"
    )
    scheduler.start()
```

### Pattern 3: Account Status Indicator (Traffic Light System)

**What:** Frontend displays colored badge on each account card reflecting token state: green (active), yellow (expired), red (revoked/error). Status pulled from InstagramAccount.status field in database.

**When to use:** Required per CONTEXT.md - users must see clear status for each connected account.

**Frontend example:**

```typescript
// Source: Traffic light status pattern - CONTEXT.md decision
// File: frontend/src/components/InstagramAccountCard.tsx

interface InstagramAccountProps {
  account: InstagramAccount;
  onReconnect: (accountId: string) => void;
  onDisconnect: (accountId: string) => void;
}

export function InstagramAccountCard({
  account,
  onReconnect,
  onDisconnect,
}: InstagramAccountProps) {
  const statusColors: Record<AccountStatus, string> = {
    active: "bg-green-100 text-green-800",      // Green
    expired: "bg-yellow-100 text-yellow-800",   // Yellow
    revoked: "bg-red-100 text-red-800",         // Red
  };

  return (
    <div className="card account-card">
      <img src={account.profile_picture} alt={account.username} className="avatar" />

      <div className="account-info">
        <h3>{account.username}</h3>
        <p className="account-type">{account.account_type}</p>
        <p className="followers">{account.follower_count.toLocaleString()} followers</p>
      </div>

      <div className="status-section">
        <span className={`status-badge ${statusColors[account.status]}`}>
          {account.status === "active" && "Connected"}
          {account.status === "expired" && "Token Expired"}
          {account.status === "revoked" && "Permission Revoked"}
        </span>

        {account.status === "expired" && (
          <button onClick={() => onReconnect(account.id)} className="btn-secondary">
            Reconnect
          </button>
        )}
      </div>

      <button onClick={() => onDisconnect(account.id)} className="btn-danger btn-small">
        Disconnect
      </button>
    </div>
  );
}
```

### Anti-Patterns to Avoid

- **Storing tokens in frontend localStorage/sessionStorage:** Tokens are sensitive; NEVER store in browser. Store in httpOnly cookies (backend-set) or backend database only.
- **Using popup OAuth instead of full-page redirect:** Popups are blocked in many browsers/devices; full-page redirect is more reliable.
- **Synchronous token refresh on API call:** Don't refresh tokens only when user tries to use an Instagram account. Schedule automatic refresh proactively every 50 days.
- **Hardcoding Instagram app credentials:** Use environment variables; never commit credentials to version control.
- **Single refresh token for multiple users:** Each Instagram account must have its own refresh token; never share tokens between app users.
- **Manual account disconnection without cascade delete:** When user disconnects Instagram account, delete all associated scan history immediately. No soft deletes; per CONTEXT.md, hard delete only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OAuth2 flow implementation | Custom OAuth state machine, code-to-token exchange | Authlib OAuth2Client | Authlib handles PKCE, CSRF, token refresh automatically; avoids security bugs |
| Token refresh scheduling | Custom polling loop or cron script | APScheduler with AsyncIOScheduler | Integrated with Python async; no external services needed; simpler than Celery for this use case |
| Token encryption at rest | Custom encryption logic | SQLAlchemy-Utils EncryptedType or cryptography module | Don't roll custom crypto; use vetted libraries |
| User account enumeration (list connected accounts) | Custom query logic | SQLAlchemy ORM relationships | ORM handles relationship queries efficiently; avoids N+1 bugs |
| Instagram API calls for account info | Custom httpx calls | Authlib with Instagram provider config | Authlib manages token headers, error handling, and provider-specific quirks |

**Key insight:** OAuth2 has many security pitfalls (PKCE bypass, CSRF attacks, token theft, revocation handling). Use battle-tested libraries like Authlib rather than building custom solutions.

---

## Common Pitfalls

### Pitfall 1: Token Expiration Beyond 60 Days

**What goes wrong:** If token refresh isn't scheduled, tokens expire after 60 days of non-use. User's Instagram account becomes disconnected with no way to recover without manual reconnection.

**Why it happens:** Instagram's token lifetime is 60 days, but many developers assume tokens are valid forever or set refresh frequency to 30/90 days instead of 50-55.

**How to avoid:**
- Schedule automatic token refresh every 50 days (5 days before expiration)
- Verify refresh success in logs; alert on failures
- Set token_expires_at in database; use it to calculate when refresh is due

**Warning signs:** Users reporting "Instagram account disconnected" after ~60 days with no visible error in UI.

### Pitfall 2: Storing OAuth Tokens in Browser

**What goes wrong:** XSS attack steals tokens from localStorage/sessionStorage. Attacker gains access to Instagram account without user knowing.

**Why it happens:** Convenience — tokens are "stateless" to client code. But tokens are sensitive credentials; browsers can't protect them from JavaScript.

**How to avoid:**
- Store tokens in database only (encrypted)
- Send tokens from backend when calling Instagram API
- If you must send tokens to frontend, use httpOnly cookies (server-set only, not accessible to JavaScript)

**Warning signs:** Storing token anywhere except server-side database.

### Pitfall 3: Popup OAuth Blocked by Browsers/Devices

**What goes wrong:** User clicks "Connect Instagram" → popup opens → popup blocked by browser or device → user sees blank screen, confused.

**Why it happens:** Modern browsers and mobile devices block unsolicited popups by default (security feature).

**How to avoid:**
- Use full-page redirect OAuth (per CONTEXT.md decision)
- If you must support popups, fallback to redirect for blocked popups
- Test on iOS Safari, Android Chrome, desktop browsers

**Warning signs:** Users on mobile or with popup blockers can't connect accounts.

### Pitfall 4: Not Handling Token Revocation Errors

**What goes wrong:** Token refresh fails (user revoked Instagram app access), but system doesn't mark account as revoked. Next API call uses invalid token → API returns 403 → UI shows cryptic error.

**Why it happens:** Assuming all tokens are valid until proven otherwise. But Instagram lets users revoke app access anytime.

**How to avoid:**
- On token refresh failure, mark account status as "revoked"
- On API call 403, mark account as revoked immediately
- Show clear UI message: "Your Instagram connection was revoked. Reconnect to continue."

**Warning signs:** Users seeing "Instagram API error" instead of actionable "reconnect" message.

### Pitfall 5: Cascade Delete Issues on Disconnect

**What goes wrong:** User disconnects Instagram account, but scan history remains in database orphaned. Later, data becomes inconsistent (foreign key violations, orphaned records).

**Why it happens:** Forget to add CASCADE DELETE constraint on foreign key, or delete Instagram account without deleting related scans.

**How to avoid:**
- Database: Add CASCADE DELETE on instagram_account_id foreign key in scans table
- Backend: Use transaction to atomically delete account and all related scans
- Verify: Test disconnect flow deletes account AND all scans

**Warning signs:** Database errors after account disconnect; orphaned scan records in database.

### Pitfall 6: CSRF Attack on OAuth Callback

**What goes wrong:** Attacker tricks user into clicking malicious link with different authorization code. User's account gets linked to attacker's Instagram account.

**Why it happens:** OAuth callback doesn't validate state parameter (CSRF token).

**How to avoid:**
- Generate random state token before redirecting to Instagram OAuth
- Verify state token matches in callback (Authlib does this automatically)
- Store state in session or Redis for verification

**Warning signs:** Not using state parameter in OAuth flow.

---

## Code Examples

Verified patterns from official sources:

### Example 1: Instagram Account Model (SQLAlchemy)

```python
# Source: Phase 2 research - database schema for multi-account OAuth
# File: backend/app/models/instagram_account.py

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class AccountStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)

    # Instagram account info
    instagram_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    profile_picture = Column(String)
    account_type = Column(String)  # "Personal", "Creator", "Business"
    follower_count = Column(Integer)

    # Token storage (encrypted at rest)
    access_token = Column(LargeBinary, nullable=False)  # Encrypted
    refresh_token = Column(LargeBinary, nullable=False)  # Encrypted

    # Token lifecycle
    token_expires_at = Column(DateTime, nullable=False)
    last_refreshed = Column(DateTime, default=datetime.utcnow)

    # Account status
    status = Column(Enum(AccountStatus), default=AccountStatus.active)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="instagram_accounts")

    # Cascade delete: all scans/analysis for this account are deleted
    scans = relationship(
        "InstagramScan",
        back_populates="instagram_account",
        cascade="all, delete-orphan"
    )
```

### Example 2: Refresh Token Response Schema

```python
# Source: Instagram Graph API token refresh endpoint - 2026
# File: backend/app/schemas/instagram.py

from pydantic import BaseModel
from datetime import datetime

class InstagramAccountCreate(BaseModel):
    instagram_id: str
    username: str
    profile_picture: str
    account_type: str
    follower_count: int

class InstagramAccountResponse(BaseModel):
    id: str
    instagram_id: str
    username: str
    profile_picture: str
    account_type: str
    follower_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenRefreshRequest(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
```

### Example 3: Email Notification on Token Expiration

```python
# Source: Resend transactional email pattern - Phase 1 research
# File: backend/app/tasks/token_refresh.py (expanded)

from resend import Emails

async def notify_token_expired(user_email: str, username: str, reconnect_url: str):
    """Send email notification when Instagram token expires."""
    email_client = Emails(api_key=settings.RESEND_API_KEY)

    await email_client.send(
        to=user_email,
        from_="noreply@antigraivity.app",
        subject="Instagram Connection Expired - Reconnect Now",
        html=f"""
        <h2>Instagram Connection Expired</h2>
        <p>Your Instagram account <strong>@{username}</strong> is no longer connected.</p>
        <p>Click the link below to reconnect:</p>
        <a href="{reconnect_url}" class="btn">Reconnect Instagram</a>
        <p>If you didn't request this, you can ignore this email.</p>
        """,
    )
```

### Example 4: Dashboard Expiry Banner (React)

```typescript
// Source: Dismissible banner pattern - CONTEXT.md decision
// File: frontend/src/components/ExpiryBanner.tsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface ExpiredAccount {
  id: string;
  username: string;
}

export function ExpiryBanner({ account }: { account: ExpiredAccount }) {
  const [dismissed, setDismissed] = useState(false);
  const navigate = useNavigate();

  if (dismissed) return null;

  return (
    <div className="banner banner-warning">
      <div className="banner-content">
        <p>
          Your Instagram account <strong>@{account.username}</strong> connection has expired.
        </p>
        <button
          onClick={() => navigate(`/settings/integrations?focus=${account.id}`)}
          className="btn-link"
        >
          Fix now
        </button>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="btn-close"
        aria-label="Dismiss"
      >
        ✕
      </button>
    </div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Basic Display API | Instagram Graph API exclusively | November 2024 | All integrations must migrate to Graph API; Basic Display deprecated |
| Short-lived tokens only | Long-lived tokens (60 days) | 2020s | Enables 60-day token windows with automatic refresh |
| Manual token refresh on demand | Proactive automatic refresh every 50 days | Best practice emerging 2024-2026 | Prevents token expiration surprises; improves reliability |
| OAuth popup flows | Full-page redirect flows | 2020s-present | Popups blocked on mobile/modern browsers; redirect is standard |
| HTTPS optional | HTTPS mandatory; TLS 1.2+ required | 2025 | All token transmission must use TLS 1.2+; PKCE mandatory for public clients |
| Personal account access | Business/Creator accounts only | November 2024 | Instagram removed personal account access to Graph API |

**Deprecated/outdated:**
- **Basic Display API:** Deprecated November 2024. Replace with Instagram Graph API.
- **Short-lived tokens (1 hour):** Use long-lived tokens (60 days) with automatic refresh instead.
- **Manual user-triggered refresh:** Replace with proactive scheduled refresh every 50 days.

---

## Open Questions

1. **Email notification sender address**
   - What we know: Phase 1 uses Resend for transactional email
   - What's unclear: Should token expiry emails come from noreply@domain or support@domain?
   - Recommendation: Use same sender as other system notifications (verify in Phase 1 email settings)

2. **Account limit enforcement for free tier**
   - What we know: CONTEXT.md says "tier-based" limits; exact limits to be defined based on Phase 10 subscription tiers
   - What's unclear: How do we handle user trying to connect account #2 when at limit? Error message? Upgrade prompt?
   - Recommendation: Plan with Phase 10 planner; design upgrade flow that doesn't block disconnect flow

3. **Instagram account type detection**
   - What we know: Display account_type (Personal/Creator/Business) on card
   - What's unclear: How to detect account type? Instagram Graph API /me endpoint returns it, but need to verify field names in Graph API v19.0
   - Recommendation: Fetch account type during initial OAuth callback; verify API response schema against official Graph API docs

4. **Conflict resolution: Multiple app users + same Instagram account**
   - What we know: CONTEXT.md says default to one-to-one (one Instagram account per app user)
   - What's unclear: If user B tries to connect Instagram account already connected by user A, how to handle? Block? Allow user A to revoke user B?
   - Recommendation: Implement with constraint: unique(instagram_id) in database; reject with "This Instagram account is already connected" message

5. **Token encryption key management**
   - What we know: Tokens must be encrypted at rest
   - What's unclear: Key rotation strategy? Single master key or per-token key?
   - Recommendation: Use single master key for simplicity; if key compromise occurs, refresh all tokens. Document key rotation procedure.

---

## Sources

### Primary (HIGH confidence)

- [Instagram Graph API: Complete Developer Guide for 2026](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2026/) - Token lifetime, refresh process, required scopes, rate limits
- [FastAPI Official Documentation - OAuth2 with Password & Bearer JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - FastAPI OAuth2 security patterns
- [Authlib Documentation - FastAPI OAuth Client](https://docs.authlib.org/en/latest/client/fastapi.html) - OAuth2 client implementation
- [APScheduler Documentation](https://apscheduler.readthedocs.io/) - Background task scheduling for token refresh
- [SQLAlchemy 2.0+ Documentation](https://docs.sqlalchemy.org/) - ORM for Instagram account model
- [Auth.js Database Models](https://authjs.dev/concepts/database-models) - Best practices for OAuth account storage schema

### Secondary (MEDIUM confidence)

- [Refresh long-lived token via Instagram Graph API](https://reshmeeauckloo.com/posts/powerautomate_instagram-refresh-longlived-token/) - Instagram token refresh mechanics
- [How To Renew Instagram Long Lived Access Token](https://www.getfishtank.com/insights/renewing-instagram-access-token) - Token refresh timing
- [React + FastAPI Authentication Guide](https://www.propelauth.com/post/react-fastapi-authentication-guide) - Full-stack OAuth patterns
- [Auth0 Blog: Redirect vs Popup Mode](https://auth0.com/blog/getting-started-with-lock-episode-3-redirect-vs-popup-mode/) - OAuth flow patterns
- [Token Expiry Best Practices](https://zuplo.com/learning-center/token-expiry-best-practices) - Token lifecycle management
- [Implementing Background Job Scheduling in FastAPI with APScheduler](https://rajansahu713.medium.com/implementing-background-job-scheduling-in-fastapi-with-apscheduler-6f5fdabf3186) - APScheduler integration
- [Database Models for Multiple OAuth Accounts](https://repost.aws/questions/QU_u51s2nbQnOV9XDTBJa-7g/how-to-securely-store-oauth-tokens-for-multiple-users-and-apps) - Schema design for multi-account OAuth

### Tertiary (LOW confidence - marked for validation)

- [Instagram API Deprecated?](https://sociavault.com/blog/instagram-api-deprecated-alternative-2026) - API deprecation status (verify against Meta official docs)
- [Card UI Design Best Practices](https://www.nngroup.com/articles/cards-component/) - Frontend card component patterns (general UX, not Instagram-specific)
- [Settings Page UX Design](https://medium.com/design-bootcamp/designing-profile-account-and-setting-pages-for-better-ux-345ef4ca1490) - Settings page layout patterns (general, not Instagram-specific)

---

## Metadata

**Confidence breakdown:**
- **Standard stack:** HIGH - Authlib, APScheduler, SQLAlchemy are industry-standard for OAuth2 + scheduling in Python
- **Architecture:** HIGH - Instagram Graph API docs verified; token refresh pattern is documented best practice
- **Pitfalls:** HIGH - Token expiration and revocation handling are well-documented pitfalls in OAuth implementations
- **Code examples:** MEDIUM-HIGH - Examples follow official patterns but adapted for Phase 2 context; needs validation against actual Instagram API v19.0 response schema

**Research date:** 2026-02-18
**Valid until:** 2026-03-20 (30 days - Instagram API stable, but verify token response schema before implementation)
**Next validation:** Before starting task 02-01, verify Instagram API v19.0 token refresh endpoint response format against official Meta developer docs

---

