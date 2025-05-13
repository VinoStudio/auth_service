from dataclasses import dataclass

import structlog

from src import domain
from src.application import dto
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.base.session.session_manager import BaseSessionManager
from src.application.dto.token import TokenPair
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.uow import UnitOfWork

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class OAuthLoginUserCommand(BaseCommand):
    user_id: str
    jwt_data: bytes
    request: RequestProtocol | None
    response: ResponseProtocol | None


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
