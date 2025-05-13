from abc import ABC, abstractmethod
from dataclasses import (
    dataclass,
    field,
)

from src.application.base.queries.base import BaseQuery
from src.application.base.queries.query_handler import (
    QR,
    QT,
    BaseQueryHandler,
)


@dataclass(eq=False)
class BaseQueryMediator(ABC):
    query_map: dict[QT, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    @abstractmethod
    def register_query(
        self, query: type[BaseQuery], query_handler: BaseQueryHandler[QT, QR]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_query(self, query: QT) -> QR:
        raise NotImplementedError
