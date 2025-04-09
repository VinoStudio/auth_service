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
class CreateRoleCommand(BaseCommand):
    name: str
    description: str
    security_level: int
    permissions: List[str]
    request: RequestProtocol


@dataclass(frozen=True)
class CreateRoleCommandHandler(CommandHandler[CreateRoleCommand, domain.Role]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    async def handle(self, command: CreateRoleCommand) -> domain.Role:
        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data: dto.Token = await self._jwt_manager.validate_token(token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        role = dto.RoleCreation(
            name=command.name,
            description=command.description,
            security_level=command.security_level,
            permissions=command.permissions,
        )

        created_role: domain.Role = await self._rbac_manager.create_role(
            role_dto=role, request_from=security_user
        )

        return created_role
