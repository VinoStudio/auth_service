from dataclasses import dataclass

from src import domain
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetAllRolesQuery(BaseQuery):
    pagination: Pagination


@dataclass(frozen=True)
class GetAllRolesHandler(BaseQueryHandler[GetAllRolesQuery, list[domain.Role]]):
    _role_repo: BaseRoleRepository

    async def handle(self, query: GetAllRolesQuery) -> list[domain.Role]:
        return await self._role_repo.get_all_roles(pagination=query.pagination)
