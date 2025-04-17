import structlog
from dataclasses import dataclass, field
from typing import Optional
from uuid6 import uuid7

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.exceptions import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
    TokenExpiredException,
    PasswordTokenExpiredException,
)
from src.application.base.commands import BaseCommand, CommandHandler
from src.infrastructure.base.repository import BaseUserWriter, BaseUserReader
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.message_broker.events.internal.user_registered import (
    UserRegistered,
)


from src.domain.user.values import Email, Username, Password, UserId
import src.domain as domain
from src.infrastructure.repositories import TokenBlackListRepository

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
    _uow: UnitOfWork

    async def handle(self, command: ResetUserPasswordCommand) -> domain.User:
        user_token = await self._token_repo.get_reset_password_token(command.token)
        if not user_token:
            raise PasswordTokenExpiredException("")

        user: domain.User = await self._user_reader.get_user_by_id(user_token)

        user.set_password(new_pass=command.new_password)
        await self._token_repo.invalidate_reset_password_token(command.token)

        await self._user_writer.update_user(user)
        await self._uow.commit()

        logger.info("User password reset", user_id=user_token)

        return user
