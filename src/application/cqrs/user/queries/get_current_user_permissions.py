from dataclasses import dataclass
from typing import Any, List

from src.application.base.interface.request import RequestProtocol
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.security.security_user import SecurityUser

import src.application.dto as dto


@dataclass(frozen=True)
class GetCurrentUserPermissions(BaseQuery):
    request: RequestProtocol


@dataclass(frozen=True)
class GetCurrentUserPermissionsHandler(
    BaseQueryHandler[GetCurrentUserPermissions, List[str]]
):
    _jwt_manager: BaseJWTManager

    @authorization_required
    async def handle(
        self, query: GetCurrentUserPermissions, security_user: SecurityUser
    ) -> List[str]:
        return security_user.get_permissions()
