from dataclasses import dataclass
from typing import List

from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository import BaseUserReader
import src.domain as domain
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetUserPermissions(BaseQuery):
    user_id: str
    pagination: Pagination


@dataclass(frozen=True)
class GetUserPermissionsHandler(BaseQueryHandler[GetUserPermissions, List[str]]):
    _user_reader: BaseUserReader

    async def handle(self, query: GetUserPermissions) -> List[str]:
        return await self._user_reader.get_user_permissions(
            query.user_id, query.pagination
        )
