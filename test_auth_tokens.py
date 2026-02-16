"""Test script for authentication token service."""

import sys
import time
sys.path.insert(0, 'backend')

from app.services.auth import (
    generate_verification_token,
    verify_verification_token,
    generate_reset_token,
    verify_reset_token,
    EMAIL_SALT,
    PASSWORD_RESET_SALT
)

print("Testing email verification tokens...")
# Test verification token generation and validation
token = generate_verification_token("test@example.com")
print(f"Verification token: {token[:30]}...")

# Valid token
email = verify_verification_token(token)
assert email == "test@example.com", "Email should match"
print("[PASS] Valid verification token works")

# Test expiration (2 second expiration)
print("\nTesting token expiration (waiting 3 seconds)...")
token_2s = generate_verification_token("expire@example.com")
time.sleep(3)
expired_email = verify_verification_token(token_2s, expiration=2)
assert expired_email is None, "Token should be expired"
print("[PASS] Token expiration working correctly")

# Test invalid token
print("\nTesting invalid token...")
invalid_email = verify_verification_token("invalid.token.here")
assert invalid_email is None, "Invalid token should return None"
print("[PASS] Invalid token handling works")

print("\nTesting password reset tokens...")
# Test reset token generation and validation
reset_token = generate_reset_token("reset@example.com")
print(f"Reset token: {reset_token[:30]}...")

# Valid reset token
reset_email = verify_reset_token(reset_token)
assert reset_email == "reset@example.com", "Reset email should match"
print("[PASS] Valid reset token works")

# Test that salts are different (prevent cross-flow reuse)
print("\nTesting salt separation...")
assert EMAIL_SALT != PASSWORD_RESET_SALT, "Salts should be different"
print(f"Email salt: {EMAIL_SALT}")
print(f"Reset salt: {PASSWORD_RESET_SALT}")

# Verify token created with one salt cannot be verified with another
verification_token = generate_verification_token("test@example.com")
# Try to verify verification token as reset token (should fail)
cross_flow_email = verify_reset_token(verification_token)
assert cross_flow_email is None, "Cross-flow token reuse should fail"
print("[PASS] Different salts prevent cross-flow token reuse")

print("\n" + "="*50)
print("[PASS] All authentication token tests passed")
print("="*50)
