from celery import Celery
from typing import Dict
from email.message import Message
import smtplib
import ssl
import pickle
import structlog

from src.settings.config import get_config

logger = structlog.getLogger(__name__)

config = get_config()

celery = Celery(__name__, broker=config.redis.redis_url)

celery.conf.update(
    result_expires=60 * 60 * 24,  # 24 hours
    enable_utc=True,
    accept_content=["json", "pickle"],
    task_serializer="pickle",
    result_serializer="pickle",
    smtp_host=config.smtp.host,
    smtp_port=config.smtp.port,
    smtp_user=config.smtp.user,
    smtp_password=config.smtp.password,
)


@celery.task(
    bind=True,
    max_retries=3,
    name="notifications.send_registration_email",
    autoretry_for=(
        smtplib.SMTPException,
        ConnectionError,
    ),  # Auto-retry for specific exceptions
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    soft_time_limit=30,
    time_limit=60,
)
def send_user_registration_notification(self, msg: bytes):
    msg = pickle.loads(msg)
    """Send HTML notification for new user registration"""
    try:
        with smtplib.SMTP(config.smtp.host, config.smtp.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(config.smtp.user, config.smtp.password)
            server.send_message(msg)

        logger.info("Registration notification sent", email=msg["To"])

    except (ConnectionError, smtplib.SMTPException) as exc:
        logger.error("Failed to send email", email=msg["To"], error=str(exc))
        # Retry task with exponential backoff
        self.retry(exc=exc, countdown=2**self.request.retries)
