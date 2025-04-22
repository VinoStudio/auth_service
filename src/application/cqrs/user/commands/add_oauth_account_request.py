import hashlib
import secrets
from dataclasses import dataclass
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.services.security.oauth_manager import OAuthManager
from src.application.services.tasks.notification_manager import (
    NotificationManager,
    NotificationType,
)
from src.infrastructure.base.repository import BaseUserReader

import src.application.dto as dto
from src.infrastructure.repositories import TokenBlackListRepository, TokenType


@dataclass(frozen=True)
class AddOAuthAccountRequestCommand(BaseCommand):
    provider: str
    request: RequestProtocol


@dataclass(frozen=True)
class AddOAuthAccountRequestCommandHandler(
    CommandHandler[AddOAuthAccountRequestCommand, str]
):
    _token_repo: TokenBlackListRepository
    _oauth_manager: OAuthManager
    _jwt_manager: BaseJWTManager

    async def handle(self, command: AddOAuthAccountRequestCommand) -> str:

        state = secrets.token_urlsafe(32)

        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data = await self._jwt_manager.validate_token(token)
        user_id = token_data.sub

        await self._token_repo.add_reset_token(user_id, state, TokenType.OAUTH_CONNECT)

        # Get OAuth login URL
        return self._oauth_manager.get_oauth_url(
            command.provider, state, is_connect=True
        )
