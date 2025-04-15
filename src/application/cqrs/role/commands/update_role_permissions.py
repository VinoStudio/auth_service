from dataclasses import dataclass
from typing import List

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser

import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class UpdateRolePermissionsCommand(BaseCommand):
    role_name: str
    new_permissions: List[str]
    request: RequestProtocol


@dataclass(frozen=True)
class UpdateRolePermissionsCommandHandler(
    CommandHandler[UpdateRolePermissionsCommand, domain.Role]
):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    async def handle(self, command: UpdateRolePermissionsCommand) -> domain.Role:
        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data: dto.Token = await self._jwt_manager.validate_token(token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        for permission_name in command.new_permissions:
            db_permission = await self._rbac_manager.get_permission(
                permission_name=permission_name, request_from=security_user
            )
            role.add_permission(db_permission)

        updated_role = await self._rbac_manager.update_role(
            role=role, request_from=security_user
        )
        await self._uow.commit()

        # store timestamp with role_name as key into redis for token revocation if user have old role version
        await self._rbac_manager.invalidate_role(updated_role.name.to_raw())

        return updated_role
