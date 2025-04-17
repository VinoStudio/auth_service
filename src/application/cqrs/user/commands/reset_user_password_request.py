import hashlib
import secrets
from dataclasses import dataclass
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.services.tasks.notification_manager import NotificationManager
from src.infrastructure.base.repository import BaseUserReader

import src.application.dto as dto
from src.infrastructure.repositories import TokenBlackListRepository


@dataclass(frozen=True)
class ResetPasswordRequestCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class ResetPasswordRequestCommandHandler(
    CommandHandler[ResetPasswordRequestCommand, None]
):
    _user_reader: BaseUserReader
    _token_repo: TokenBlackListRepository
    _notification_manager: NotificationManager

    async def handle(self, command: ResetPasswordRequestCommand) -> None:
        user_credentials: dto.UserCredentials = (
            await self._user_reader.get_user_credentials_by_email_or_username(
                command.email
            )
        )

        # Generate secure token
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        # Add token to memory cache
        await self._token_repo.add_reset_password_token(
            user_credentials.user_id, hashed_token
        )

        # Send email with reset link
        await self._notification_manager.send_reset_password_email(
            email=command.email, reset_token=hashed_token
        )
