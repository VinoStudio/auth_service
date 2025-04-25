from dataclasses import dataclass
from typing import Any

from src.application.base.queries import BaseQuery, BaseQueryHandler
from src.infrastructure.base.repository import BaseUserReader
import src.domain as domain


@dataclass(frozen=True)
class GetUserById(BaseQuery):
    user_id: str


@dataclass(frozen=True)
class GetUserByIdHandler(BaseQueryHandler[GetUserById, Any]):
    _user_reader: BaseUserReader

    async def handle(self, query: GetUserById) -> domain.User:
        return await self._user_reader.get_active_user_by_id(user_id=query.user_id)
