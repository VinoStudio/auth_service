from dataclasses import dataclass

from src import domain
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.rbac.rbac_manager import RBACManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.uow import UnitOfWork


@dataclass(frozen=True)
class UpdateRolePermissionsCommand(BaseCommand):
    role_name: str
    new_permissions: list[str]
    request: RequestProtocol


@dataclass(frozen=True)
class UpdateRolePermissionsCommandHandler(
    CommandHandler[UpdateRolePermissionsCommand, domain.Role]
):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: UpdateRolePermissionsCommand, security_user: SecurityUser
    ) -> domain.Role:
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
