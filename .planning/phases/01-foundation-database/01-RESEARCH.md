# Phase 1: Foundation & Database - Research

**Researched:** 2026-02-15
**Domain:** Authentication, User Management, and Database Schema for SaaS
**Confidence:** HIGH

---

## Summary

Phase 1 establishes the foundational infrastructure for the SaaS application: a complete user authentication system and database schema that supports the entire viral content analyzer platform. This phase requires three parallel workstreams: backend authentication/session management, email service integration, and database schema design with migrations.

The primary challenge is ensuring security-first implementation from day one (password hashing, JWT token management, email verification tokens, CORS isolation) rather than patching it later. Secondary challenge is database schema flexibility to accommodate the complex viral post data model while maintaining referential integrity.

**Primary recommendation:** Use Argon2id for password hashing, JWT tokens stored in httpOnly cookies with CSRF protection, Alembic for schema migrations, and Resend for transactional email (simpler API than SendGrid for this phase).

---

## Standard Stack

### Core Backend Authentication

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.110+ | REST API framework with async support | Built-in OAuth2/JWT dependency injection; auto-generated OpenAPI docs; type hints catch auth bugs early |
| SQLAlchemy | 2.0+ | ORM for user and account data | Industry standard, handles complex relationships, async support via SQLAlchemy async |
| Alembic | 1.13+ | Database schema migrations | Version-controls schema changes, tracks history, enables team collaboration |
| python-jose | 3.3+ | JWT token creation/validation | FastAPI ecosystem standard; secure token handling with expiration |
| passlib | 1.7.4+ | Password hashing abstraction | Unified API for multiple hashing algorithms; Argon2 support |
| argon2-cffi | 23.1+ | Argon2id password hashing | OWASP-recommended, winner of Password Hashing Competition (2015); GPU-resistant |
| pydantic | 2.0+ | Data validation | Type-safe request/response schemas; automatic OpenAPI documentation |

### Email Service Integration

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Resend | SDK 2.0+ | Transactional email API | Simple API, excellent for sending verification/reset emails; modern DX |
| EmailValidator | 2.1+ | Email validation before sending | Verify format before hitting email service; catch typos early |
| python-dotenv | 1.0+ | Environment variable management | Store API keys securely (development); not used in production |

### Database & Async Support

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asyncpg | 0.29+ | PostgreSQL async driver | Native async queries for concurrent email verifications and token lookups |
| alembic | 1.13+ | Migration management | Versioning schema changes for team coordination |

### Frontend Authentication

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| axios | 1.6+ | HTTP client for API calls | Intercepts requests to attach JWT token; handles errors centrally |
| zustand | 4.4+ | Client state management | Lightweight global auth state (user, isLoggedIn, token); no Redux boilerplate |
| react-router | 6.20+ | Client routing | Protected routes preventing access to authenticated pages before login |
| react-hook-form | 7.48+ | Form handling | Efficient form state for signup, login, password reset forms |
| zod | 3.22+ | Form validation (frontend) | Type-safe form validation matching backend Pydantic schemas |
| js-cookie | 3.0+ | Cookie management | httpOnly cookies are server-managed, but useful for reading/setting non-httpOnly tokens if needed |

### Installation (Backend)

```bash
# Core FastAPI stack
pip install fastapi uvicorn sqlalchemy alembic asyncpg

# Authentication
pip install python-jose passlib argon2-cffi pydantic

# Email service
pip install resend email-validator python-dotenv

# Testing (optional at this phase but recommended)
pip install pytest pytest-asyncio httpx
```

### Installation (Frontend)

```bash
npm install axios zustand react-router-dom react-hook-form zod js-cookie
npm install -D @hookform/resolvers
```

---

## User Constraints

