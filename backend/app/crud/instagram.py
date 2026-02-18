from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.instagram_account import InstagramAccount, AccountStatus
from typing import Optional, List


async def get_user_instagram_accounts(db: AsyncSession, user_id: int) -> List[InstagramAccount]:
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.user_id == user_id))
    return result.scalars().all()


async def get_instagram_account_by_instagram_id(db: AsyncSession, instagram_user_id: str) -> Optional[InstagramAccount]:
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.instagram_user_id == instagram_user_id))
    return result.scalar_one_or_none()


async def create_instagram_account(
    db: AsyncSession,
    user_id: int,
    instagram_user_id: str,
    username: str,
    access_token_encrypted: bytes,
    token_expires_at,
    profile_picture: Optional[str] = None,
    account_type: Optional[str] = None,
    follower_count: Optional[int] = None,
) -> InstagramAccount:
    account = InstagramAccount(
        user_id=user_id,
        instagram_user_id=instagram_user_id,
        username=username,
        access_token=access_token_encrypted,
        token_expires_at=token_expires_at,
        profile_picture=profile_picture,
        account_type=account_type,
        follower_count=follower_count,
        status=AccountStatus.active,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def delete_instagram_account(db: AsyncSession, account_id: int, user_id: int) -> bool:
    """Hard delete account and all associated data (CASCADE handles related records)."""
    result = await db.execute(
        select(InstagramAccount).where(
            InstagramAccount.id == account_id,
            InstagramAccount.user_id == user_id
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        return False
    await db.delete(account)
    await db.commit()
    return True


async def update_instagram_account_status(db: AsyncSession, account_id: int, status: AccountStatus) -> Optional[InstagramAccount]:
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.id == account_id))
    account = result.scalar_one_or_none()
    if account:
        account.status = status
        await db.commit()
        await db.refresh(account)
    return account
