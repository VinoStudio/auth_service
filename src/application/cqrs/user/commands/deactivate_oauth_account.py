from dataclasses import dataclass

import structlog

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.oauth_manager import OAuthManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.uow import UnitOfWork

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class DeactivateUsersOAuthAccountCommand(BaseCommand):
    provider_name: str
    provider_user_id: str
    request: RequestProtocol


@dataclass(frozen=True)
class DeactivateUsersOAuthAccountCommandHandler(
    CommandHandler[DeactivateUsersOAuthAccountCommand, None]
):
    _oauth_manager: OAuthManager
    _jwt_manager: BaseJWTManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: DeactivateUsersOAuthAccountCommand, _security_user: SecurityUser
    ) -> None:
        await self._oauth_manager.disconnect_oauth_account(
            provider_name=command.provider_name,
            provider_user_id=command.provider_user_id,
        )

        await self._uow.commit()
