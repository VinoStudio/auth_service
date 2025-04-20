from dataclasses import dataclass
from typing import List

from src.application.base.queries import BaseQuery, BaseQueryHandler
import src.domain as domain
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetAllRolesQuery(BaseQuery):
    pagination: Pagination


@dataclass(frozen=True)
class GetAllRolesHandler(BaseQueryHandler[GetAllRolesQuery, List[domain.Role]]):
    _role_repo: BaseRoleRepository

    async def handle(self, query: GetAllRolesQuery) -> List[domain.Role]:
        return await self._role_repo.get_all_roles(pagination=query.pagination)
