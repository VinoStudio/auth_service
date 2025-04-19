import pickle
import ssl
from datetime import datetime
from enum import Enum
from typing import Dict

import structlog
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dataclasses import dataclass
from src.application.services.tasks.email_templates import (
    generate_registration_html,
    generate_reset_password_html,
    generate_email_change_html,
    generate_password_changed_html,
    generate_email_changed_html,
)
from src.application.services.tasks.celery import (
    send_user_registration_notification,
    send_notification_email,
)
from email.message import Message


logger = structlog.getLogger(__name__)


class NotificationType(Enum):
    RESET_PASSWORD = {
        "subject": "Reset Your Password",
        "url_path": "auth/reset-password/confirm",
        "template_func": generate_reset_password_html,
        "celery_task": send_notification_email,
        "needs_token": True,
    }

    CHANGE_EMAIL = {
        "subject": "Verify Your New Email Address",
        "url_path": "auth/email-change/confirm",
        "template_func": generate_email_change_html,
        "celery_task": send_notification_email,
        "needs_token": True,
    }

    PASSWORD_CHANGED = {
        "subject": "Your Password Has Been Changed",
        "template_func": generate_password_changed_html,
        "celery_task": send_notification_email,
        "needs_token": False,
    }

    EMAIL_CHANGED = {
        "subject": "Your Email Address Has Been Changed",
        "template_func": generate_email_changed_html,
        "celery_task": send_notification_email,
        "needs_token": False,
    }


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

    async def send_notification(
        self,
        notification_type: NotificationType,
        email: str,
        token: str | None,
        username: str | None,
    ):
        """
        Universal method to send various types of notifications

        Args:
            notification_type: Type of notification to send
            email: Recipient email
            token: Security token for verification
            username: Optional. Recipient username
        """
        try:
            notification_schema = notification_type.value
            needs_token = notification_schema.get("needs_token", False)

            # Validate token requirement
            if needs_token and not token:
                logger.error(f"Token required for {notification_type} but not provided")
                return False

            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = notification_schema["subject"]
            msg["From"] = self.username
            msg["To"] = email

            # Prepare template data
            data = dict()
            data["email"] = email

            # Add verification URL if token provided
            if token and notification_schema.get("url_path"):
                verification_url = f"{'some-frontend-url'}{notification_schema['url_path']}?token={token}"
                data["verification_url"] = verification_url

            if not needs_token:
                data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if username:
                data["username"] = username

            # Generate HTML content
            html = notification_schema["template_func"](**data)

            # Attach HTML part
            html_part = MIMEText(html, "html")
            msg.attach(html_part)

            msg_pickle = pickle.dumps(msg)

            # Queue for async delivery
            notification_schema["celery_task"].apply_async(
                args=[msg_pickle],
            )

            logger.info(f"{notification_type.value} notification queued for {email}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to send {notification_type.value} notification: {str(e)}"
            )
            return False
