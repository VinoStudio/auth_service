from dataclasses import dataclass

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser

import src.domain as domain
import src.application.dto as dto


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

    async def handle(self, command: CreatePermissionCommand) -> domain.Permission:
        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data: dto.Token = await self._jwt_manager.validate_token(token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        new_permission = dto.PermissionCreation(
            name=command.name,
        )

        created_permission = await self._rbac_manager.create_permission(
            permission_dto=new_permission, request_from=security_user
        )

        await self._uow.commit()

        return created_permission
