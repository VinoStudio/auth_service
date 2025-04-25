from dataclasses import dataclass
from typing import List

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.cqrs.helpers import authorization_required
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.repository import BaseUserWriter, BaseUserReader
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser

import src.domain as domain
import src.application.dto as dto
from src.infrastructure.repositories import TokenBlackListRepository


@dataclass(frozen=True)
class AssignRoleCommand(BaseCommand):
    assign_to_user: str
    role_name: str
    request: RequestProtocol


@dataclass(frozen=True)
class AssignRoleCommandHandler(CommandHandler[AssignRoleCommand, domain.User]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _user_reader: BaseUserReader
    _blacklist_repo: TokenBlackListRepository
    _uow: UnitOfWork

    @authorization_required
    async def handle(
        self, command: AssignRoleCommand, security_user: SecurityUser
    ) -> domain.User:
        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        user = await self._user_reader.get_user_by_username(
            username=command.assign_to_user
        )

        updated_user: domain.User = await self._rbac_manager.assign_role_to_user(
            user=user,
            role=role,
            request_from=security_user,
        )

        await self._uow.commit()

        await self._blacklist_repo.add_to_blacklist(
            user_id=updated_user.id.to_raw(),
        )

        return updated_user
