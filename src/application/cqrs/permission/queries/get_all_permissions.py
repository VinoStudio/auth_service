from dataclasses import dataclass

from src import domain
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetAllPermissionsQuery(BaseQuery):
    pagination: Pagination


@dataclass(frozen=True)
class GetAllPermissionsHandler(
    BaseQueryHandler[GetAllPermissionsQuery, list[domain.Permission]]
):
    _permission_repo: BasePermissionRepository

    async def handle(self, query: GetAllPermissionsQuery) -> list[domain.Permission]:
        return await self._permission_repo.get_all_permissions(
            pagination=query.pagination
        )
