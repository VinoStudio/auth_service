from dataclasses import dataclass

from src import domain
from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetCurrentUserConnectedAccounts(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserConnectedAccountsHandler(
    BaseQueryHandler[GetCurrentUserConnectedAccounts, list[domain.OAuthAccount]]
):
    _user_reader: BaseUserReader
    _jwt_manager: BaseJWTManager

    @authorization_required
    async def handle(
        self, _query: GetCurrentUserConnectedAccounts, security_user: SecurityUser
    ) -> list[domain.OAuthAccount]:
        return await self._user_reader.get_user_oauth_accounts(
            user_id=security_user.get_user_identifier()
        )
