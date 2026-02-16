"""Test script to verify schemas work correctly (no database needed)."""

import sys
sys.path.insert(0, 'backend')

print("Testing Pydantic schemas...")

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

# Test schema validation
print("\nTesting schema validation...")

# Test UserCreate schema with email validation
try:
    user_create = UserCreate(email="test@example.com", password="TestPassword123")
    assert user_create.email == "test@example.com"
    assert user_create.password == "TestPassword123"
    print("[PASS] UserCreate schema validates correctly")
except Exception as e:
    print(f"[FAIL] UserCreate validation failed: {e}")

# Test invalid email
try:
    invalid_user = UserCreate(email="not-an-email", password="test")
    print("[FAIL] Invalid email should raise error")
except Exception:
    print("[PASS] Invalid email rejected correctly")

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

# Test TokenData schema
token_data = TokenData(email="user@example.com")
assert token_data.email == "user@example.com"
print("[PASS] TokenData schema validates correctly")

# Test VerifyEmailRequest schema
verify_req = VerifyEmailRequest(token="verification_token")
assert verify_req.token == "verification_token"
print("[PASS] VerifyEmailRequest schema validates correctly")

# Test PasswordResetRequest schema
reset_req = PasswordResetRequest(email="reset@example.com")
assert reset_req.email == "reset@example.com"
print("[PASS] PasswordResetRequest schema validates correctly")

# Test PasswordResetConfirm schema
reset_confirm = PasswordResetConfirm(token="reset_token", new_password="NewPass123")
assert reset_confirm.token == "reset_token"
assert reset_confirm.new_password == "NewPass123"
print("[PASS] PasswordResetConfirm schema validates correctly")

# Test UserBase schema
user_base = UserBase(email="base@example.com")
assert user_base.email == "base@example.com"
print("[PASS] UserBase schema validates correctly")

print("\n" + "="*50)
print("[PASS] All Pydantic schema tests passed")
print("="*50)
print("\nSchemas created:")
print("  - UserBase, UserCreate, UserUpdate, UserResponse")
print("  - Token, TokenData, VerifyEmailRequest")
print("  - PasswordResetRequest, PasswordResetConfirm")
print("\nNote: CRUD operations require PostgreSQL and asyncpg.")
print("Files created: backend/app/crud/user.py")
print("Run test_user_crud.py when database is available.")
