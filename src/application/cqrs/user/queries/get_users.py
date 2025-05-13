from dataclasses import dataclass

from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.domain import User
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.repositories.pagination import Pagination


@dataclass(frozen=True)
class GetUsers(BaseQuery):
    pagination: Pagination


@dataclass(frozen=True)
class GetUsersHandler(BaseQueryHandler[GetUsers, list[User]]):
    _user_reader: BaseUserReader

    async def handle(self, query: GetUsers) -> list[User]:
        return await self._user_reader.get_all_users(pagination=query.pagination)
