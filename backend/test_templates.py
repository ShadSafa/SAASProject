"""Test email templates rendering without requiring Resend API."""

from pathlib import Path


def render_template(template_name: str, context: dict) -> str:
    """Render an HTML email template with provided context."""
    template_path = Path(__file__).parent / "app" / "templates" / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(**context)


# Test verification email template
print("Testing verification email template...")
verification_html = render_template(
    "verify_email.html",
    {
        "verification_link": "http://localhost:3000/verify-email?token=test-token-123",
        "email": "test@example.com"
    }
)
assert "test-token-123" in verification_html
assert "Verify Email" in verification_html
print("[PASS] Verification email template renders correctly")

# Test password reset email template
print("\nTesting password reset email template...")
reset_html = render_template(
    "password_reset.html",
    {
        "reset_link": "http://localhost:3000/reset-password?token=reset-token-456",
        "email": "test@example.com"
    }
)
assert "reset-token-456" in reset_html
assert "Reset Password" in reset_html
print("[PASS] Password reset email template renders correctly")

print("\n[PASS] All template tests passed!")
