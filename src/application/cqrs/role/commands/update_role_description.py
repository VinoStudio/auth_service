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
class UpdateRoleDescriptionCommand(BaseCommand):
    role_name: str
    new_description: str
    request: RequestProtocol


@dataclass(frozen=True)
class UpdateRoleDescriptionCommandHandler(
    CommandHandler[UpdateRoleDescriptionCommand, domain.Role]
):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: UpdateRoleDescriptionCommand, security_user: SecurityUser
    ) -> domain.Role:
        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        role.description = command.new_description

        updated_role = await self._rbac_manager.update_role(
            role=role, request_from=security_user
        )
        await self._uow.commit()

        return updated_role