*(No CONTEXT.md exists for this phase, so all decisions are at Claude's discretion.)*

**Locked decisions from prior research:**
- Python FastAPI + React stack (confirmed in STACK.md)
- PostgreSQL 16+ database (confirmed in STACK.md)
- Third-party email service (Resend or SendGrid) - research recommends Resend for simplicity
- Argon2id for password hashing (OWASP standard in 2026)

---

## Architecture Patterns

### Recommended Project Structure

**Backend (FastAPI):**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app creation, middleware setup
│   ├── config.py                    # Environment variables, settings
│   ├── database.py                  # SQLAlchemy engine, SessionLocal, Base
│   │
│   ├── models/
│   │   ├── user.py                  # User SQLAlchemy model
│   │   ├── instagram_account.py     # InstagramAccount model
│   │   └── ...                       # Other models (scans, posts, etc.)
│   │
│   ├── schemas/                     # Pydantic models for API requests/responses
│   │   ├── user.py                  # UserCreate, UserResponse
│   │   ├── auth.py                  # Token, TokenResponse
│   │   └── ...
│   │
│   ├── crud/                        # Database operations (Create, Read, Update, Delete)
│   │   └── user.py                  # get_user_by_email, create_user, etc.
│   │
│   ├── services/                    # Business logic
│   │   ├── auth.py                  # Token generation, password hashing
│   │   ├── email.py                 # Email verification, password reset emails
│   │   └── ...
│   │
│   ├── routes/                      # API endpoint definitions
│   │   ├── auth.py                  # POST /auth/signup, /auth/login, etc.
│   │   └── ...
│   │
│   ├── middleware/
│   │   ├── cors.py                  # CORS configuration
│   │   ├── auth.py                  # JWT verification middleware
│   │   └── ...
│   │
│   └── utils/
│       ├── security.py              # Hash passwords, create tokens
│       └── ...
│
├── migrations/                      # Alembic migrations directory
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
│
├── tests/
│   ├── test_auth.py
│   └── ...
│
├── requirements.txt
└── .env.example
```

**Frontend (React):**
```
frontend/
├── src/
│   ├── api/
│   │   └── auth.ts                  # API calls to backend auth endpoints
│   │
│   ├── pages/
│   │   ├── SignupPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── VerifyEmailPage.tsx
│   │   ├── PasswordResetPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── ...
│   │
│   ├── components/
│   │   ├── ProtectedRoute.tsx       # Route guard checking auth state
│   │   ├── AuthForm.tsx
│   │   └── ...
│   │
│   ├── store/
│   │   └── authStore.ts             # Zustand auth state (user, token, isLoading)
│   │
│   ├── hooks/
│   │   ├── useAuth.ts               # Custom hook for auth context
│   │   └── ...
│   │
│   ├── types/
│   │   └── auth.ts                  # TypeScript interfaces for auth
│   │
│   ├── utils/
│   │   ├── api.ts                   # Axios instance with token attachment
│   │   └── ...
│   │
│   └── App.tsx
```

---

## Architecture Patterns

### Pattern 1: JWT Token Management (Stateless Sessions)

**What:** JWT tokens contain user identity information (sub, exp, iat) signed with a secret. No server-side session storage needed. Client includes token in Authorization header for subsequent requests.

**When to use:** RESTful APIs with stateless requirements; distributed systems where server can't guarantee sticky sessions.

**Why it matters for Phase 1:** Enables scaling backend horizontally; token expiration and refresh patterns prevent long-lived tokens from becoming attack vectors.

**Implementation outline:**

Backend (FastAPI):
```python
# app/services/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Token creation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Token verification (used in dependency)
async def get_current_user(token: str = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

Frontend (React):
```typescript
// src/utils/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,  // Include httpOnly cookies
});

// Attach token to Authorization header (if storing in state; httpOnly cookies don't need this)
api.interceptors.request.use((config) => {
  // Token is in httpOnly cookie; browser automatically includes it
  // If using localStorage, attach manually:
  // const token = localStorage.getItem('token');
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

**Source:** [FastAPI OAuth2 with JWT - Official Docs](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

### Pattern 2: Email Verification Token Flow

**What:** User receives time-limited token via email. Token is valid for ~30 minutes. User clicks link or enters code to verify email, backend validates token, and marks email as verified.

**When to use:** Confirming email ownership before granting access; preventing spam signup.

**Implementation outline:**

Backend:
```python
# app/services/email.py
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt=settings.EMAIL_SALT)

def verify_verification_token(token: str, expiration: int = 3600) -> str | None:  # 1 hour
    try:
        email = serializer.loads(token, salt=settings.EMAIL_SALT, max_age=expiration)
        return email
    except Exception:
        return None

# In route handler
@router.post("/auth/send-verification-email")
async def send_verification_email(request: SendVerificationRequest):
    user = await get_user_by_email(request.email)
    if not user:
        return {"status": "sent"}  # Don't reveal if email exists

    token = generate_verification_token(user.email)
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    await send_email_via_resend(
        to=user.email,
        subject="Verify your email",
        html_template=render_email_template("verify_email.html", link=verification_link)
    )
    return {"status": "sent"}

@router.post("/auth/verify-email")
async def verify_email(request: VerifyEmailRequest):
    email = verify_verification_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await get_user_by_email(email)
    user.email_verified = True
    await db.commit()
    return {"status": "verified"}
```

Frontend:
```typescript
// src/pages/VerifyEmailPage.tsx
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../utils/api';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      return;
    }

    api.post('/auth/verify-email', { token })
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'));
  }, [searchParams]);

  return (
    <div>
      {status === 'verifying' && <p>Verifying your email...</p>}
      {status === 'success' && <p>Email verified! You can now log in.</p>}
      {status === 'error' && <p>Verification failed. Link may be expired.</p>}
    </div>
  );
}
```

**Source:** [FastAPI Best Practices - Email Verification](https://fastlaunchapi.dev/blog/how-to-implement-auth)

---

### Pattern 3: Password Reset with Time-Limited Tokens

**What:** User requests password reset, receives email with time-limited link, clicks link to set new password, token is invalidated after use.

**When to use:** Password reset, email verification, any time-sensitive, single-use action.

**Implementation:** Similar to email verification, but token is used once then invalidated.

---

### Pattern 4: CORS & CSRF Protection

**What:** CORS (Cross-Origin Resource Sharing) whitelist restricts which frontend origins can call backend. CSRF tokens or SameSite cookies prevent cross-site request forgery.

**When to use:** Separating frontend and backend domains; protecting against browser-based attacks.

**Implementation outline:**

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # e.g., "https://localhost:3000"
    allow_credentials=True,                  # Allow httpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# httpOnly cookies are immune to XSS attacks; CSRF protection is automatic
# with SameSite=Strict (default in modern browsers)
```

