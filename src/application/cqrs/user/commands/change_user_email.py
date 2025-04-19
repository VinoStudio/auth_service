import structlog
from dataclasses import dataclass


from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.exceptions import EmailTokenExpiredException
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.services.tasks.notification_manager import (
    NotificationManager,
    NotificationType,
)
from src.infrastructure.base.repository import BaseUserWriter, BaseUserReader
from src.infrastructure.base.uow import UnitOfWork


from src.domain.user.values import Email, Username, Password, UserId
import src.domain as domain
from src.infrastructure.repositories import TokenBlackListRepository, TokenType

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class ChangeUserEmailCommand(BaseCommand):
    token: str
    new_email: str


@dataclass(frozen=True)
class ChangeUserEmailCommandHandler(
    CommandHandler[ChangeUserEmailCommand, domain.User]
):
    _user_writer: BaseUserWriter
    _user_reader: BaseUserReader
    _token_repo: TokenBlackListRepository
    _notification_manager: NotificationManager
    _uow: UnitOfWork

    async def handle(self, command: ChangeUserEmailCommand) -> domain.User:
        user_token = await self._token_repo.get_reset_token(
            command.token, TokenType.EMAIL_CHANGE
        )
        if not user_token:
            raise EmailTokenExpiredException("")

        user: domain.User = await self._user_reader.get_user_by_id(user_token)

        old_email = user.email.to_raw()

        user.set_email(email=Email(command.new_email))
        await self._token_repo.invalidate_reset_token(
            command.token, TokenType.EMAIL_CHANGE
        )

        await self._user_writer.update_user(user)
        await self._uow.commit()

        await self._notification_manager.send_notification(
            notification_type=NotificationType.EMAIL_CHANGED,
            username=user.username.to_raw(),
            email=old_email,
            token=None,
        )

        logger.info("User email has been changed", user_id=user_token)

        return user
