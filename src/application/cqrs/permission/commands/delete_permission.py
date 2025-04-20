from dataclasses import dataclass
from typing import List

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser
from src.domain.permission.values.permission_name import PermissionName

import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class DeletePermissionCommand(BaseCommand):
    name: str
    request: RequestProtocol


@dataclass(frozen=True)
class DeletePermissionCommandHandler(CommandHandler[DeletePermissionCommand, bool]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    async def handle(self, command: DeletePermissionCommand) -> bool:
        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data: dto.Token = await self._jwt_manager.validate_token(token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        permission_to_delete: domain.Permission = (
            await self._rbac_manager.get_permission(
                permission_name=command.name, request_from=security_user
            )
        )

        await self._rbac_manager.delete_permission(
            permission=permission_to_delete, request_from=security_user
        )

        await self._uow.commit()

        return True
