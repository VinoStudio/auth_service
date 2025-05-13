import hashlib
import secrets
from dataclasses import dataclass

import structlog

from src.application import dto
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.services.tasks.notification_manager import (
    NotificationManager,
    NotificationType,
)
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.repositories import TokenBlackListRepository, TokenType

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class ChangeEmailRequestCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class ChangeEmailRequestCommandHandler(CommandHandler[ChangeEmailRequestCommand, None]):
    _user_reader: BaseUserReader
    _token_repo: TokenBlackListRepository
    _notification_manager: NotificationManager

    async def handle(self, command: ChangeEmailRequestCommand) -> None:
        user_credentials: dto.UserCredentials = (
            await self._user_reader.get_user_credentials_by_email(command.email)
        )

        # Generate secure token
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        # Add token to memory cache
        await self._token_repo.add_reset_token(
            user_credentials.user_id, hashed_token, TokenType.EMAIL_CHANGE
        )

        # Send email with reset link
        await self._notification_manager.send_notification(
            notification_type=NotificationType.CHANGE_EMAIL,
            username=user_credentials.username,
            email=command.email,
            token=hashed_token,
        )
