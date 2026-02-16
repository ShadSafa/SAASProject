"""Test script to verify schemas and imports work correctly.

This test does NOT require a database connection.
"""

import sys
sys.path.insert(0, 'backend')

print("Testing schema imports...")

# Test user schemas
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
print("[PASS] User schemas imported successfully")

# Test auth schemas
from app.schemas.auth import (
    Token,
    TokenData,
    VerifyEmailRequest,
    PasswordResetRequest,
    PasswordResetConfirm
)
print("[PASS] Auth schemas imported successfully")

# Test CRUD imports (should work even without database)
from app.crud.user import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
    verify_user_email
)
print("[PASS] User CRUD operations imported successfully")

# Test schema validation
print("\nTesting schema validation...")

# Test UserCreate schema
user_create = UserCreate(email="test@example.com", password="TestPassword123")
assert user_create.email == "test@example.com"
assert user_create.password == "TestPassword123"
print("[PASS] UserCreate schema validates correctly")

# Test UserUpdate schema with optional fields
user_update = UserUpdate()
assert user_update.email is None
assert user_update.password is None
print("[PASS] UserUpdate schema with optional fields works")

user_update_with_email = UserUpdate(email="new@example.com")
assert user_update_with_email.email == "new@example.com"
assert user_update_with_email.password is None
print("[PASS] UserUpdate schema with partial data works")

# Test Token schema
token = Token(access_token="abc123")
assert token.access_token == "abc123"
assert token.token_type == "bearer"
print("[PASS] Token schema validates correctly")

# Test PasswordResetConfirm schema
reset = PasswordResetConfirm(token="reset_token", new_password="NewPass123")
assert reset.token == "reset_token"
assert reset.new_password == "NewPass123"
print("[PASS] PasswordResetConfirm schema validates correctly")

print("\n" + "="*50)
print("[PASS] All schema and import tests passed")
print("="*50)
print("\nNote: Full CRUD tests require PostgreSQL.")
print("Run test_user_crud.py when database is available.")
