from dataclasses import dataclass, field

import structlog
from uuid6 import uuid7

from src import domain
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.event_sourcing.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from src.domain.user.values import Email, Password, UserId, Username
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.message_broker.events.internal.user_registered import (
    UserRegistered,
)

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class RegisterUserCommand(BaseCommand):
    request: RequestProtocol | None
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    middle_name: str | None = field(default=None)


@dataclass(frozen=True)
class RegisterUserCommandHandler(CommandHandler[RegisterUserCommand, domain.User]):
    _event_publisher: BaseEventPublisher
    _user_writer: BaseUserWriter
    _role_repo: BaseRoleRepository
    _uow: UnitOfWork

    async def handle(self, command: RegisterUserCommand) -> domain.User:
        if await self._user_writer.check_if_field_exists(
            field="username", value=command.username
        ):
            raise UsernameAlreadyExistsException(command.username)

        if await self._user_writer.check_if_field_exists(
            field="email", value=command.email
        ):
            raise EmailAlreadyExistsException(command.email)

        user_role = await self._role_repo.get_role_by_name("user")

        user = domain.User.create(
            user_id=UserId(str(uuid7())),
            username=Username(command.username),
            email=Email(command.email),
            password=Password.create(command.password),
            role=user_role,
        )

        await self._user_writer.create_user(user)
        await self._uow.commit()

        logger.info("User registered", user_id=user.id.to_raw())

        event = UserRegistered(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            first_name=command.first_name,
            last_name=command.last_name,
            middle_name=command.middle_name,
            created_at=user.created_at,
        )

        await self._event_publisher.handle_event(event)

        logger.info("Event created", event_type=event.event_type)

        return user
