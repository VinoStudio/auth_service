from dataclasses import dataclass
from typing import Any

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import JWTUserInterface, BaseJWTManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader
import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class GetCurrentUserPermissions(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserPermissionsHandler(
    BaseQueryHandler[GetCurrentUserPermissions, JWTUserInterface]
):
    _jwt_manager: BaseJWTManager

    async def handle(self, query: GetCurrentUserPermissions) -> JWTUserInterface:

        refresh_token: str = await self._jwt_manager.get_token_from_cookie(
            query.request
        )

        token_data: dto.Token = await self._jwt_manager.validate_token(refresh_token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        return security_user
