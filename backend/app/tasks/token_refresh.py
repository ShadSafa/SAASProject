"""
Background task: Refresh Instagram access tokens before 60-day expiration.
Runs every 50 days to maintain active connections.
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.instagram_account import InstagramAccount, AccountStatus
from app.services.instagram import refresh_access_token, encrypt_token, decrypt_token
from app.services.email import send_token_expired_email

logger = logging.getLogger(__name__)

# Module-level scheduler instance (initialized on startup)
_scheduler: AsyncIOScheduler = None


async def refresh_instagram_tokens():
    """
    Refresh all non-revoked Instagram tokens.
    Called by scheduler every 50 days.
    """
    logger.info("Starting scheduled Instagram token refresh")
    refreshed = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        # Get all accounts except already-revoked ones
        result = await db.execute(
            select(InstagramAccount).where(
                InstagramAccount.status != AccountStatus.revoked
            )
        )
        accounts = result.scalars().all()
        logger.info(f"Refreshing tokens for {len(accounts)} accounts")

        for account in accounts:
            try:
                # Decrypt current token for API call
                current_token = decrypt_token(account.access_token)

                # Call Instagram refresh endpoint
                new_token, expires_in = await refresh_access_token(current_token)

                # Store encrypted new token
                account.access_token = encrypt_token(new_token)
                account.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                account.status = AccountStatus.active
                await db.commit()
                refreshed += 1
                logger.info(f"Successfully refreshed token for account {account.id} (@{account.username})")

            except Exception as e:
                logger.error(f"Token refresh failed for account {account.id} (@{account.username}): {e}")
                # Mark as revoked (permission revoked or token invalid)
                account.status = AccountStatus.revoked
                await db.commit()
                failed += 1

                # Send expiry email notification (INSTA-03: email notification on token expiry)
                try:
                    await _notify_token_expired(db, account)
                except Exception as email_err:
                    logger.error(f"Failed to send expiry email for account {account.id}: {email_err}")

    logger.info(f"Token refresh complete: {refreshed} refreshed, {failed} failed/revoked")


async def _notify_token_expired(db, account: InstagramAccount):
    """Send email notification to user when token expires."""
    from app.crud.user import get_user_by_id
    from app.config import settings
    user = await get_user_by_id(db, account.user_id)
    if not user:
        return

    reconnect_url = f"{settings.FRONTEND_URL}/settings/integrations"
    send_token_expired_email(
        to_email=user.email,
        username=account.username,
        reconnect_url=reconnect_url,
    )


def start_scheduler():
    """Initialize and start the APScheduler."""
    global _scheduler
    _scheduler = AsyncIOScheduler()

    # Refresh tokens every 50 days (Instagram tokens expire after 60 days)
    _scheduler.add_job(
        refresh_instagram_tokens,
        trigger="interval",
        days=50,
        id="refresh_instagram_tokens",
        name="Refresh Instagram Access Tokens",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Token refresh scheduler started (runs every 50 days)")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Token refresh scheduler stopped")
