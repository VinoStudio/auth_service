from dataclasses import dataclass
from typing import List

from src.application.base.queries import BaseQuery, BaseQueryHandler
import src.domain as domain
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetAllPermissionsQuery(BaseQuery):
    pagination: Pagination


@dataclass(frozen=True)
class GetAllPermissionsHandler(
    BaseQueryHandler[GetAllPermissionsQuery, List[domain.Permission]]
):
    _permission_repo: BasePermissionRepository

    async def handle(self, query: GetAllPermissionsQuery) -> List[domain.Permission]:
        return await self._permission_repo.get_all_permissions(
            pagination=query.pagination
        )
