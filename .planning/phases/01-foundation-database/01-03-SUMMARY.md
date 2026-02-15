---
phase: 01-foundation-database
plan: 03
subsystem: authentication-services
tags: [security, authentication, password-hashing, jwt, tokens, crud, schemas]
dependency-graph:
  requires: [database-schema, models]
  provides: [security-service, auth-token-service, user-crud, api-schemas]
  affects: [all-auth-endpoints]
tech-stack:
  added: [itsdangerous==2.1.2]
  patterns: [argon2id-hashing, jwt-tokens, time-limited-tokens, async-crud, pydantic-validation]
key-files:
  created:
    - backend/app/services/security.py
    - backend/app/services/auth.py
    - backend/app/crud/user.py
    - backend/app/schemas/user.py
    - backend/app/schemas/auth.py
  modified:
    - backend/requirements.txt
decisions:
  - Used Argon2id over bcrypt (OWASP 2026 recommendation)
  - Configured Argon2id with 64MB memory, 3 iterations, 4 threads
  - Separate salts for email verification vs password reset tokens
  - 1-hour default expiration for all token types (JWT, verification, reset)
  - Password strength requires 8+ chars, uppercase, number
  - All CRUD operations use async/await with AsyncSession
metrics:
  duration: 10 minutes
  completed: 2026-02-15T19:59:16Z
  tasks: 3
  commits: 3
---

# Phase 01 Plan 03: Authentication Services Summary

**One-liner:** JWT authentication with Argon2id password hashing using passlib and python-jose, time-limited verification tokens with itsdangerous, and async user CRUD operations with Pydantic schemas.

## Overview

Built the complete authentication service layer with secure password hashing, JWT token management, time-limited verification tokens, and user database operations. This provides the security primitives required for all authentication flows including signup, login, email verification, and password reset.

## Tasks Completed

### Task 1: Create password hashing and JWT token service
**Status:** ✓ Complete
**Commit:** 62ef14f

Created security service with:
- **Argon2id password hashing** using passlib CryptContext
  - Memory cost: 64MB (65536 KB)
  - Time cost: 3 iterations
  - Parallelism: 4 threads
  - Follows OWASP 2026 recommendations (NOT bcrypt or PBKDF2)
- **JWT token creation and verification** using python-jose
  - Default 1-hour expiration
  - Includes `exp` (expiration), `iat` (issued at), `type` (token type)
  - Uses SECRET_KEY from settings (already configured in config.py)
  - Algorithm: HS256
- **Password strength validation**
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one number
  - Returns tuple of (is_valid, error_message)

**Functions exported:**
- `hash_password(password: str) -> str`
- `verify_password(plain_password: str, hashed_password: str) -> bool`
- `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`
- `verify_token(token: str) -> dict | None`
- `validate_password_strength(password: str) -> tuple[bool, str]`

**Testing:** All functions tested successfully with test_security.py. Password hashing verified using Argon2id algorithm, JWT tokens created and decoded correctly, password validation enforces all requirements.

### Task 2: Create email verification and password reset token service
**Status:** ✓ Complete
**Commit:** 42448a5

Created auth token service with:
- **Email verification tokens** using itsdangerous URLSafeTimedSerializer
  - Salt: "email-verification"
  - Default 1-hour expiration (3600 seconds)
  - URL-safe signed tokens
- **Password reset tokens** using same serializer with different salt
  - Salt: "password-reset"
  - Default 1-hour expiration (3600 seconds)
  - Prevents cross-flow token reuse (verification token cannot be used for reset)
- **Time-based expiration** with configurable max_age
- **Signature verification** to prevent tampering

**Functions exported:**
- `generate_verification_token(email: str) -> str`
- `verify_verification_token(token: str, expiration: int = 3600) -> str | None`
- `generate_reset_token(email: str) -> str`
- `verify_reset_token(token: str, expiration: int = 3600) -> str | None`

**Dependencies added:**
- itsdangerous==2.1.2 to requirements.txt

**Testing:** All token functions tested successfully with test_auth_tokens.py. Tokens expire correctly after specified time, invalid tokens return None, separate salts prevent cross-flow reuse.

### Task 3: Create user CRUD operations and Pydantic schemas
**Status:** ✓ Complete
**Commit:** 5dd3c85

Created database operations and API schemas:

**Pydantic Schemas** (`backend/app/schemas/user.py`):
- `UserBase` - Base schema with email field
- `UserCreate` - Signup schema (email, password)
- `UserUpdate` - Update schema (optional email, password)
- `UserResponse` - API response schema (id, email, email_verified, created_at)
  - Uses `from_attributes = True` for Pydantic v2 ORM compatibility

**Auth Schemas** (`backend/app/schemas/auth.py`):
- `Token` - JWT token response (access_token, token_type)
- `TokenData` - Token payload data (email)
- `VerifyEmailRequest` - Email verification request (token)
- `PasswordResetRequest` - Password reset request (email)
- `PasswordResetConfirm` - Password reset confirmation (token, new_password)

