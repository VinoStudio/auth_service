from dishka import Provider, Scope, provide

from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)


class RBACProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_rbac_manager(
        self,
        role_repo: BaseRoleRepository,
        user_writer: BaseUserWriter,
        permission_repo: BasePermissionRepository,
        role_invalidation: RoleInvalidationRepository,
    ) -> RBACManager:
        return RBACManager(
            role_repository=role_repo,
            user_writer=user_writer,
            permission_repository=permission_repo,
            role_invalidation=role_invalidation,
        )
