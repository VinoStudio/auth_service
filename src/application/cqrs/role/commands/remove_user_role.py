from dataclasses import dataclass
from typing import List

from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.security import BaseJWTManager
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.repository import BaseUserWriter, BaseUserReader
from src.infrastructure.base.uow import UnitOfWork
from src.application.services.security.security_user import SecurityUser

import src.domain as domain
import src.application.dto as dto
from src.infrastructure.repositories import TokenBlackListRepository


@dataclass(frozen=True)
class RemoveRoleCommand(BaseCommand):
    remove_from_user: str
    role_name: str
    request: RequestProtocol


@dataclass(frozen=True)
class RemoveRoleCommandHandler(CommandHandler[RemoveRoleCommand, domain.User]):
    _jwt_manager: BaseJWTManager
    _rbac_manager: RBACManager
    _user_reader: BaseUserReader
    _user_writer: BaseUserWriter
    _blacklist_repo: TokenBlackListRepository
    _uow: UnitOfWork

    async def handle(self, command: RemoveRoleCommand) -> domain.User:
        token = self._jwt_manager.get_token_from_cookie(command.request)
        token_data: dto.Token = await self._jwt_manager.validate_token(token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        role: domain.Role = await self._rbac_manager.get_role(
            role_name=command.role_name, request_from=security_user
        )

        user = await self._user_reader.get_user_by_username(
            username=command.remove_from_user
        )

        updated_user: domain.User = await self._rbac_manager.remove_role_from_user(
            user=user,
            role=role,
            request_from=security_user,
        )

        await self._user_writer.update_user(user=updated_user)
        await self._uow.commit()

        await self._blacklist_repo.add_to_blacklist(
            user_id=updated_user.id.to_raw(),
        )

        return updated_user