**User CRUD Operations** (`backend/app/crud/user.py`):
All operations use AsyncSession for async FastAPI compatibility:
- `get_user_by_email(db, email)` - Find user by email
- `get_user_by_id(db, user_id)` - Find user by ID
- `create_user(db, user)` - Create user with hashed password
- `update_user(db, user_id, user_update)` - Update email or password
- `delete_user(db, user_id)` - Delete user (CASCADE relationships)
- `verify_user_email(db, email)` - Mark email as verified

**Testing:** All Pydantic schemas tested successfully with test_schemas_only.py. Email validation works correctly, optional fields handled properly, all schemas validate input/output. CRUD operations syntax validated (full database tests require PostgreSQL and asyncpg installation).

## Deviations from Plan

None - plan executed exactly as written.

## Security Design Decisions

### Password Hashing
**Decision:** Use Argon2id with specific cost parameters
**Rationale:** OWASP 2026 recommends Argon2id over bcrypt or PBKDF2 for password hashing. Configured parameters (64MB memory, 3 iterations, 4 threads) balance security and performance for typical authentication workloads.

### Token Expiration
**Decision:** Default 1-hour expiration for all token types
**Rationale:** Balances security (short-lived tokens) with user experience (enough time to complete verification/reset flows). Configurable per token type if needed.

### Salt Separation
**Decision:** Different salts for verification vs reset tokens
**Rationale:** Prevents cross-flow token reuse. An email verification token cannot be used for password reset even if intercepted. This is a critical security measure.

### Password Requirements
**Decision:** 8+ chars, uppercase, number minimum
**Rationale:** Balances security with usability. More restrictive than many sites but not overly complex. Can be enhanced later with additional checks (special characters, common password lists).

### Async CRUD
**Decision:** All database operations use async/await
**Rationale:** FastAPI is async-first. Using AsyncSession ensures non-blocking database operations for better performance under load.

## Verification Checklist

- [x] Argon2id password hashing working (not bcrypt or MD5)
- [x] JWT tokens created with 1-hour expiration
- [x] Email verification tokens expire after 1 hour
- [x] Password reset tokens use different salt than verification
- [x] User CRUD operations use AsyncSession
- [x] Pydantic schemas validate input/output
- [x] Password strength validation enforces 8+ chars, uppercase, number
- [x] SECRET_KEY in environment variables (not hardcoded)
- [x] All security functions tested and passing
- [x] All token functions tested and passing
- [x] All schemas tested and passing

## Testing Results

### Security Service Tests
All tests passed:
- Password hashing creates Argon2id hashes
- Password verification accepts correct passwords
- Password verification rejects incorrect passwords
- JWT tokens encode and decode correctly
- JWT tokens include exp, iat, type fields
- Invalid tokens return None
- Password strength validation enforces all requirements

### Auth Token Tests
All tests passed:
- Verification tokens generate and verify correctly
- Reset tokens generate and verify correctly
- Tokens expire after specified time (tested with 2-second expiration)
- Invalid tokens return None
- Cross-flow token reuse prevented (verification token fails reset verification)
- Different salts confirmed for each token type

### Schema Tests
All tests passed:
- Email validation rejects invalid emails
- Optional fields handled correctly in UserUpdate
- All schemas serialize/deserialize correctly
- from_attributes configuration works for ORM compatibility

### CRUD Operations
Code syntax validated. Full integration tests require:
- PostgreSQL database running
- asyncpg package installed (requires C++ build tools on Windows)
- Alembic migrations applied: `alembic upgrade head`

## Next Steps

1. **Phase 01 Plan 04+:** Build authentication endpoints using these services
2. **Database Setup:** Install PostgreSQL and apply migrations to enable full CRUD testing
3. **Integration Tests:** Create end-to-end tests for signup, login, verification flows
4. **Email Service:** Integrate with email service to send verification/reset emails

## Self-Check: PASSED

**Created files verified:**
- FOUND: backend/app/services/security.py
- FOUND: backend/app/services/auth.py
- FOUND: backend/app/crud/user.py
- FOUND: backend/app/schemas/user.py
- FOUND: backend/app/schemas/auth.py

**Modified files verified:**
- FOUND: backend/requirements.txt (itsdangerous added)

**Commits verified:**
- FOUND: 62ef14f (Task 1: Security service)
- FOUND: 42448a5 (Task 2: Auth token service)
- FOUND: 5dd3c85 (Task 3: CRUD operations and schemas)

**Function exports verified:**
```bash
# Security service exports
$ python -c "from app.services.security import hash_password, verify_password, create_access_token, verify_token, validate_password_strength; print('Security service OK')"
Security service OK

# Auth service exports
$ python -c "from app.services.auth import generate_verification_token, verify_verification_token, generate_reset_token, verify_reset_token; print('Auth service OK')"
Auth service OK

# Schemas exports
$ python -c "from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse; from app.schemas.auth import Token, TokenData, VerifyEmailRequest, PasswordResetRequest, PasswordResetConfirm; print('Schemas OK')"
Schemas OK
```

All verification criteria met. Plan 01-03 execution complete.
