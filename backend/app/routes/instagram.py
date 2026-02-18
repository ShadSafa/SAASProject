"""Instagram OAuth flow and account management routes."""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.instagram import InstagramAccountResponse
from app.crud.instagram import (
    create_instagram_account,
    get_user_instagram_accounts,
    get_instagram_account_by_instagram_id,
    delete_instagram_account,
)
from app.services.instagram import (
    build_authorize_url,
    exchange_code_for_token,
    fetch_instagram_profile,
    encrypt_token,
)
from app.config import settings
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/integrations/instagram", tags=["instagram"])

# In-memory state store for CSRF protection (use Redis in production)
_oauth_states: dict = {}


@router.get("/authorize")
async def authorize(current_user: User = Depends(get_current_active_user)):
    """Redirect user to Instagram OAuth authorization page. INSTA-01."""
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = current_user.id
    return RedirectResponse(url=build_authorize_url(state))


@router.get("/callback")
async def callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Handle OAuth callback from Instagram. INSTA-01, INSTA-02."""
    frontend_url = settings.FRONTEND_URL

    # Handle user denied access
    if error:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=denied")

    # Validate state (CSRF protection)
    if not state or state not in _oauth_states:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=invalid_state")

    expected_user_id = _oauth_states.pop(state)
    if expected_user_id != current_user.id:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=invalid_state")

    # Exchange code for long-lived token
    try:
        access_token, expires_in = await exchange_code_for_token(code)
    except Exception as e:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=token_exchange")

    # Fetch Instagram profile
    try:
        profile = await fetch_instagram_profile(access_token)
    except Exception as e:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=profile_fetch")

    instagram_user_id = profile.get("id")
    if not instagram_user_id:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=invalid_profile")

    # Check if this Instagram account is already linked to another user (one-to-one constraint)
    existing = await get_instagram_account_by_instagram_id(db, instagram_user_id)
    if existing and existing.user_id != current_user.id:
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=already_connected")

    # Enforce tier-based account limit: free tier = 1 account
    # Phase 10 will add subscription lookup; for now enforce free tier limit
    user_accounts = await get_user_instagram_accounts(db, current_user.id)
    if existing is None and len(user_accounts) >= 1:
        # TODO Phase 10: Check subscription tier for higher limits
        return RedirectResponse(url=f"{frontend_url}/settings/integrations?error=account_limit")

    # Store encrypted token
    token_encrypted = encrypt_token(access_token)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    account = await create_instagram_account(
        db=db,
        user_id=current_user.id,
        instagram_user_id=instagram_user_id,
        username=profile.get("username", ""),
        access_token_encrypted=token_encrypted,
        token_expires_at=expires_at,
        profile_picture=profile.get("profile_picture_url"),
        account_type=profile.get("account_type"),
        follower_count=profile.get("followers_count"),
    )

    return RedirectResponse(
        url=f"{frontend_url}/settings/integrations?connected=true&account={account.id}"
    )


@router.get("/accounts", response_model=List[InstagramAccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all Instagram accounts connected by the current user. INSTA-04."""
    return await get_user_instagram_accounts(db, current_user.id)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Hard delete Instagram account and all associated scan history. INSTA-06."""
    deleted = await delete_instagram_account(db, account_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instagram account not found"
        )
