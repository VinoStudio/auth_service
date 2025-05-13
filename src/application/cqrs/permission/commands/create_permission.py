from dataclasses import dataclass

from src import domain
from src.application import dto
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.rbac.rbac_manager import RBACManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.uow import UnitOfWork


@dataclass(frozen=True)
class CreatePermissionCommand(BaseCommand):
    name: str
    request: RequestProtocol


@dataclass(frozen=True)
class CreatePermissionCommandHandler(
    CommandHandler[CreatePermissionCommand, domain.Permission]
):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: CreatePermissionCommand, security_user: SecurityUser
    ) -> domain.Permission:
        new_permission = dto.PermissionCreation(
            name=command.name,
        )

        created_permission = await self._rbac_manager.create_permission(
            permission_dto=new_permission, request_from=security_user
        )

        await self._uow.commit()

        return created_permission
