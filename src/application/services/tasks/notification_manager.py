import pickle
from dataclasses import dataclass
from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

import structlog

from src.application.services.tasks.celery import (
    send_notification_email,
    send_user_registration_notification,
)
from src.application.services.tasks.email_templates import (
    generate_email_change_html,
    generate_email_changed_html,
    generate_password_changed_html,
    generate_registration_html,
    generate_reset_password_html,
)

logger = structlog.getLogger(__name__)


class NotificationType(Enum):
    """
    Enumeration of notification types with their configuration.

    Each notification type defines a complete configuration for sending
    a specific type of system notification including email subject,
    template function, delivery method, and security requirements.

    Each enum value contains a dictionary with these keys:
        - subject: Email subject line
        - url_path: (optional) Path for verification links
        - template_func: Function that generates HTML content
        - celery_task: Async task for sending the notification
        - needs_token: Whether a security token is required for confirmation of operation
    """

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
    """
    Manages sending HTML notifications via email.

    This service handles the creation and dispatch of various system notifications
    to users, including welcome emails, security alerts, and verification messages.
    It uses async task processing for delivery.

    Attributes:
        username: SMTP Email address used as the sender for notifications
    """

    username: str

    async def send_registration_notification(self, user_data: dict[str, str]) -> None:
        """
        Send HTML welcome email to newly registered user.

        Creates and queues a welcome notification for a newly registered user
        with customized content based on the user's information.

        Args:
            user_data: Dictionary containing user information
                      Must include 'email' key and may include other profile data

        Returns:
            bool: True if notification was successfully queued, False otherwise

        Note:
            This method queues the notification for asynchronous delivery via celery
            and doesn't guarantee the email was actually delivered.
        """
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

            logger.info("Registration notification queued", email=user_data["email"])

        except (ValueError, RuntimeError) as e:
            logger.error("Failed to send notification: ", exception=e)

    async def send_notification(
        self,
        notification_type: NotificationType,
        email: str,
        token: str | None,
        username: str | None,
    ) -> None:
        """
        Universal method to send various types of notifications.

        Creates and queues a notification based on the specified type with
        appropriate subject, content, and security features.

        Args:
            notification_type: Type of notification to send (from NotificationType enum)
            email: Recipient email address
            token: Security token for verification links (required for some notification types)
            username: Optional recipient username for personalization

        Returns:
            bool: True if notification was successfully queued, False otherwise

        Note:
            - For notifications that require tokens (needs_token=True), the token parameter is mandatory
            - Verification URLs are generated for notifications with url_path defined
            - All notifications are queued for asynchronous delivery via celery
        """
        try:
            notification_schema = notification_type.value
            needs_token = notification_schema.get("needs_token", False)

            # Validate token requirement
            if needs_token and not token:
                logger.error(
                    "Token required, but not provided", notification=notification_type
                )
                return

            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = notification_schema["subject"]
            msg["From"] = self.username
            msg["To"] = email

            # Prepare template data
            data = {"email": email}

            # Add verification URL if token provided
            if token and notification_schema.get("url_path"):
                verification_url = f"{'some-frontend-url'}{notification_schema['url_path']}?token={token}"
                data["verification_url"] = verification_url

            if not needs_token:
                data["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

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

            logger.debug(
                "Notification queued.",
                notification=notification_type.value,
                email=email,
            )

        except (ValueError, RuntimeError) as e:
            logger.error(
                "Failed to send notification: ",
                error=e,
                notification=notification_type.value,
            )
