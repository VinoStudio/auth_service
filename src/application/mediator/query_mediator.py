from dataclasses import dataclass, field

from src.application.base.mediator.query import BaseQueryMediator
from src.application.base.queries import BaseQueryHandler, QueryResult, QueryType
from src.application.exceptions import QueryIsNotRegisteredException


@dataclass(eq=False)
class QueryMediator(BaseQueryMediator):
    query_map: dict[QueryType, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: QueryType, query_handler: BaseQueryHandler) -> None:
        self.query_map[query] = query_handler

    async def handle_query(self, query: QueryType) -> QueryResult:
        if query.__class__ not in self.query_map:
            raise QueryIsNotRegisteredException(query)

        return await self.query_map[query.__class__].handle(query)
