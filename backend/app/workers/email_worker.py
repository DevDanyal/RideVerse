"""Email sending tasks."""

import logging
from app.workers.celery_app import app

logger = logging.getLogger("rideverse.workers.email")


@app.task(bind=True, max_retries=3)
def send_email(self, to: str, subject: str, body: str, html: bool = False) -> dict:
    """Send an email message.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.
        html: Whether the body is HTML.

    Returns:
        dict with send status.
    """
    try:
        # TODO: Integrate with email provider (SendGrid, SES, etc.)
        logger.info("sending_email to=%s subject=%s", to, subject)
        return {"status": "sent", "to": to, "subject": subject}
    except Exception as exc:
        logger.exception("email_send_failed to=%s", to)
        self.retry(exc=exc, countdown=60)


@app.task
def send_password_reset_email(to: str, reset_token: str) -> dict:
    """Send a password reset email."""
    return send_email.delay(
        to=to,
        subject="RideVerse - Password Reset",
        body=f"Use this token to reset your password: {reset_token}",
    )


@app.task
def send_welcome_email(to: str, username: str) -> dict:
    """Send a welcome email to new players."""
    return send_email.delay(
        to=to,
        subject="Welcome to RideVerse!",
        body=f"Welcome {username}! Your adventure begins now.",
    )
