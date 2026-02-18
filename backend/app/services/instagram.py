import httpx
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from app.config import settings

INSTAGRAM_AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
INSTAGRAM_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
INSTAGRAM_LONG_LIVED_TOKEN_URL = "https://graph.instagram.com/access_token"
INSTAGRAM_REFRESH_TOKEN_URL = "https://graph.instagram.com/refresh_access_token"
INSTAGRAM_ME_URL = "https://graph.instagram.com/me"


def get_fernet() -> Optional[Fernet]:
    """Get Fernet cipher for token encryption. Returns None if key not configured."""
    if not settings.TOKEN_ENCRYPTION_KEY:
        return None
    return Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> bytes:
    """Encrypt access token for database storage. Falls back to plain bytes if no key configured."""
    fernet = get_fernet()
    if fernet:
        return fernet.encrypt(token.encode())
    return token.encode()  # Development fallback (no encryption)


def decrypt_token(token_bytes: bytes) -> str:
    """Decrypt access token from database storage."""
    fernet = get_fernet()
    if fernet:
        return fernet.decrypt(token_bytes).decode()
    return token_bytes.decode()  # Development fallback


def build_authorize_url(state: str) -> str:
    """Build Instagram OAuth authorization URL."""
    from urllib.parse import urlencode
    params = {
        "client_id": settings.INSTAGRAM_APP_ID,
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "scope": "instagram_business_basic,instagram_business_manage_messages",
        "response_type": "code",
        "state": state,
    }
    return f"{INSTAGRAM_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> Tuple[str, int]:
    """Exchange authorization code for short-lived token, then upgrade to long-lived token.
    Returns (long_lived_access_token, expires_in_seconds).
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Exchange code for short-lived token
        response = await client.post(
            INSTAGRAM_TOKEN_URL,
            data={
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
                "code": code,
            }
        )
        response.raise_for_status()
        short_lived = response.json()
        short_token = short_lived["access_token"]

        # Step 2: Exchange short-lived for long-lived token (60 days)
        ll_response = await client.get(
            INSTAGRAM_LONG_LIVED_TOKEN_URL,
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "access_token": short_token,
            }
        )
        ll_response.raise_for_status()
        long_lived = ll_response.json()
        return long_lived["access_token"], long_lived.get("expires_in", 5184000)  # 60 days default


async def fetch_instagram_profile(access_token: str) -> dict:
    """Fetch user profile from Instagram Graph API /me endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            INSTAGRAM_ME_URL,
            params={
                "fields": "id,username,profile_picture_url,account_type,followers_count",
                "access_token": access_token,
            }
        )
        response.raise_for_status()
        return response.json()


async def refresh_access_token(access_token: str) -> Tuple[str, int]:
    """Refresh a long-lived Instagram token. Returns (new_token, expires_in_seconds)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            INSTAGRAM_REFRESH_TOKEN_URL,
            params={
                "grant_type": "ig_refresh_token",
                "access_token": access_token,
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"], data.get("expires_in", 5184000)
