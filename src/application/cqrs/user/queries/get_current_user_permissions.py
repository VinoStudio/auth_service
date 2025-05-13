from dataclasses import dataclass

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser


@dataclass(frozen=True)
class GetCurrentUserPermissions(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserPermissionsHandler(
    BaseQueryHandler[GetCurrentUserPermissions, list[str]]
):
    _jwt_manager: BaseJWTManager

    @authorization_required
    async def handle(
        self, _query: GetCurrentUserPermissions, security_user: SecurityUser
    ) -> list[str]:
        return security_user.get_permissions()
