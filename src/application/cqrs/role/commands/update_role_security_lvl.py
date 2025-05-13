from dataclasses import dataclass

import structlog

from src import domain
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.exceptions import AccessDeniedException
from src.application.services.rbac.rbac_manager import RBACManager
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.uow import UnitOfWork

logger = structlog.getLogger(__name__)


@dataclass(frozen=True)
class UpdateRoleSecurityLvlCommand(BaseCommand):
    role_name: str
    new_security_lvl: int
    request: RequestProtocol


@dataclass(frozen=True)
class UpdateRoleSecurityLvlCommandHandler(
    CommandHandler[UpdateRoleSecurityLvlCommand, domain.Role]
):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: UpdateRoleSecurityLvlCommand, security_user: SecurityUser
    ) -> domain.Role:
        can_modify_security_level = False

        for role in security_user.roles:
            if role in self._rbac_manager.system_roles:
                can_modify_security_level = True
                break

        if not can_modify_security_level:
            raise AccessDeniedException(
                "You have not enough permissions to modify security level"
            )

        logger.info("Security level change initiated by ", user_id=security_user.id)

        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        role.security_level = command.new_security_lvl

        updated_role = await self._rbac_manager.update_role(
            role=role, request_from=security_user
        )
        await self._uow.commit()

        await self._rbac_manager.invalidate_role(updated_role.name.to_raw())

        return updated_role
