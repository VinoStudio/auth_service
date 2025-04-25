from dataclasses import dataclass

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import JWTUserInterface, BaseJWTManager
from src.application.base.session.session_manager import BaseSessionManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser
import src.domain as domain
import src.application.dto as dto
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetCurrentUserSession(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserSessionHandler(
    BaseQueryHandler[GetCurrentUserSession, domain.Session]
):
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager

    @authorization_required
    async def handle(
        self, query: GetCurrentUserSession, security_user: SecurityUser
    ) -> domain.Session:
        user_session = await self._session_manager.get_user_session(
            user_id=security_user.get_user_identifier(),
            device_id=security_user.get_device_id(),
        )

        return user_session
