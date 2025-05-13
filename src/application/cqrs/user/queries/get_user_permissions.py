from dataclasses import dataclass

from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetUserPermissions(BaseQuery):
    user_id: str
    pagination: Pagination


@dataclass(frozen=True)
class GetUserPermissionsHandler(BaseQueryHandler[GetUserPermissions, set[str]]):
    _user_reader: BaseUserReader

    async def handle(self, query: GetUserPermissions) -> set[str]:
        return await self._user_reader.get_user_permissions_by_user_id(
            query.user_id, query.pagination
        )
