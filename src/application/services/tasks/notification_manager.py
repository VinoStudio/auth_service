import pickle
import ssl
from typing import Dict

import structlog
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dataclasses import dataclass
from src.application.services.tasks.email_templates import generate_registration_html
from src.application.services.tasks.celery import send_user_registration_notification
from email.message import Message


logger = structlog.getLogger(__name__)


@dataclass(eq=False)
class NotificationManager:
    """Manages sending HTML notifications via email"""

    server: str
    port: int
    username: str
    password: str

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
