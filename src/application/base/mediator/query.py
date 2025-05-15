from abc import ABC, abstractmethod
from dataclasses import (
    dataclass,
    field,
)

from src.application.base.queries.base import BaseQuery
from src.application.base.queries.query_handler import (
    QueryType,
    QueryResult,
    BaseQueryHandler,
)


@dataclass(eq=False)
class BaseQueryMediator(ABC):
    query_map: dict[QueryType, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    @abstractmethod
    def register_query(
        self,
        query: type[BaseQuery],
        query_handler: BaseQueryHandler[QueryType, QueryResult],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_query(self, query: QueryType) -> QueryResult:
        raise NotImplementedError