**Source:** [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)

---

### Anti-Patterns to Avoid

- **Storing JWT in localStorage:** Vulnerable to XSS attacks. Use httpOnly cookies instead (browser doesn't expose to JavaScript).
- **Not hashing passwords:** Using plaintext or weak algorithms (MD5, SHA1). Use Argon2id with proper memory/time costs.
- **Hardcoding secrets:** Never commit SECRET_KEY, API keys, database URLs. Use environment variables with .env files (development only).
- **Not validating email verification:** Allowing unverified emails to access the app. Require email_verified=true check on protected endpoints.
- **Long-lived tokens:** Access tokens valid for weeks/months; use short expiration (1 hour) with refresh tokens for longer sessions.
- **Not rate limiting auth endpoints:** Allows brute force attacks on login, password reset. Use slowapi for per-IP rate limiting.
- **CORS too permissive:** allow_origins=["*"] defeats protection. Whitelist specific frontend domains only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hashing function | argon2-cffi (via passlib) | Argon2id is GPU-resistant, memory-hard; rolling your own is cryptographically dangerous |
| JWT token signing | Manual JWT parsing | python-jose | Handles edge cases (algorithm confusion attacks, key rotation), secure default algorithms |
| Email validation | Simple regex | email-validator library | RFC 5322 compliance is surprisingly complex; library handles edge cases |
| Database migrations | Manual SQL files | Alembic | Version control, auto-diff generation, rollback capability; manual SQL is error-prone |
| Session management | Custom session storage | JWT tokens + httpOnly cookies | Proven patterns; custom sessions are hard to scale horizontally |
| Rate limiting | Manual request counting | slowapi middleware | Distributed rate limiting, Redis support, handles edge cases |

**Key insight:** Authentication is one of the most exploited domains in web applications. Off-the-shelf libraries like passlib, python-jose, and Alembic have been battle-tested across millions of applications. Custom implementations almost always miss edge cases (timing attacks, algorithm confusion, token cloning, etc.).

---

## Common Pitfalls

### Pitfall 1: Email Verification Token Never Expires or Has Wrong Expiration

**What goes wrong:** User receives verification email, delays clicking link for weeks. Token is still valid, allowing account takeover. Or token expires too quickly (5 minutes), user misses email notification.

**Why it happens:** Expiration configuration feels like "no token is best"; actually, specific expiration (30-60 min) balances security and UX.

**How to avoid:**
- Set expiration to 30-60 minutes (long enough for user to check email, short enough to limit exposure)
- Log token generation timestamp; verify in validation
- Test with tokens approaching expiration to verify behavior

**Warning signs:**
- Tokens working weeks after email sent
- Verification links frequently failing for users checking email after 10 minutes

**Source:** [URLSafeTimedSerializer best practices](https://itsdangerous.palletsprojects.com/en/2.1.x/serializer/)

---

### Pitfall 2: Password Reset Token Reused or Not Invalidated

**What goes wrong:** User requests password reset, gets token, attacker intercepts and uses same token weeks later to reset password again.

**Why it happens:** Developers forget that reset tokens should be single-use.

**How to avoid:**
- Generate new token each request
- Mark token as "used" or store only current valid token (not all historical tokens)
- Invalidate token on successful password change

**Warning signs:**
- Old password reset links still work after months
- Users report password changes they didn't initiate

---

### Pitfall 3: Jwt Not Validated on Every Protected Request

**What goes wrong:** JWT token is validated at login, but not on subsequent requests. Attacker steals token, uses it indefinitely even after expiration.

**Why it happens:** Developers forget to add dependency injection to all protected routes.

**How to avoid:**
- Use FastAPI dependency injection on ALL protected routes
- Every route requiring auth should have `current_user = Depends(get_current_user)` parameter
- Test by creating token, waiting past expiration, and verifying request fails

**Code example:**
```python
@router.get("/profile", dependencies=[Depends(get_current_user)])
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user  # Dependency validates token on EVERY call
```

**Warning signs:**
- API endpoints that don't require auth should
- Token expiration not working as expected

---

### Pitfall 4: Database Schema Doesn't Support Email Uniqueness or Allows SQL Injection

**What goes wrong:** Two users register with same email, or attacker bypasses login by injecting SQL.

**Why it happens:** Unique constraint missing on email column; or hand-rolling SQL queries instead of using ORM.

**How to avoid:**
- Add UNIQUE constraint on users.email in migrations
- Always use SQLAlchemy ORM for queries, never string concatenation
- Test unique constraint by attempting duplicate email signup

**Code example:**
```python
# models/user.py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)  # Unique + indexed
    hashed_password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Migrations will enforce this at database level
# alembic revision --autogenerate -m "Add unique email constraint"
```

**Warning signs:**
- Able to sign up with duplicate emails
- Database accepts malformed input

---

### Pitfall 5: CORS Not Restricted or Secrets in Code

**What goes wrong:** `allow_origins=["*"]` allows any website to call backend; SECRET_KEY in source code exposed on GitHub.

**Why it happens:** "Easier" to develop with permissive settings; developers forget environment variables aren't automatic.

**How to avoid:**
- Set `allow_origins=[settings.FRONTEND_URL]` to specific domain only
- Move all secrets to .env file, load via settings
- Use `.env.example` to show what variables are needed (without values)
- Never commit .env or secrets to Git

**Warning signs:**
- CORS middleware configured before CORS issue occurs (reactive, not proactive)
- SECRET_KEY or API keys visible in git history

---

### Pitfall 6: Session/Token Not Persisting Across Browser Restarts

**What goes wrong:** User logs in, closes browser, reopens—logged out. Or token stored in RAM doesn't survive refresh.

**Why it happens:** Token in memory (not persisted) or httpOnly cookie with wrong SameSite policy.

**How to avoid:**
- Use httpOnly cookies (set-cookie header); browser persists automatically
- If using localStorage (AVOID for tokens), use refresh tokens: store refresh token in httpOnly cookie, short-lived access token in memory
- Test by logging in, closing browser, reopening, checking auth status

**Backend (httpOnly cookie setup):**
```python
response = JSONResponse({"status": "success"})
response.set_cookie(
    key="access_token",
    value=token,
    max_age=3600,  # 1 hour
    httponly=True,  # JavaScript can't access
    secure=True,    # HTTPS only (production)
    samesite="strict",  # CSRF protection
)
return response
```

**Warning signs:**
- Logged-out after browser restart
- Token expired errors on page refresh

---

## Code Examples

Verified patterns from official sources and current best practices:

### Database Schema (SQLAlchemy Models)

```python
# app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

**Source:** [SQLAlchemy ORM Tutorial - Official Docs](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)

---

### User Registration Endpoint

```python
# app/routes/auth.py
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr, BaseModel

from app.models.user import User
from app.services.security import hash_password, create_access_token
from app.services.email import send_verification_email_resend
from app.crud.user import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/signup", response_model={"status": str})
async def signup(request: UserCreateRequest, session: AsyncSession = Depends(get_db)):
    # Check if user exists
    existing_user = await get_user_by_email(session, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    hashed_pwd = hash_password(request.password)

    # Create user
    new_user = await create_user(
        session,
        email=request.email,
        hashed_password=hashed_pwd,
        email_verified=False
    )

    # Send verification email
    verification_token = generate_verification_token(new_user.email)
    await send_verification_email_resend(
        email=new_user.email,
        token=verification_token
    )

    return {"status": "success", "message": "Verification email sent"}
```

**Source:** [FastAPI Dependency Injection & ORM Integration](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

### Login Endpoint with JWT Token

```python
# app/routes/auth.py (continued)
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from datetime import timedelta

@router.post("/login", response_model=TokenResponse)
async def login(request: UserCreateRequest, session: AsyncSession = Depends(get_db)):
    # Retrieve user
    user = await get_user_by_email(session, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify email before allowing login
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email."
        )

    # Verify password
    from app.services.security import verify_password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token (1 hour expiration)
    access_token_expires = timedelta(hours=1)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # Set httpOnly cookie
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict"
    )
    return response
```

---

### Protected Endpoint with Dependency Injection

```python
# app/routes/profile.py
from fastapi import Depends

@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at
    }

# Dependency for verifying JWT on every request
async def get_current_user(token: HTTPAuthCredentials = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

---

### Alembic Migration (Database Schema Versioning)

```bash
# Initialize Alembic in project
alembic init migrations

# Auto-generate migration from SQLAlchemy models
alembic revision --autogenerate -m "Create user table"

# Review generated file in migrations/versions/
# Then apply to database
alembic upgrade head
```

**Generated migration file (migrations/versions/xxxx_create_user_table.py):**
```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

**Source:** [Alembic Official Documentation](https://alembic.sqlalchemy.org/en/latest/)

---

### Email Verification Service (Resend)

```python
# app/services/email.py
from resend import Resend

resend = Resend(api_key=settings.RESEND_API_KEY)

async def send_verification_email(email: str, token: str):
    """Send email verification link."""
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    response = resend.emails.send(
        {
            "from": f"no-reply@{settings.RESEND_DOMAIN}",
            "to": email,
            "subject": "Verify your email",
            "html": f"""
            <p>Click the link below to verify your email:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>This link expires in 1 hour.</p>
            """,
        }
    )

    if response.get("id"):
        return {"status": "sent"}
    else:
        raise Exception(f"Failed to send email: {response}")
```

**Source:** [Resend FastAPI Integration Guide](https://resend.com/fastapi)

---

### React Authentication Hook

```typescript
// src/hooks/useAuth.ts
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { useAuthStore } from '../store/authStore';

export const useAuth = () => {
  const navigate = useNavigate();
  const { user, setUser, setLoading, setError } = useAuthStore();

  const signup = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/signup', { email, password });
      // Frontend handles email verification redirect
      navigate('/verify-email-pending', { state: { email } });
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Signup failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, navigate]);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      const userData = response.data;
      setUser(userData);
      navigate('/dashboard');
      return userData;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, navigate, setUser]);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }, [setUser, navigate]);

  return { user, signup, login, logout };
};
```

**Source:** [React Hook Form Patterns](https://react-hook-form.com/form-builder)

---

### React Authentication State (Zustand)

```typescript
// src/store/authStore.ts
import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  email_verified: boolean;
}

