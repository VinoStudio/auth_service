from dataclasses import dataclass
from typing import Any

from src import domain
from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository import BaseUserReader


@dataclass(frozen=True)
class GetUserByUsername(BaseQuery):
    username: str


@dataclass(frozen=True)
class GetUserByUsernameHandler(BaseQueryHandler[GetUserByUsername, Any]):
    _user_reader: BaseUserReader

    async def handle(self, query: GetUserByUsername) -> domain.User:
        return await self._user_reader.get_user_by_username(query.username)
