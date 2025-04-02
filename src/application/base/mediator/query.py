from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable

from application.base.queries.base import BaseQuery
from application.base.queries.query_handler import (
    BaseQueryHandler,
    QT,
    QR,
)


@dataclass(eq=False)
class QueryMediator(ABC):
    query_map: dict[QT, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    @abstractmethod
    def register_query(
        self, query: BaseQuery, query_handler: BaseQueryHandler[QT, QR]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_query(self, query: QT) -> QR:
        raise NotImplementedError
