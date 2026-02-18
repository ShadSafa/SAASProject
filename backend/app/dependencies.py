"""Shared FastAPI dependencies to avoid circular imports."""
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.security import verify_token
from app.crud.user import get_user_by_email
from app.models.user import User

_security = HTTPBearer(auto_error=False)


async def get_current_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
    access_token: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency for protected routes - validates JWT token from Bearer header or httpOnly cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
