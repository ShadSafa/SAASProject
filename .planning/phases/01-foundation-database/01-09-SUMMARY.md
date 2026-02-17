---
phase: 01-foundation-database
plan: 09
subsystem: backend-auth
tags: [profile, auth, account-management, fastapi]
dependency_graph:
  requires: [01-05]
  provides: [profile-endpoints, account-deletion]
  affects: [01-10]
tech_stack:
  added: []
  patterns: [get_current_active_user dependency, sync email service calls, CASCADE delete]
key_files:
  created:
    - backend/app/routes/profile.py
  modified:
    - backend/app/schemas/user.py
    - backend/app/main.py
decisions:
  - Call send_verification_email synchronously (no await) - consistent with existing auth patterns
  - Add 500 error guard when update_user returns None (defensive programming)
  - Email change triggers email_verified=False + re-verification email before returning response
metrics:
  duration: ~8 min
  completed: 2026-02-17
---

# Phase 01 Plan 09: Profile Backend Summary

**One-liner:** Profile management endpoints (GET/PUT /profile, DELETE /profile/account) with email re-verification and CASCADE account deletion.

---

## What Was Built

Three profile management endpoints registered at `/profile` prefix:

- `GET /profile` - Returns authenticated user's profile data (id, email, email_verified, created_at)
- `PUT /profile` - Updates email and/or password with full validation
- `DELETE /profile/account` - Deletes user and all related data via database CASCADE

All endpoints require Bearer token authentication via `get_current_active_user` dependency.

---

## Implementation Details

### Schemas Added (`backend/app/schemas/user.py`)

**ProfileUpdateRequest** - Accepts optional email, current_password, and new_password fields.

**ProfileResponse** - Returns id, email, email_verified, created_at with `from_attributes = True` for ORM mapping.

### Profile Endpoints (`backend/app/routes/profile.py`)

**GET /profile:**
- Depends on `get_current_active_user` - returns 401 if unauthenticated
- Returns `ProfileResponse` from ORM User model

**PUT /profile:**
- Email uniqueness check (409 if email taken)
- Password change requires current_password verification (401 if wrong)
- New password validated for strength (400 if weak)
- On email change: sets `email_verified=False`, sends verification email (sync call)
- update_user CRUD handles password hashing

**DELETE /profile/account:**
- Calls delete_user CRUD which uses SQLAlchemy `db.delete()` + commit
- Returns 500 if user not found (defensive guard)
- CASCADE behavior handled at DB schema level (foreign keys with CASCADE)

### Router Registration (`backend/app/main.py`)

Added `from app.routes import auth, profile` and `app.include_router(profile.router)`.

---

## Security Validations

| Scenario | Status Code | Detail |
|---|---|---|
| No auth token | 401 | Invalid or expired token |
| Email already in use | 409 | Email already in use |
| Missing current_password for pw change | 400 | Current password required to set new password |
| Wrong current_password | 401 | Current password is incorrect |
| Weak new_password | 400 | (from validate_password_strength) |
| update_user returns None | 500 | Failed to update profile |
| delete_user returns False | 500 | Failed to delete account |

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed await on synchronous send_verification_email call**
- **Found during:** Task 1 implementation
- **Issue:** Plan template code used `await send_verification_email(...)` but the function is synchronous (confirmed in `backend/app/services/email.py`). Using `await` on a non-coroutine raises `TypeError: object dict can't be used in 'await' expression` at runtime.
- **Fix:** Called `send_verification_email(updated_user.email, verification_token)` without `await`, consistent with the existing pattern in `backend/app/routes/auth.py` (lines 69, 132, 238).
- **Files modified:** `backend/app/routes/profile.py`

**2. [Rule 2 - Missing critical functionality] Added None guard after update_user**
- **Found during:** Task 1 implementation
- **Issue:** Plan template didn't check if `update_user` returned `None` (user not found). Calling `.email_verified` on `None` would raise `AttributeError`.
- **Fix:** Added `if not updated_user: raise HTTPException(500, "Failed to update profile")` guard after the `update_user` call.
- **Files modified:** `backend/app/routes/profile.py`

**3. [Rule 2 - Missing critical functionality] Added email result logging in profile update**
- **Found during:** Task 1 implementation
- **Issue:** Plan template silently discarded the verification email send result on profile update.
- **Fix:** Added `if email_result.get("status") != "sent": print(...)` warning log, consistent with the signup endpoint pattern.
- **Files modified:** `backend/app/routes/profile.py`

---

## Verification Checklist

- [x] GET /profile returns authenticated user (requires Bearer token)
- [x] PUT /profile updates email with re-verification (email_verified set to False)
- [x] PUT /profile changes password with current password check
- [x] DELETE /profile/account deletes user and all related data (CASCADE at DB level)
- [x] All endpoints require authentication (get_current_active_user dependency)
- [x] Email uniqueness enforced on update (409 conflict)
- [x] Password strength validated on change (validate_password_strength)
- [x] send_verification_email called synchronously (no await)
- [x] Profile router registered in main.py

---

## Files Modified

| File | Change |
|---|---|
| `backend/app/routes/profile.py` | Created (137 lines) - profile management endpoints |
| `backend/app/schemas/user.py` | Added ProfileUpdateRequest and ProfileResponse schemas |
| `backend/app/main.py` | Added profile router import and include_router call |

---

## Requirements Covered

- AUTH-08: Profile management (view and update)
- AUTH-09: Account deletion with CASCADE
