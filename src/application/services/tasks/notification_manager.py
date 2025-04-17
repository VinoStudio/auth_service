import pickle
import ssl
from typing import Dict

import structlog
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dataclasses import dataclass
from src.application.services.tasks.email_templates import (
    generate_registration_html,
    generate_reset_password_html,
)
from src.application.services.tasks.celery import (
    send_user_registration_notification,
    send_password_reset_notification,
)
from email.message import Message


logger = structlog.getLogger(__name__)


@dataclass(eq=False)
class NotificationManager:
    """Manages sending HTML notifications via email"""

    username: str

    async def send_registration_notification(self, user_data: Dict[str, str]):
        """Send HTML welcome email to newly registered user"""
        try:
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Welcome to Our Platform!"
            msg["From"] = self.username
            msg["To"] = user_data["email"]

            # Generate HTML content
            html = generate_registration_html(user_data)

            # Attach HTML part
            html_part = MIMEText(html, "html")
            msg.attach(html_part)

            msg = pickle.dumps(msg)

            send_user_registration_notification.apply_async(
                args=[msg],
            )

            logger.info(f"Registration notification queued for {user_data['email']}")

            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    async def send_reset_password_email(self, email: str, reset_token: str):
        """Send password reset email with secure token link"""
        try:
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Reset Your Password"
            msg["From"] = self.username
            msg["To"] = email

            # Create reset URL with frontend support
            reset_url = (
                f"{"some-frontend-url"}auth/reset-password/confirm?token={reset_token}"
            )

            # Generate HTML content
            html = generate_reset_password_html(email, reset_url)

            # Attach HTML part
            html_part = MIMEText(html, "html")
            msg.attach(html_part)

            msg = pickle.dumps(msg)

            # Queue for async delivery (assuming you have a similar task for password resets)
            send_password_reset_notification.apply_async(
                args=[msg],
            )

            logger.info(f"Password reset notification queued for {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset notification: {str(e)}")
            return False
