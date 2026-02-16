"""Test script for security service functions."""

import sys
sys.path.insert(0, 'backend')

from app.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    validate_password_strength
)

print("Testing password hashing...")
# Test password hashing
hashed = hash_password("TestPassword123")
print(f"Hashed: {hashed[:50]}...")
assert verify_password("TestPassword123", hashed), "Password verification failed"
assert not verify_password("WrongPassword", hashed), "Wrong password should not verify"
print("[PASS] Password hashing working")

print("\nTesting JWT tokens...")
# Test JWT tokens
token = create_access_token({"sub": "test@example.com"})
print(f"Token: {token[:50]}...")
payload = verify_token(token)
assert payload is not None, "Token verification failed"
assert payload["sub"] == "test@example.com", "Token payload incorrect"
assert payload["type"] == "access", "Token type incorrect"
print("[PASS] JWT tokens working")

print("\nTesting password strength validation...")
# Test password strength validation
valid, msg = validate_password_strength("Test123")
assert not valid, "Short password should be invalid"
assert "8 characters" in msg, "Error message incorrect"

valid, msg = validate_password_strength("testpassword123")
assert not valid, "No uppercase should be invalid"
assert "uppercase" in msg, "Error message incorrect"

valid, msg = validate_password_strength("TestPassword")
assert not valid, "No number should be invalid"
assert "number" in msg, "Error message incorrect"

valid, msg = validate_password_strength("TestPassword123")
assert valid, "Valid password should pass"
assert msg == "", "Valid password should have no error message"
print("[PASS] Password strength validation working")

print("\nTesting invalid token...")
# Test invalid token
invalid_payload = verify_token("invalid.token.here")
assert invalid_payload is None, "Invalid token should return None"
print("[PASS] Invalid token handling working")

print("\n" + "="*50)
print("[PASS] All security tests passed")
print("="*50)
