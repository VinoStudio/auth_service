from dataclasses import dataclass

from src import domain
from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetCurrentUser(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserHandler(BaseQueryHandler[GetCurrentUser, domain.User]):
    _jwt_manager: BaseJWTManager
    _user_reader: BaseUserReader

    @authorization_required
    async def handle(
        self, _query: GetCurrentUser, security_user: SecurityUser
    ) -> domain.User:
        current_user = await self._user_reader.get_user_by_id(
            user_id=security_user.get_user_identifier()
        )

        return current_user
