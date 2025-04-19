from dataclasses import dataclass
from typing import Optional

from src.application.base.session.session_manager import BaseSessionManager
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.dto.token import TokenPair
from src.application.base.commands import BaseCommand, CommandHandler, CT, CR
from src.application.services.security.oauth_manager import OAuthManager

from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.uow import UnitOfWork


import src.domain as domain
import src.application.dto as dto
import structlog

from src.infrastructure.repositories import TokenBlackListRepository, TokenType

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class AddOAuthAccountToCurrentUserCommand(BaseCommand):
    code: str
    state: str
    provider: str


@dataclass(frozen=True)
class AddOAuthAccountToCurrentUserCommandHandler(
    CommandHandler[AddOAuthAccountToCurrentUserCommand, None]
):
    _user_reader: BaseUserReader
    _oauth_manager: OAuthManager
    _token_repo: TokenBlackListRepository
    _session_manager: BaseSessionManager
    _uow: UnitOfWork

    async def handle(self, command: AddOAuthAccountToCurrentUserCommand) -> None:
        user_id = await self._token_repo.get_reset_token(
            command.state, TokenType.OAUTH_CONNECT
        )

        logger.info("User id", user_id=user_id)

        await self._oauth_manager.associate_oauth_with_existing_user(
            user_id=user_id,
            code=command.code,
            provider_name=command.provider,
            state=command.state,
        )

        await self._uow.commit()

        await self._token_repo.invalidate_reset_token(
            command.state, TokenType.OAUTH_CONNECT
        )
