"""Email service for sending transactional emails via Resend."""

import logging
from pathlib import Path
from typing import Dict

import resend

from app.config import settings

logger = logging.getLogger(__name__)


# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


def render_template(template_name: str, context: Dict[str, str]) -> str:
    """
    Render an HTML email template with provided context.

    Args:
        template_name: Name of the template file (e.g., "verify_email.html")
        context: Dictionary of variables to interpolate into template

    Returns:
        Rendered HTML string
    """
    template_path = Path(__file__).parent.parent / "templates" / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(**context)


def send_verification_email(email: str, token: str) -> Dict[str, str]:
    """
    Send email verification link to user.

    Args:
        email: User's email address
        token: Verification token to include in link

    Returns:
        Dictionary with status and message_id or error
    """
    try:
        # Construct verification link
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        # Render HTML template
        html_content = render_template(
            "verify_email.html",
            {
                "verification_link": verification_link,
                "email": email
            }
        )

        # Send email via Resend
        response = resend.Emails.send(
            {
                "from": f"no-reply@{settings.RESEND_DOMAIN}",
                "to": [email],  # to field must be a list in v2.0
                "subject": "Verify your email for Instagram Viral Analyzer",
                "html": html_content,
            }
        )

        return {
            "status": "sent",
            "message_id": response.get("id", "")
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


def send_token_expired_email(to_email: str, username: str, reconnect_url: str) -> Dict[str, str]:
    """
    Send notification that Instagram token has expired. INSTA-03.

    Args:
        to_email: User's email address
        username: Instagram username that was disconnected
        reconnect_url: URL to reconnect the Instagram account

    Returns:
        Dictionary with status and message_id or error
    """
    try:
        response = resend.Emails.send({
            "from": f"no-reply@{settings.RESEND_DOMAIN}",
            "to": [to_email],  # to field must be a list in v2.0
            "subject": f"Instagram Connection Expired - Reconnect @{username}",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
                <h2 style="color: #1a1a1a;">Instagram Connection Expired</h2>
                <p style="color: #4a4a4a;">Your Instagram account <strong>@{username}</strong> has been disconnected
                because the access token expired.</p>
                <p style="color: #4a4a4a;">Click the button below to reconnect your account and continue
                analyzing viral content.</p>
                <a href="{reconnect_url}"
                   style="display: inline-block; padding: 12px 24px; background-color: #7c3aed; color: white;
                   text-decoration: none; border-radius: 8px; font-weight: 600; margin: 16px 0;">
                    Reconnect Instagram Account
                </a>
                <p style="color: #9a9a9a; font-size: 14px; margin-top: 24px;">
                    If you no longer wish to use this service, you can ignore this email.
                </p>
            </div>
            """,
        })

        return {
            "status": "sent",
            "message_id": response.get("id", "")
        }

    except Exception as e:
        logger.error(f"Failed to send token expired email to {to_email}: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


def send_password_reset_email(email: str, token: str) -> Dict[str, str]:
    """
    Send password reset link to user.

    Args:
        email: User's email address
        token: Password reset token to include in link

    Returns:
        Dictionary with status and message_id or error
    """
    try:
        # Construct reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        # Render HTML template
        html_content = render_template(
            "password_reset.html",
            {
                "reset_link": reset_link,
                "email": email
            }
        )

        # Send email via Resend
        response = resend.Emails.send(
            {
                "from": f"no-reply@{settings.RESEND_DOMAIN}",
                "to": [email],  # to field must be a list in v2.0
                "subject": "Reset your password for Instagram Viral Analyzer",
                "html": html_content,
            }
        )

        return {
            "status": "sent",
            "message_id": response.get("id", "")
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
