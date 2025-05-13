from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.application.base.queries.base import BaseQuery

QueryType = TypeVar("QueryType", bound=type(BaseQuery))
QueryResult = TypeVar("QueryResult", bound=Any)


@dataclass(frozen=True)
class BaseQueryHandler(ABC, Generic[QueryType, QueryResult]):
    async def handle(self, query: QueryType) -> QueryResult: ...
