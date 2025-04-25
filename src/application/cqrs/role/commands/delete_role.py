from dataclasses import dataclass
from typing import List

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser

import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class DeleteRoleCommand(BaseCommand):
    role_name: str
    request: RequestProtocol


@dataclass(frozen=True)
class DeleteRoleCommandHandler(CommandHandler[DeleteRoleCommand, bool]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: DeleteRoleCommand, security_user: SecurityUser
    ) -> bool:
        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        await self._rbac_manager.delete_role(role=role, request_from=security_user)

        await self._uow.commit()

        return True
