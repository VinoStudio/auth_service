import secrets
from dataclasses import dataclass

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.oauth_manager import OAuthManager
from src.application.services.security.security_user import SecurityUser
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

    @authorization_required
    async def handle(
        self, command: AddOAuthAccountRequestCommand, security_user: SecurityUser
    ) -> str:
        state = secrets.token_urlsafe(32)

        await self._token_repo.add_reset_token(
            user_id=security_user.get_user_identifier(),
            token=state,
            token_type=TokenType.OAUTH_CONNECT,
        )

        # Get OAuth login URL
        return self._oauth_manager.get_oauth_url(
            command.provider, state, is_connect=True
        )
