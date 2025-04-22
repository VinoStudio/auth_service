from dataclasses import dataclass

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import JWTUserInterface, BaseJWTManager
from src.application.services.security.security_user import SecurityUser
import src.domain as domain
import src.application.dto as dto
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetCurrentUser(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserHandler(BaseQueryHandler[GetCurrentUser, domain.User]):
    _jwt_manager: BaseJWTManager
    _user_reader: BaseUserReader

    async def handle(self, query: GetCurrentUser) -> domain.User:

        refresh_token: str = self._jwt_manager.get_token_from_cookie(query.request)

        token_data: dto.Token = await self._jwt_manager.validate_token(refresh_token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        current_user = await self._user_reader.get_user_by_id(
            user_id=security_user.get_user_identifier()
        )

        return current_user
