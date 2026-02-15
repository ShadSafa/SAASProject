"""Email service for sending transactional emails via Resend."""

from pathlib import Path
from typing import Dict

from resend import Resend
from resend.exceptions import ResendError

from app.config import settings


# Initialize Resend client
resend_client = Resend(api_key=settings.RESEND_API_KEY)


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
        response = resend_client.emails.send(
            {
                "from": f"no-reply@{settings.RESEND_DOMAIN}",
                "to": email,
                "subject": "Verify your email for Instagram Viral Analyzer",
                "html": html_content,
            }
        )

        return {
            "status": "sent",
            "message_id": response.get("id", "")
        }

    except ResendError as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Unexpected error: {str(e)}"
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
        response = resend_client.emails.send(
            {
                "from": f"no-reply@{settings.RESEND_DOMAIN}",
                "to": email,
                "subject": "Reset your password for Instagram Viral Analyzer",
                "html": html_content,
            }
        )

        return {
            "status": "sent",
            "message_id": response.get("id", "")
        }

    except ResendError as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Unexpected error: {str(e)}"
        }
