from dataclasses import dataclass

import structlog

from src import domain
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.exceptions import (
    PasswordTokenExpiredException,
)
from src.application.services.tasks.notification_manager import (
    NotificationManager,
    NotificationType,
)
from src.infrastructure.base.repository import BaseUserReader, BaseUserWriter
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.repositories import TokenBlackListRepository, TokenType

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class ResetUserPasswordCommand(BaseCommand):
    token: str
    new_password: str


@dataclass(frozen=True)
class ResetUserPasswordCommandHandler(
    CommandHandler[ResetUserPasswordCommand, domain.User]
):
    _user_writer: BaseUserWriter
    _user_reader: BaseUserReader
    _token_repo: TokenBlackListRepository
    _notification_manager: NotificationManager
    _uow: UnitOfWork

    async def handle(self, command: ResetUserPasswordCommand) -> domain.User:
        user_token = await self._token_repo.get_reset_token(
            command.token, TokenType.PASSWORD_RESET
        )
        if not user_token:
            raise PasswordTokenExpiredException("")

        user: domain.User = await self._user_reader.get_user_by_id(user_token)

        old_email = user.email.to_raw()

        user.set_password(new_pass=command.new_password)
        await self._token_repo.invalidate_reset_token(
            command.token, TokenType.PASSWORD_RESET
        )

        await self._user_writer.update_user(user)
        await self._uow.commit()

        await self._notification_manager.send_notification(
            notification_type=NotificationType.PASSWORD_CHANGED,
            username=user.username.to_raw(),
            email=old_email,
            token=None,
        )

        logger.info("User password reset", user_id=user_token)

        return user
