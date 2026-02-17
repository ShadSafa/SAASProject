"""Profile management API routes for viewing, updating, and deleting user accounts."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import ProfileResponse, ProfileUpdateRequest, UserUpdate
from app.crud.user import get_user_by_email, update_user, delete_user
from app.services.security import verify_password, validate_password_strength
from app.routes.auth import get_current_active_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.

    Requirements covered:
    - AUTH-08: Profile management (view)
    """
    return current_user


@router.put("", response_model=ProfileResponse)
async def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile (email or password).

    Requirements covered:
    - AUTH-08: Profile management (update)
    """
    # If changing email, check if new email already exists
    if update_data.email and update_data.email != current_user.email:
        existing_user = await get_user_by_email(db, update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )

    # If changing password, verify current password first
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to set new password"
            )

        # Verify current password
        if not verify_password(update_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Validate new password strength
        is_valid, error_msg = validate_password_strength(update_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

    # Update user
    user_update = UserUpdate(
        email=update_data.email,
        password=update_data.new_password  # Will be hashed in CRUD
    )

    updated_user = await update_user(db, current_user.id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

    # If email changed, mark as unverified and send verification email
    if update_data.email and update_data.email != current_user.email:
        updated_user.email_verified = False
        await db.commit()
        await db.refresh(updated_user)

        # Send verification email for new address (sync function - no await)
        from app.services.auth import generate_verification_token
        from app.services.email import send_verification_email

        verification_token = generate_verification_token(updated_user.email)
        email_result = send_verification_email(updated_user.email, verification_token)

        if email_result.get("status") != "sent":
            # Log error but don't fail the update (user can request resend)
            print(f"Warning: Failed to send verification email to {updated_user.email}")

    return updated_user


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account and all associated data.

    Requirements covered:
    - AUTH-09: Account deletion

    Note: CASCADE delete removes:
    - Instagram accounts
    - Scans
    - Viral posts
    - Analyses
    - User usage records
    """
    success = await delete_user(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

    return {
        "message": "Account deleted successfully",
        "email": current_user.email
    }