interface AuthStore {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isLoading: false,
  error: null,
  setUser: (user) => set({ user }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));

// Usage in component:
// const { user, setUser, setLoading } = useAuthStore();
```

---

## Database Schema (Complete for Phase 1)

```sql
-- Created via Alembic migration

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);

-- Additional tables required for Instagram integration and scans
-- Will be created in later phases, but schema needs to be extensible

CREATE TABLE instagram_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instagram_user_id VARCHAR NOT NULL,
    instagram_username VARCHAR,
    access_token VARCHAR,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_instagram_accounts_user_id ON instagram_accounts(user_id);
CREATE UNIQUE INDEX ix_instagram_accounts_unique_per_user ON instagram_accounts(user_id, instagram_user_id);

-- For tracking usage/subscription quotas
CREATE TABLE user_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    scans_count INTEGER DEFAULT 0,
    last_reset_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_user_usage_user_id_month ON user_usage(user_id, month);
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MD5/SHA1 password hashing | Argon2id (OWASP 2026 standard) | 2015+ | GPU-resistant; slows down brute force attacks exponentially |
| Session storage in database | JWT tokens (stateless) | 2010s+ | Scales horizontally; no session synchronization needed |
| CORS disabled entirely | Specific origin whitelist | 2020s+ | Balances security and functionality; prevents drive-by attacks |
| localStorage for tokens | httpOnly cookies | 2023+ | XSS-proof; requires CSRF consideration but more secure overall |
| Manual password reset flow | Token-based with expiration | 2010s+ | Single-use tokens, prevents replay attacks |
| Python 2 / Django | Python 3.10+ / FastAPI | 2020s+ | Async support, type hints, modern AI ecosystem |

