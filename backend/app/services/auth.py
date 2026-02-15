"""
Authentication token service for email verification and password reset.

Uses itsdangerous for time-limited, signed tokens with separate salts
to prevent cross-flow token reuse.
"""

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.config import settings


# Initialize serializer with SECRET_KEY
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# Different salts for different token types (prevents cross-flow reuse)
EMAIL_SALT = "email-verification"
PASSWORD_RESET_SALT = "password-reset"


def generate_verification_token(email: str) -> str:
    """Generate time-limited email verification token.

    Args:
        email: Email address to encode in token

    Returns:
        URL-safe token string
    """
    return serializer.dumps(email, salt=EMAIL_SALT)


def verify_verification_token(token: str, expiration: int = 3600) -> str | None:
    """Verify email verification token (default 1 hour expiration).

    Args:
        token: Token string to verify
        expiration: Maximum age in seconds (default 3600 = 1 hour)

    Returns:
        Email address if valid, None if expired or invalid
    """
    try:
        email = serializer.loads(token, salt=EMAIL_SALT, max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


def generate_reset_token(email: str) -> str:
    """Generate time-limited password reset token.

    Uses different salt than verification tokens to prevent cross-flow reuse.

    Args:
        email: Email address to encode in token

    Returns:
        URL-safe token string
    """
    return serializer.dumps(email, salt=PASSWORD_RESET_SALT)


def verify_reset_token(token: str, expiration: int = 3600) -> str | None:
    """Verify password reset token (default 1 hour expiration).

    Args:
        token: Token string to verify
        expiration: Maximum age in seconds (default 3600 = 1 hour)

    Returns:
        Email address if valid, None if expired or invalid
    """
    try:
        email = serializer.loads(token, salt=PASSWORD_RESET_SALT, max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None
