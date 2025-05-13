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
class DeletePermissionCommand(BaseCommand):
    name: str
    request: RequestProtocol


@dataclass(frozen=True)
class DeletePermissionCommandHandler(CommandHandler[DeletePermissionCommand, bool]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: DeletePermissionCommand, security_user: SecurityUser
    ) -> bool:
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