**Deprecated/outdated:**
- **Flask for new projects:** Still viable but lacks native async. FastAPI is industry standard for API-first.
- **Session-based authentication:** Works but requires server-side storage; JWT is simpler for distributed systems.
- **Plaintext password storage:** Never acceptable; Argon2id is industry minimum.
- **CORS disabled:** Dangerous; specific whitelist is required in 2026.

---

## State of Phase 1 Complexity

Phase 1 is the **highest-complexity phase proportionally** due to:

1. **Security-critical:** Passwords, tokens, sessions are attack surface. Mistakes here cascade to entire app.
2. **Cross-domain concerns:** Frontend state management, backend JWT logic, database schema all must align.
3. **Integration points:** Email service, password hashing library, JWT library all must work together.
4. **Testing requirements:** Every auth path needs unit + integration tests (signup, email verification, login, logout, password reset).

**Why it's hard:**
- No visible product yet (no dashboard, no data)
- Many moving parts (backend, frontend, email service, database)
- Security mistakes are catastrophic but non-obvious

---

## Open Questions

1. **Refresh Token Strategy**
   - What we know: Access tokens expire in 1 hour; need way to get new tokens without re-logging in
   - What's unclear: Where to store refresh token? httpOnly cookie (secure, automatic) or localStorage (requires manual management but more control)?
   - Recommendation: Use httpOnly cookie for refresh token; browser automatically includes it. Implement token refresh endpoint that validates refresh token and returns new access token.

