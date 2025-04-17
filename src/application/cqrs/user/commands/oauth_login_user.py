from dataclasses import dataclass
from typing import Optional

from uuid6 import uuid7
from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.session.session_manager import BaseSessionManager
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.dto.token import TokenPair
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.exceptions import PasswordIsInvalidException
from src.application.services.security.oauth_manager import OAuthManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader, BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.message_broker.events import UserRegistered

from src.domain.user.values import Password, UserId, Username, Email

import src.domain as domain
import src.application.dto as dto
import structlog

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class OAuthLoginUserCommand(BaseCommand):
    user_id: str
    jwt_data: bytes
    request: Optional[RequestProtocol]
    response: Optional[ResponseProtocol]


@dataclass(frozen=True)
class OAuthLoginUserCommandHandler(CommandHandler[OAuthLoginUserCommand, TokenPair]):
    _user_reader: BaseUserReader
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager
    _uow: UnitOfWork

    async def handle(self, command: OAuthLoginUserCommand) -> TokenPair:
        session: domain.Session = await self._session_manager.get_or_create_session(
            user_id=command.user_id, request=command.request
        )
        await self._uow.commit()

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=command.jwt_data, device_id=session.device_id
        )

        token_pair: dto.TokenPair = self._jwt_manager.create_token_pair(
            security_user=security_user
        )

        self._jwt_manager.set_token_in_cookie(
            command.response, token_pair.refresh_token
        )

        return token_pair
