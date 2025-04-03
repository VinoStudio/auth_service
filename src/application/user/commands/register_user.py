from dataclasses import dataclass, field
from typing import Optional
from uuid6 import uuid7

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.exceptions import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
)
from src.application.base.commands import BaseCommand, CommandHandler
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.repositories import UserWriter, RoleRepository
from src.infrastructure.message_broker.events.user_registered import UserRegistered


from src.domain.user.values import Email, Username, Password, UserId
import src.domain as domain


@dataclass(frozen=True)
class RegisterUserCommand(BaseCommand):
    username: str
    email: str
    password: str
    request: Optional[RequestProtocol]
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

        await self._event_publisher.handle_event(
            UserRegistered(
                user_id=user.id.to_raw(),
                username=user.username.to_raw(),
                first_name=command.first_name,
                last_name=command.last_name,
                middle_name=command.middle_name,
                created_at=user.created_at,
            )
        )

        return user
