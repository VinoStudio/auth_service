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
class CreateRoleCommand(BaseCommand):
    name: str
    description: str
    security_level: int
    permissions: list[str]
    request: RequestProtocol


@dataclass(frozen=True)
class CreateRoleCommandHandler(CommandHandler[CreateRoleCommand, domain.Role]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: CreateRoleCommand, security_user: SecurityUser
    ) -> domain.Role:
        role = dto.RoleCreation(
            name=command.name,
            description=command.description,
            security_level=command.security_level,
            permissions=command.permissions,
        )

        created_role: domain.Role = await self._rbac_manager.create_role(
            role_dto=role, request_from=security_user
        )

        await self._uow.commit()

        return created_role
