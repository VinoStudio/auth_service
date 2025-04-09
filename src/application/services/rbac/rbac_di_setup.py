from dishka import Scope, provide, Provider
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository


class RBACProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_rbac_manager(
        self,
        role_repo: BaseRoleRepository,
        permission_repo: BasePermissionRepository,
    ) -> RBACManager:
        return RBACManager(
            role_repository=role_repo, permission_repository=permission_repo
        )
