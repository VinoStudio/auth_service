import structlog
from dataclasses import dataclass, field
from typing import Optional
from uuid6 import uuid7

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.exceptions import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
)
from src.application.base.commands import BaseCommand, CommandHandler
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.repositories.oauth.oauth_repo import OAuthAccountRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.message_broker.events.internal.user_registered import (
    UserRegistered,
)


from src.domain.user.values import Email, Username, Password, UserId
import src.domain as domain
import src.application.dto as dto


logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class RegisterOAuthUserCommand(BaseCommand):
    oauth_info: dto.OauthUserCredentials


@dataclass(frozen=True)
class RegisterOAuthUserCommandHandler(
    CommandHandler[RegisterOAuthUserCommand, domain.User]
):
    _event_publisher: BaseEventPublisher
    _user_writer: BaseUserWriter
    _role_repo: BaseRoleRepository
    _oauth_repo: OAuthAccountRepository
    _uow: UnitOfWork

    async def handle(self, command: RegisterOAuthUserCommand) -> domain.User:
        oauth_user_data = command.oauth_info
        user_role = await self._role_repo.get_role_by_name("user")

        user = domain.User.create(
            user_id=UserId(str(uuid7())),
            username=Username(oauth_user_data.username),
            email=Email(oauth_user_data.provider_email),
            password=Password.create(oauth_user_data.password),
            role=user_role,
        )

        oauth_account = domain.OAuthAccount(
            user_id=user.id.to_raw(),
            provider=oauth_user_data.provider_name,
            provider_user_id=oauth_user_data.provider_user_id,
            provider_email=oauth_user_data.provider_email,
        )

        await self._user_writer.create_user(user)
        await self._oauth_repo.create_oauth_account(oauth_account)

        await self._uow.commit()

        logger.info("User registered", user_id=user.id.to_raw())

        event = UserRegistered(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            first_name=oauth_user_data.first_name,
            last_name=oauth_user_data.last_name,
            middle_name=oauth_user_data.middle_name,
            created_at=user.created_at,
        )

        # await self._event_publisher.handle_event(event)

        # logger.info("Event created", event_type=event.event_type)

        return user
