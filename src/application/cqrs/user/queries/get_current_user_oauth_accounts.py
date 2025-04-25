from dataclasses import dataclass
from typing import Any, List

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import JWTUserInterface, BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader
import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class GetCurrentUserConnectedAccounts(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserConnectedAccountsHandler(
    BaseQueryHandler[GetCurrentUserConnectedAccounts, List[str]]
):
    _user_reader: BaseUserReader
    _jwt_manager: BaseJWTManager

    @authorization_required
    async def handle(
        self, query: GetCurrentUserConnectedAccounts, security_user: SecurityUser
    ) -> List[str]:
        return await self._user_reader.get_user_oauth_accounts(
            user_id=security_user.get_user_identifier()
        )
