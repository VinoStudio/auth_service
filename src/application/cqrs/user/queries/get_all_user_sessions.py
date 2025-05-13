from dataclasses import dataclass

from src import domain
from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import BaseJWTManager
from src.application.base.session.session_manager import BaseSessionManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser


@dataclass(frozen=True)
class GetCurrentUserSessions(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserSessionsHandler(
    BaseQueryHandler[GetCurrentUserSessions, list[domain.Session]]
):
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager

    @authorization_required
    async def handle(
        self, _query: GetCurrentUserSessions, security_user: SecurityUser
    ) -> list[domain.Session]:
        user_sessions = await self._session_manager.get_user_active_sessions(
            user_id=security_user.get_user_identifier()
        )

        return user_sessions
