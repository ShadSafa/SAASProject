"""
User CRUD operations for database access.

All operations use async/await with AsyncSession for FastAPI compatibility.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.security import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email address.

    Args:
        db: Async database session
        email: Email address to search for

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID.

    Args:
        db: Async database session
        user_id: User ID to search for

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create new user with hashed password.

    Args:
        db: Async database session
        user: User creation data (email, password)

    Returns:
        Created user object
    """
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        email_verified=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    """Update user details.

    Args:
        db: Async database session
        user_id: ID of user to update
        user_update: Fields to update (email, password)

    Returns:
        Updated user if found, None otherwise
    """
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = hash_password(user_update.password)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user and all related data (CASCADE).

    Args:
        db: Async database session
        user_id: ID of user to delete

    Returns:
        True if deleted, False if user not found
    """
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True


async def verify_user_email(db: AsyncSession, email: str) -> User | None:
    """Mark user's email as verified.

    Args:
        db: Async database session
        email: Email address to verify

    Returns:
        Updated user if found, None otherwise
    """
    db_user = await get_user_by_email(db, email)
    if not db_user:
        return None

    db_user.email_verified = True
    await db.commit()
    await db.refresh(db_user)
    return db_user
