from dataclasses import dataclass, field
from typing import Type

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
        self, query: Type[BaseQuery], query_handler: BaseQueryHandler[QT, QR]
    ) -> None:
        self.query_map[query] = query_handler

    async def handle_query(self, query: QT) -> QR:
        if query.__class__ not in self.query_map:
            raise QueryIsNotRegisteredException(query)

        return await self.query_map[query.__class__].handle(query)
