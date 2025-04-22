from dataclasses import dataclass
from typing import List

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import JWTUserInterface, BaseJWTManager
from src.application.base.session.session_manager import BaseSessionManager
from src.application.services.security.security_user import SecurityUser
import src.domain as domain
import src.application.dto as dto
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetCurrentUserSessions(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserSessionsHandler(
    BaseQueryHandler[GetCurrentUserSessions, List[domain.Session]]
):
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager

    async def handle(self, query: GetCurrentUserSessions) -> List[domain.Session]:

        refresh_token: str = self._jwt_manager.get_token_from_cookie(query.request)

        token_data: dto.Token = await self._jwt_manager.validate_token(refresh_token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        user_sessions = await self._session_manager.get_user_active_sessions(
            user_id=security_user.get_user_identifier()
        )

        return user_sessions
