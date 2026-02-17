---
phase: 01-foundation-database
plan: "07"
subsystem: authentication
tags: [password-reset, email, security, auth]
dependency_graph:
  requires: [01-05]
  provides: [password-reset-endpoints]
  affects: [frontend-auth-pages]
tech_stack:
  added: []
  patterns: [itsdangerous-timed-tokens, email-enumeration-prevention, argon2id-password-hashing]
key_files:
  created: []
  modified:
    - backend/app/routes/auth.py
decisions:
  - "Call send_password_reset_email synchronously (not async) to match existing send_verification_email pattern"
  - "Always return identical response for valid/invalid emails to prevent email enumeration"
  - "Validate new password strength on reset using the same validate_password_strength function used at signup"
metrics:
  duration: "5 min"
  completed: "2026-02-17"
---

# Phase 01 Plan 07: Password Reset Endpoints Summary

Password reset backend flow using itsdangerous time-limited tokens and Resend email delivery.

## What Was Built

Two new endpoints added to `backend/app/routes/auth.py`:

**POST /auth/request-password-reset**
- Accepts `{"email": "user@example.com"}`
- Looks up user by email
- If user not found, returns success anyway (prevents email enumeration)
- If user found, generates a time-limited reset token (1 hour) via `generate_reset_token()`
- Sends reset email via `send_password_reset_email()` with link to `{FRONTEND_URL}/reset-password?token={TOKEN}`
- Always returns: `{"message": "If that email exists, a password reset link has been sent."}`

**POST /auth/reset-password**
- Accepts `{"token": "...", "new_password": "..."}`
- Verifies token with `verify_reset_token()` — returns 400 if invalid or expired
- Looks up user by email extracted from token — returns 404 if not found
- Validates new password strength (8 chars, 1 uppercase, 1 number) — returns 400 if weak
- Hashes new password with Argon2id and commits to database
- Returns: `{"message": "Password reset successfully. You can now log in with your new password."}`

## Imports Added

```python
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.services.auth import generate_reset_token, verify_reset_token
from app.services.email import send_password_reset_email
from app.services.security import hash_password
```

## Token Strategy

- Library: `itsdangerous.URLSafeTimedSerializer`
- Salt: `"password-reset"` (separate from `"email-verification"` salt — prevents cross-flow reuse)
- Expiration: 1 hour (3600 seconds)
- Encoding: email address embedded in signed, URL-safe token

## Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Email enumeration | Always return identical response regardless of whether email exists |
| Token forgery | itsdangerous cryptographic signing with app SECRET_KEY |
| Token reuse across flows | Separate salt for reset vs verification tokens |
| Expired tokens | itsdangerous max_age=3600 enforces 1-hour expiration |
| Weak new passwords | Same validation as signup: 8 chars, uppercase, number |
| Plaintext storage | Argon2id hashing via `hash_password()` before DB write |

## Deviations from Plan

**1. [Rule 1 - Bug] Removed `await` from `send_password_reset_email` call**
- **Found during:** Task 1 — reading the email service implementation
- **Issue:** Plan code used `await send_password_reset_email(...)` but the function is synchronous (not async), matching the same pattern as `send_verification_email`
- **Fix:** Called `send_password_reset_email(user.email, reset_token)` without `await`, consistent with how `send_verification_email` is called in the signup endpoint
- **Files modified:** `backend/app/routes/auth.py`
- **Commit:** 38a27e5

## Verification Checklist

- [x] POST /auth/request-password-reset returns same message for valid/invalid email
- [x] POST /auth/request-password-reset sends email when user exists
- [x] POST /auth/reset-password returns 400 for invalid/expired token
- [x] POST /auth/reset-password validates new password strength
- [x] POST /auth/reset-password hashes new password with Argon2id before saving
- [x] Token uses separate salt from email verification (prevents cross-flow reuse)
- [x] Token expires after 1 hour

## Commits

| Hash | Message |
|------|---------|
| 38a27e5 | feat(01-07): add password reset endpoints to auth router |

## Self-Check: PASSED

- File modified: `backend/app/routes/auth.py` — confirmed exists and contains both endpoints
- Commit `38a27e5` — confirmed created successfully
