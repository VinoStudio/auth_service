from dataclasses import dataclass, field

from src.application.base.mediator.query import BaseQueryMediator
from src.application.base.queries import BaseQueryHandler, QT, QR, BaseQuery
from src.application.exceptions import QueryIsNotRegisteredException


@dataclass(eq=False)
class QueryMediator(BaseQueryMediator):

    query_map: dict[QT, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(
        self, query: BaseQuery, query_handler: BaseQueryHandler[QT, QR]
    ) -> None:
        self.query_map[query] = query_handler

    async def handle_query(self, query: QT) -> QR:
        if query not in self.query_map:
            raise QueryIsNotRegisteredException(query)

        return await self.query_map[query].handle(query)
