"""Test script for user CRUD operations.

NOTE: This test requires PostgreSQL to be running and migrations applied.
Run: alembic upgrade head
"""

import sys
import asyncio
sys.path.insert(0, 'backend')

from app.database import AsyncSessionLocal
from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    verify_user_email,
    delete_user
)
from app.schemas.user import UserCreate, UserUpdate


async def test_user_crud():
    """Test all user CRUD operations."""

    # Use unique email to avoid conflicts
    test_email = f"test_{asyncio.get_event_loop().time()}@example.com"

    async with AsyncSessionLocal() as db:
        print("Testing user CRUD operations...")

        # Test 1: Create user
        print(f"\n1. Creating user: {test_email}")
        user_data = UserCreate(email=test_email, password="TestPassword123")
        user = await create_user(db, user_data)
        print(f"   Created user ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Email verified: {user.email_verified}")
        print(f"   Password hashed: {user.hashed_password[:30]}...")
        assert user.email == test_email, "Email should match"
        assert user.email_verified is False, "Email should not be verified initially"
        assert user.hashed_password.startswith("$argon2"), "Password should be Argon2 hash"
        print("   [PASS] User created successfully")

        user_id = user.id

        # Test 2: Get user by email
        print(f"\n2. Getting user by email: {test_email}")
        found_user = await get_user_by_email(db, test_email)
        assert found_user is not None, "User should be found"
        assert found_user.id == user_id, "User ID should match"
        print(f"   [PASS] User found by email")

        # Test 3: Get user by ID
        print(f"\n3. Getting user by ID: {user_id}")
        found_by_id = await get_user_by_id(db, user_id)
        assert found_by_id is not None, "User should be found"
        assert found_by_id.email == test_email, "Email should match"
        print(f"   [PASS] User found by ID")

        # Test 4: Verify user email
        print(f"\n4. Verifying user email")
        verified_user = await verify_user_email(db, test_email)
        assert verified_user is not None, "User should be found"
        assert verified_user.email_verified is True, "Email should be verified"
        print(f"   Email verified: {verified_user.email_verified}")
        print(f"   [PASS] Email verification successful")

        # Test 5: Update user
        new_email = f"updated_{asyncio.get_event_loop().time()}@example.com"
        print(f"\n5. Updating user email to: {new_email}")
        update_data = UserUpdate(email=new_email)
        updated_user = await update_user(db, user_id, update_data)
        assert updated_user is not None, "User should be found"
        assert updated_user.email == new_email, "Email should be updated"
        print(f"   [PASS] User updated successfully")

        # Test 6: Update password
        print(f"\n6. Updating user password")
        old_hash = updated_user.hashed_password
        password_update = UserUpdate(password="NewPassword456")
        updated_user = await update_user(db, user_id, password_update)
        assert updated_user is not None, "User should be found"
        assert updated_user.hashed_password != old_hash, "Password hash should change"
        print(f"   Old hash: {old_hash[:30]}...")
        print(f"   New hash: {updated_user.hashed_password[:30]}...")
        print(f"   [PASS] Password updated successfully")

        # Test 7: Delete user
        print(f"\n7. Deleting user")
        deleted = await delete_user(db, user_id)
        assert deleted is True, "Deletion should succeed"

        # Verify deletion
        deleted_user = await get_user_by_id(db, user_id)
        assert deleted_user is None, "User should not exist after deletion"
        print(f"   [PASS] User deleted successfully")

        # Test 8: Delete non-existent user
        print(f"\n8. Testing deletion of non-existent user")
        deleted = await delete_user(db, 999999)
        assert deleted is False, "Deletion should fail for non-existent user"
        print(f"   [PASS] Non-existent user deletion handled correctly")

    print("\n" + "="*50)
    print("[PASS] All user CRUD tests passed")
    print("="*50)


if __name__ == "__main__":
    try:
        asyncio.run(test_user_crud())
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nMake sure PostgreSQL is running and migrations are applied:")
        print("  alembic upgrade head")
        sys.exit(1)