2. **Email Service Cost**
   - What we know: Resend or SendGrid both viable
   - What's unclear: Exact pricing for Phase 1 volumes (assume 1000 users = 1000 signup emails + password resets)
   - Recommendation: Resend free tier covers ~100 emails/day; sufficient for MVP. Monitor usage, switch to SendGrid if exceeding free tier.

3. **Async Database Queries**
   - What we know: FastAPI supports async/await; SQLAlchemy supports async via asyncpg
   - What's unclear: All CRUD operations need async versions; is this boilerplate or does ORM handle it?
   - Recommendation: Use SQLAlchemy 2.0+ with `select()` API and `AsyncSession`. ORM handles most of the async plumbing; minimal boilerplate.

4. **Password Complexity Validation**
   - What we know: Need to validate passwords at signup
   - What's unclear: How strict? Minimum 8 chars? Uppercase/numbers/special chars?
   - Recommendation: Start with simple (minimum 8 chars, at least 1 uppercase, 1 number). Can tighten later based on user feedback.

---

## Sources

### Primary (HIGH confidence)

- **FastAPI Official Security Tutorial** - [OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Token creation, validation, dependency injection patterns
- **SQLAlchemy 2.0 Documentation** - [ORM Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) - Model definition, async support
- **Alembic Official Docs** - [Database Migrations](https://alembic.sqlalchemy.org/en/latest/) - Migration versioning, auto-generation
- **OWASP Password Hashing Guide** - Password hashing algorithms and Argon2id recommendation
- **FastAPI Best Practices 2026** - [FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026) - Production-ready auth patterns

### Secondary (MEDIUM confidence)

- **TestDriven.io - Securing FastAPI with JWT** - Real-world FastAPI + JWT implementation patterns
- **Resend Documentation** - [FastAPI Integration](https://resend.com/fastapi) - Email service setup for FastAPI
- **React Hook Form Patterns** - Form handling and validation for auth pages
- **Zustand Documentation** - Client-side state management for auth
- **NIST Cybersecurity Framework** - Email verification and session management best practices

### Tertiary (Sources cited in research)

- **Password Hashing Comparison 2026** - [guptadeepak.com](https://guptadeepak.com/the-complete-guide-to-password-hashing-argon2-vs-bcrypt-vs-scrypt-vs-pbkdf2-2026/)
- **itsdangerous Documentation** - Time-limited token serialization
- **sqlalchemy-authorization patterns** - RBAC foundations (for future phases)

---

## Metadata

**Confidence breakdown:**
- **Standard stack:** HIGH - FastAPI, SQLAlchemy, Alembic, Argon2id are industry standard in 2026
- **Architecture patterns:** HIGH - JWT + httpOnly cookies verified across official docs and multiple sources
- **Pitfalls:** MEDIUM-HIGH - Based on FastAPI security blogs and OWASP, but edge cases always possible
- **Email service:** MEDIUM - Resend vs SendGrid choice depends on volume; both viable
- **React state management:** MEDIUM - Zustand vs Context API both work; choice affects later phases

**Research date:** 2026-02-15
**Valid until:** ~2026-03-15 (30 days for stable libraries) or until new FastAPI/SQLAlchemy major releases

---

## Next Steps for Planning

Once this research is accepted, the planner will:

1. **Break Phase 1 into tasks:**
   - Database schema + migrations (Alembic setup, user table, instagram_accounts, user_usage)
   - Backend auth service (password hashing, JWT token creation/validation)
   - API endpoints (signup, login, logout, email verification, password reset, profile management)
   - Email service integration (Resend setup, email templates)
   - Frontend auth pages (signup, login, verify email, password reset, profile)
   - Frontend auth state (Zustand store, API client)
   - Test coverage (unit tests for security functions, integration tests for auth flows)

2. **Success criteria:**
   - User can signup, receive verification email, verify email, login, stay logged in after refresh
   - JWT tokens expire in 1 hour and require refresh
   - User can reset password via email link
   - User can update profile and delete account
   - Database schema supports future phases (instagram_accounts, scans, posts, analyses)

3. **Estimated effort:**
   - Database: 2-3 days (schema design, migrations, testing)
   - Backend auth: 4-5 days (endpoints, JWT, password hashing, email integration)
   - Frontend auth: 3-4 days (pages, forms, state management)
   - Testing & polish: 2-3 days (edge cases, error handling)
   - Total: 6-8 plans (rough estimates; exact breakdown by planner)
